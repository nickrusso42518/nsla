#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Manage IP SLA probes and MDT subscriptions.
"""

import argparse
from nornir import InitNornir
from ncclient.operations.rpc import RPCError
from lxml.etree import fromstring  # pylint: disable=no-name-in-module
import xmltodict
from nsla import build_sla, build_mdt
from nsla.processors import ProcGrafanaDashboard


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
    print("Constructed common SLA config")

    # The MDT config is simpler and more static. Build that next
    mdt_inputs = nornir.inventory.groups["devices"].data["mdt"]
    replace_mdt = build_mdt.subscription(mdt_inputs)
    print("Constructed common MDT config")

    # Manage the IP SLA probes on each device using the common
    # merge_sla and replace_mdt dictionaries
    nornir.run(
        task=manage_probes,
        merge_sla=merge_sla,
        replace_mdt=replace_mdt,
        rebuild=args.rebuild,
    )


def process_args():
    """
    Process CLI arguments and return them for use in the script.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-r",
        "--rebuild",
        help="delete and freshly re-add SLA config",
        action="store_true",
    )
    return parser.parse_args()


def send_edit_config_rpc(conn, rpc_dict):
    """
    Helper function to send an edit_config RPC followed by
    validation and commit. Unfortunately, some IP SLA features
    require this relatively complex process and sending multiple
    edit_config RPCs with a single validate/commit does not
    always work.
    """

    # Convert Python dict to XML text
    xml_config = xmltodict.unparse(rpc_dict, pretty=True)
    conn.edit_config(
        target="candidate",
        config=xml_config,
    )

    # Copy from candidate to running config
    try:
        conn.validate(source="candidate")
        return conn.commit()
    except RPCError as rpc_error:
        # Failure occurred; discard the change, print the error, and
        # raise the error again to crash the program with stack trace
        conn.discard_changes()
        print(rpc_error.xml)
        raise


def manage_probes(task, merge_sla, replace_mdt, rebuild=False):
    """
    Nornir grouped task to manage SLA operations and MDT subscriptions.
    When rebuild is True, this deletes the existing IP SLA probes,
    then recreates and restarts them. This is the only way to modify
    an already-existing IP SLA probe.
    """

    # Establish NETCONF connection
    conn = task.host.get_connection("netconf", task.nornir.config)
    print(f"{task.host.name}: Connection established")

    # Obtain a lock on the candidate datastore to prevent other
    # NETCONF users from making concurrent changes
    print(f"{task.host.name}: Locking candidate-config")
    with conn.locked(target="candidate"):

        # If we need to rebuild the whole SLA process,
        # perform a bulk delete first
        if rebuild:
            print(f"{task.host.name}: Deleting probes")
            delete_sla = build_sla.wrapper(operation="delete")
            send_edit_config_rpc(conn, delete_sla)

        # Perform the merge operation to add the probes
        print(f"{task.host.name}: Configuring probes")
        send_edit_config_rpc(conn, merge_sla)

        # Perform the replace operation to update MDT subscriptions
        print(f"{task.host.name}: Configuring subscriptions")
        send_edit_config_rpc(conn, replace_mdt)

    # Copy from running to startup config
    print(f"{task.host.name}: Saving startup-config")
    save_rpc = '<save-config xmlns="http://cisco.com/yang/cisco-ia"/>'
    conn.dispatch(fromstring(save_rpc))


if __name__ == "__main__":
    main()
