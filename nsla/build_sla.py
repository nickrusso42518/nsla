#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Define helper functions related to NETCONF payloads
for IP Service Level Agreement (SLA) operations.
"""


def entry(attr, tag="NA"):
    """
    Create an IP SLA entry (an operation) based on specific
    node/operation attributes.
    """

    sla = attr["sla"]
    return {
        "number": attr["node_id"],
        "udp-jitter": {
            "dest-addr": attr["ipsla_addr"],
            "portno": sla["destination_port"],
            "num-packets": sla["packet_count"],
            "interval": sla["packet_interval_ms"],
            "frequency": sla["frequency_s"],
            "timeout": sla["timeout_ms"],
            "threshold": sla["timeout_ms"],
            "tos": sla["tos"],
            "verify-data": "true",
            "tag": tag,
            # "source-ip": None TODO
        },
    }


def schedule(attr):
    """
    Build an IP SLA schedule based on a specific node ID.
    """
    return {
        "entry-number": attr["node_id"],
        "life": "forever",
        "start-time": {"now-config": None, "now": None},
    }


def wrapper(operation, **kwargs):
    """
    Encapsulate keyword arguments that make up an IP SLA probe
    (such as entry and schedule) into a complete NETCONF edit_config RPC.
    """

    # Build the inner structure and specify the NETCONF operation
    sla_inner = {
        "@xmlns": "http://cisco.com/ns/yang/Cisco-IOS-XE-sla",
        "@operation": operation,
    }

    # Merge the kwargs into the dictionary just defined
    sla_inner.update(kwargs)

    # Build the outer structure around the IP SLA operation
    sla_outer = {
        "config": {
            "native": {
                "@xmlns": "http://cisco.com/ns/yang/Cisco-IOS-XE-native",
                "ip": {"sla": sla_inner},
            }
        }
    }

    # Return the full RPC structure
    return sla_outer
