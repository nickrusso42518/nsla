#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Collect the current IP SLA configuration from
IOS-XE and IOS-XR routers.
"""

from ncclient import manager
from lxml.etree import tostring
import xmltodict
import json


def main():
    """
    Execution starts here.
    """

    # Iterate over the list of hosts (string) defined below.
    # Refreshing the simple "in-line" inventory concept.
    f = ("subtree", '<ip-sla-stats xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ip-sla-oper"></ip-sla-stats>')

    #csr 172.31.43.55
    #xr 172.31.95.140
    for hostname in ["172.31.43.55"]:
        # Open a new NETCONF connection to each host using kwargs technique
        connect_params = {
            "host": hostname,
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
            print(f"{hostname}: Connection open")
            get_resp = conn.get(filter=f)
            if get_resp.ok:
                # RPC worked; print the config with header/trailer
                #print(f"{hostname}: VRF configuration start")
                xml_config = tostring(get_resp.data_ele, pretty_print=True)
                x=xml_config.decode().strip() 
                print(x)
                print(json.dumps(xmltodict.parse(x), indent=2))
                #print(f"{hostname}: VRF configuration end")
            else:
                # RPC failed; print list of errors as a comma-separated list
                print(f"{hostname}: Errors: {','.join(get_resp.errors)}")


if __name__ == "__main__":
    main()
