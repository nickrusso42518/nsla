#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Collect the current IP SLA configuration from
IOS-XE and IOS-XR routers.
"""

from nornir import InitNornir
from ncclient import manager
from lxml.etree import tostring
import xmltodict
import json


def collect_sla_stats(task, sla_filter):
    conn = task.host.get_connection("netconf", task.nornir.config)
    print(f"{task.host.name}: Connection open")

    get_resp = conn.get(filter=("subtree", sla_filter))
    if get_resp.ok:
        # RPC worked; print the config with header/trailer
        xml_config = tostring(get_resp.data_ele, pretty_print=True)
        xml_data =xml_config.decode().strip() 
        #print(xml_data)
        data = xmltodict.parse(xml_data)
        #print(data)

        with open(f"{task.host.name}_sla_stats.json", "w") as handle:
            json.dump(data, handle, indent=2)
    else:
        # RPC failed; print list of errors as a comma-separated list
        print(f"{hostname}: Errors: {','.join(get_resp.errors)}")

def main():
    """
    Execution starts here.
    """

    # Initialize Nornir and run the manage_config custom task
    nornir = InitNornir()

    # Iterate over the list of hosts (string) defined below.
    # Refreshing the simple "in-line" inventory concept.
    sla_xmlns = "http://cisco.com/ns/yang/Cisco-IOS-XE-ip-sla-oper"
    sla_filter = f'<ip-sla-stats xmlns="{sla_xmlns}"></ip-sla-stats>'

    result = nornir.run(task=collect_sla_stats, sla_filter=sla_filter)
    breakpoint()
    print(result)
    


if __name__ == "__main__":
    main()
