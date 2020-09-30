#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Collect the current IP SLA operational data.
"""

from nornir import InitNornir
from nornir.core.task import Result
from lxml.etree import tostring  # pylint: disable=no-name-in-module
import xmltodict
from nsla.processors import ProcJSON, ProcCSV


def collect_sla_stats(task, sla_filter):
    """
    Issues NETCONF get RPC to collect SLA operational statistics
    with supplier filter.
    """

    # Establish NETCONF connection
    conn = task.host.get_connection("netconf", task.nornir.config)
    print(f"{task.host.name}: Connection open")

    # Issue NETCONF get RPC to collect SLA operational details
    get_resp = conn.get(filter=sla_filter)

    # If RPC worked, print the config with header/trailer
    if get_resp.ok:
        xml_config = tostring(get_resp.data_ele, pretty_print=True)
        xml_data = xml_config.decode().strip()
        result = xmltodict.parse(xml_data)

    # RPC failed; print list of errors as a comma-separated list
    else:
        print(f"{task.host.name}: Errors: {','.join(get_resp.errors)}")

    # Return the results so they can accessed in the processors
    return Result(host=task.host, result=result)


def main():
    """
    Execution starts here.
    """

    # Initialize Nornir and register output file processors
    init_nornir = InitNornir()
    nornir = init_nornir.with_processors([ProcJSON(), ProcCSV()])

    # Build the SLA filter string in subtree format
    sla_xmlns = "http://cisco.com/ns/yang/Cisco-IOS-XE-ip-sla-oper"
    sla_filter = f'<ip-sla-stats xmlns="{sla_xmlns}"></ip-sla-stats>'

    # Perform the data collection using NETCONF with new filter
    nornir.run(task=collect_sla_stats, sla_filter=("subtree", sla_filter))


if __name__ == "__main__":
    main()
