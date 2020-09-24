#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Demonstrate NETCONF on IOS-XE and IOS-XR coupled
with Nornir to update VRF route-target configurations.
"""

from nornir import InitNornir
from ncclient.operations.rpc import RPCError
import xmltodict
import json


def get_config(task, nc_filter=None):
    conn = task.host.get_connection("netconf", task.nornir.config)
    print(f"{task.host.name}: Connection established")

    # Collect the required configuration
    print(f"{task.host.name}: Collecting configuration")
    try:
        get_resp = conn.get_config(source="running", filter=nc_filter)
    except RPCError as rpc_error:
        print(rpc_error.xml)
        raise

    print(json.dumps(xmltodict.parse(get_resp.xml), indent=2))


def main():
    """
    Execution begins here.
    """

    # Initialize Nornir and process CLI arguments
    nornir = InitNornir()

    sla_filter = (
        "subtree",
        """
        <native>
          <ip>
            <sla xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-sla"/>
          </ip>
        </native>
    """,
    )

    mdt_filter = (
        "subtree",
        """
        <mdt-config-data xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-mdt-cfg">
          <mdt-subscription/>
        </mdt-config-data>
    """,
    )

    # Run the get_probes Nornir task
    sla = nornir.run(task=get_config, nc_filter=sla_filter)
    mdt = nornir.run(task=get_config, nc_filter=mdt_filter)


if __name__ == "__main__":
    main()
