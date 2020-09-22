#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Demonstrate NETCONF on IOS-XE and IOS-XR coupled
with Nornir to update VRF route-target configurations.
"""

from nornir import InitNornir
import json
import xmltodict
from ncclient import manager
from lxml.etree import fromstring


def main():
    """
    Execution begins here.
    """

    # Initialize Nornir and run the manage_config custom task
    nornir = InitNornir()

    entry_list = []
    schedule_list = []
    for host, v in nornir.inventory.hosts.items():
        print(f"Building SLA entry for {host}")
        entry = build_sla_entry(v)
        entry_list.append(entry)

        schedule = build_sla_schedule(v)
        schedule_list.append(schedule)

    print(entry_list)
    print(schedule_list)

    wrapper = {
        "config": {
            "native": {
                "@xmlns": "http://cisco.com/ns/yang/Cisco-IOS-XE-native",
                "ip": {
                    "sla": {
                        "@xmlns": "http://cisco.com/ns/yang/Cisco-IOS-XE-sla",
                        "@operation": "replace",
                        "responder": None,
                        "entry": entry_list,
                        "schedule": schedule_list
                    }
                }
            }
        }
    }
    #print(json.dumps(wrapper, indent=2))
    xml_config = xmltodict.unparse(wrapper, pretty=True)
    #print(xml_config)


    connect_params = {
        "host": "172.31.43.55",
        "username": "admin",
        "password": "admin",
        "hostkey_verify": False,
        "allow_agent": False,
        "look_for_keys": False,
        #"device_params": {"name": "csr"}
        #"device_params": {"name": "iosxr"}
    }

    # Use the dict above as "keyword arguments" to open netconf session
    with manager.connect(**connect_params) as conn:

        # Gather the current XML configuration and pretty-print it
        #print(f"{hostname}: Connection open")

        config_resp = conn.edit_config(
            target="candidate",
            config=xml_config,
            #default_operation="replace",
        )
        
        # Perform validation everywhere to gain network-wide
        # atomicity as best as we can
        validate = conn.validate()

        # Copy from candidate to running config
        commit = conn.commit()

        # Copy from running to startup config
        save_config_ios(conn)


def build_sla_entry(v):
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
            "tos": v["tos"],
            "verify-data": "true"
        }
    }

def build_sla_schedule(v):
    return {
        "entry-number": v["node_id"],
        "life": "forever",
        "start-time": {
            "now-config": None,
            "now": None
        }
    }


def save_config_ios(conn):
    """
    Save config on Cisco XE is complex due to presence of startup-config.
    Need to use custom RPC string formed into XML document to save.
    """
    save_rpc = '<save-config xmlns="http://cisco.com/yang/cisco-ia"/>'
    save_resp = conn.dispatch(fromstring(save_rpc))

    # Return the RPC response
    return save_resp


if __name__ == "__main__":
    main()
