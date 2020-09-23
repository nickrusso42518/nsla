#!/usr/bin/env python

def entry(attr, tag="NA"):
    sla = attr["sla"]
    return {
        "number": attr["node_id"],
        "udp-jitter": {
            "dest-addr": attr["ipsla_addr"],
            "portno": sla["destination_port"],
            "num-packets": sla["packet_count"],
            "interval": sla["packet_interval_ms"],
            #"source-ip": None, TODO
            "frequency": sla["frequency_s"],
            "timeout": sla["timeout_ms"],
            "threshold": sla["timeout_ms"],
            "tos": sla["tos"],
            "verify-data": "true",
            "tag": tag
        }
    }

def schedule(attr):
    return {
        "entry-number": attr["node_id"],
        "life": "forever",
        "start-time": {
            "now-config": None,
            "now": None
        }
    }


def wrapper(operation, **kwargs):
    sla = {
        "@xmlns": "http://cisco.com/ns/yang/Cisco-IOS-XE-sla",
        "@operation":operation,
    }
    sla.update(kwargs)

    wrapper = {
        "config": {
            "native": {
                "@xmlns": "http://cisco.com/ns/yang/Cisco-IOS-XE-native",
                "ip": {
                    "sla": sla
                }
            }
        }
    }

    return wrapper
