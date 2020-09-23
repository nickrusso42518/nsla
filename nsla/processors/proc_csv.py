#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: A concrete processor that stores the packet-tracer
results in CSV format.
"""

import csv
from nsla.processors.proc_base import ProcBase


class ProcCSV(ProcBase):
    """
    Represents a processor object, inheriting from ProcBase,
    for the CSV format.
    """

    def __init__(self):
        """
        Constructor defines a string containing column headers
        to hold the results.
        """
        self.columns = [
            "name_s",
            "host_s",
            "name_d",
            "host_d",
            "oper_id",
            "succ_cnt",
            "fail_cnt",
            "rtt_min",
            "rtt_avg",
            "rtt_max",
            "lat_sd_min",
            "lat_sd_avg",
            "lat_sd_max",
            "lat_ds_min",
            "lat_ds_avg",
            "lat_ds_max",
            "jit_sd_min",
            "jit_sd_avg",
            "jit_sd_max",
            "jit_ds_min",
            "jit_ds_avg",
            "jit_ds_max",
            "pkt_lost_sd",
            "pkt_lost_ds",
            "pkt_wrong_seq",
            "pkt_late",
            "verify_fail",
        ]
        self.matrix = [self.columns]

    def task_completed(self, task, aresult):
        """
        After the task is completed for all hosts, write the CSV
        data to an output file.
        """
        super().task_completed(task, aresult)
        with open("outputs/result.csv", "w") as handle:
            sla_writer = csv.writer(handle)
            for row in self.matrix:
                sla_writer.writerow(row)

    def task_instance_completed(self, task, host, mresult):
        """
        When each host finishes running the task, assemble
        the CSV rows based on the results, and append them to
        the text string for use later.
        """
        sla_list = mresult[0].result["data"]["ip-sla-stats"]["sla-oper-entry"]
        for sla_entry in sla_list:

            # Create row with source name and host/IP
            row = [task.host.name, task.host.hostname]

            # Based on the SLA ID, find the target name and host/IP
            target_id = int(sla_entry["oper-id"])
            for k, v in task.nornir.inventory.hosts.items():
                if v["node_id"] == target_id:
                    row.extend([k, v.hostname])
                    break
            else:
                # Should be impossible, but prevent an error by using a filler
                row.extend(["UNK", "UNK"])

            # Capture high-level SLA stats
            row.append(target_id)
            row.append(sla_entry["success-count"])
            row.append(sla_entry["failure-count"])
        
            # Capture RTT performance stats
            stats = sla_entry["stats"]
            row.append(stats["rtt"]["sla-time-values"]["min"])
            row.append(stats["rtt"]["sla-time-values"]["avg"])
            row.append(stats["rtt"]["sla-time-values"]["max"])
        
            # Capture one-way latency performance stats (needs NTP)
            row.append(stats["oneway-latency"]["sd"]["min"])
            row.append(stats["oneway-latency"]["sd"]["avg"])
            row.append(stats["oneway-latency"]["sd"]["max"])
            row.append(stats["oneway-latency"]["ds"]["min"])
            row.append(stats["oneway-latency"]["ds"]["avg"])
            row.append(stats["oneway-latency"]["ds"]["max"])
        
            # Capture jitter performance stats
            row.append(stats["jitter"]["sd"]["min"])
            row.append(stats["jitter"]["sd"]["avg"])
            row.append(stats["jitter"]["sd"]["max"])
            row.append(stats["jitter"]["ds"]["min"])
            row.append(stats["jitter"]["ds"]["avg"])
            row.append(stats["jitter"]["ds"]["max"])
        
            # Capture packet loss performance stats
            row.append(stats["packet-loss"]["sd-count"])
            row.append(stats["packet-loss"]["ds-count"])
            row.append(stats["packet-loss"]["out-of-sequence"])
            row.append(stats["packet-loss"]["late-arrivals"])
        
            # Capture data verification error stats
            row.append(sla_entry["common-stats"]["no-of-verify-errors"])

            # Append row to the matrix for CSV writing later
            self.matrix.append(row)
