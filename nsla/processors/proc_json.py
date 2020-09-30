#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: A concrete processor that stores the packet-tracer
results in JSON format.
"""

import json
from nsla.processors.proc_base import ProcBase


class ProcJSON(ProcBase):
    """
    Represents a processor object, inheriting from ProcBase,
    for the JSON format.
    """

    def __init__(self):
        """
        Constructor initializes an empty dictionary to hold
        the results.
        """
        self.data = {}

    def task_completed(self, task, aresult):
        """
        After the task is completed for all hosts, write the JSON
        data to an output file.
        """
        super().task_completed(task, aresult)
        with open("outputs/result.json", "w") as handle:
            json.dump(self.data, handle, indent=2)

    def task_instance_completed(self, task, host, mresult):
        """
        When each host finishes running the task, assemble
        the JSON dictionaries based on the results, and update
        the main data dictionary for use later.
        """
        # pylint: disable=unused-argument
        self.data[host.name] = mresult[0].result
