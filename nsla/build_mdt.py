#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Define helper functions related to NETCONF payloads
for model driven telemetry (MDT).
"""


def subscription(mdt):
    """
    Build an MDT subscript payload for the SLA operations data.
    """

    # Define xpath for the data required
    xpath = "/ip-sla-ios-xe-oper:ip-sla-stats/sla-oper-entry"

    # Assemble the complete RPC body using a replace operation to ensure
    # idempotent behavior of the subscriptions
    return {
        "config": {
            "mdt-config-data": {
                "@xmlns": "http://cisco.com/ns/yang/Cisco-IOS-XE-mdt-cfg",
                "@operation": "replace",
                "mdt-subscription": {
                    "subscription-id": mdt["sub_id"],
                    "base": {
                        "stream": "yang-push",
                        "encoding": "encode-kvgpb",
                        "period": mdt["interval_s"] * 100,
                        "xpath": xpath,
                    },
                    "mdt-receivers": {
                        "address": mdt["collector_ip_addr"],
                        "port": mdt["collector_grpc_port"],
                        "protocol": "grpc-tcp",
                    },
                },
            }
        }
    }
