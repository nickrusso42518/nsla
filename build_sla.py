#!/usr/bin/env python

def entry(v, tag="NA"):
    return {
        "number": v["node_id"],
        "udp-jitter": {
            "dest-addr": v["ipsla_addr"],
            "portno": v["destination_port"],
            "num-packets": v["packet_count"],
            "interval": v["packet_interval_ms"],
            #"source-ip": None, TODO
            "frequency": v["frequency_s"],
            "timeout": v["timeout_ms"],
            "threshold": v["timeout_ms"],
            "tos": v["tos"],
            "verify-data": "true",
            "tag": tag
        }
    }

def schedule(v):
    return {
        "entry-number": v["node_id"],
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
