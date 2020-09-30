#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Demonstrate NETCONF on IOS-XE and IOS-XR coupled
with Nornir to update VRF route-target configurations.
"""

import argparse
from nornir import InitNornir
from ncclient.operations.rpc import RPCError
from lxml.etree import fromstring
import xmltodict
from nsla import build_sla, build_mdt
from nsla.processors import ProcGrafanaDashboard


def send_edit_config_rpc(conn, rpc_dict):
    xml_config = xmltodict.unparse(rpc_dict, pretty=True)
    config_resp = conn.edit_config(
        target="candidate",
        config=xml_config,
    )

    # Copy from candidate to running config
    try:
        conn.validate(source="candidate")
        return conn.commit()
    except RPCError as rpc_error:
        conn.discard_changes()
        print(rpc_error.xml)
        raise


def manage_probes(task, merge_sla, replace_mdt, rebuild=True):
    conn = task.host.get_connection("netconf", task.nornir.config)
    print(f"{task.host.name}: Connection established")

    print(f"{task.host.name}: Locking candidate-config")
    with conn.locked(target="candidate"):

        # If we need to rebuild the whole SLA process,
        # perform a bulk delete first
        if rebuild:
            print(f"{task.host.name}: Deleting probes")
            delete_sla = build_sla.wrapper(operation="delete")
            resp = send_edit_config_rpc(conn, delete_sla)

        # Perform the merge operation to add the probes
        print(f"{task.host.name}: Configuring probes")
        resp = send_edit_config_rpc(conn, merge_sla)

        # Perform the replace operation to update MDT subscriptions
        print(f"{task.host.name}: Configuring subscriptions")
        resp = send_edit_config_rpc(conn, replace_mdt)


    # Perform a final validation on the entire running config
    print(f"{task.host.name}: Validating running-config")
    conn.validate(source="running")

    # Copy from running to startup config
    print(f"{task.host.name}: Saving startup-config")
    save_rpc = '<save-config xmlns="http://cisco.com/yang/cisco-ia"/>'
    conn.dispatch(fromstring(save_rpc))


def main():
    """
    Execution begins here.
    """

    # Initialize Nornir, process CLI args, and extract the collector IP address
    nornir = InitNornir()
    args = process_args()
    mdt_rx = nornir.inventory.groups["devices"]["mdt"]["collector_ip_addr"]

    # Register the Grafana processor to create dashboards if receiver exists
    if mdt_rx:
        nornir = nornir.with_processors([ProcGrafanaDashboard(mdt_rx)])

    # Initialize empty lists and iterate over entire inventory
    entry_list = []
    schedule_list = []
    for host, attr in nornir.inventory.hosts.items():
        print(f"Building SLA entry for {host}")

        # Build the SLA entry list
        entry = build_sla.entry(attr, tag=host)
        entry_list.append(entry)

        # Build the SLA schedule list
        schedule = build_sla.schedule(attr)
        schedule_list.append(schedule)

    # Create an RPC payload which includes the entry list,
    # schedule list, and SLA responder enablement
    merge_sla = build_sla.wrapper(
        operation="merge",
        entry=entry_list,
        schedule=schedule_list,
        responder=None,
    )
    print(f"Constructed common SLA config")

    mdt_inputs = nornir.inventory.groups["devices"].data["mdt"]
    replace_mdt = build_mdt.subscription(mdt_inputs)
    print(f"Constructed common MDT config")

    # Manage the IP SLA probes on each device using the common
    # merge_sla dictionary
    result = nornir.run(
        task=manage_probes,
        merge_sla=merge_sla,
        replace_mdt=replace_mdt,
        rebuild=args.rebuild,
    )


def process_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-r",
        "--rebuild",
        help="delete and freshly re-add SLA config",
        action="store_true",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
