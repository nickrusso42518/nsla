#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Demonstrate NETCONF on IOS-XE and IOS-XR coupled
with Nornir to update VRF route-target configurations.
"""

import json
from nornir import InitNornir
from ncclient.operations.rpc import RPCError
import xmltodict


def get_config(task, nc_filter=None):
    """
    Issues a NETCONF get_config RPC with a given filter.
    """

    # Establish NETCONF connection
    conn = task.host.get_connection("netconf", task.nornir.config)
    print(f"{task.host.name}: Connection established")

    # Collect the required configuration
    print(f"{task.host.name}: Collecting configuration")
    try:
        get_resp = conn.get_config(source="running", filter=nc_filter)
    except RPCError as rpc_error:
        print(rpc_error.xml)
        raise

    # Quick and dirty verification, TODO use processor later
    print(json.dumps(xmltodict.parse(get_resp.xml), indent=2))


def main():
    """
    Execution begins here.
    """

    # Initialize Nornir
    nornir = InitNornir()

    # Define filter for collecting IP SLA configuration
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

    # Define filter for collecting MDT subscriptions
    mdt_filter = (
        "subtree",
        """
        <mdt-config-data xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-mdt-cfg">
          <mdt-subscription/>
        </mdt-config-data>
    """,
    )

    # Run the get_config Nornir task with each filter
    nornir.run(task=get_config, nc_filter=sla_filter)
    nornir.run(task=get_config, nc_filter=mdt_filter)


if __name__ == "__main__":
    main()
