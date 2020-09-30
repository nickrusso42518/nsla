#!/usr/bin/env python

def subscription(mdt):

    xpath = "/ip-sla-ios-xe-oper:ip-sla-stats/sla-oper-entry"

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
