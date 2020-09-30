#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Package init file to import each module
to simplify access individual processor classes.
"""

from nsla.processors.proc_terse import ProcTerse
from nsla.processors.proc_csv import ProcCSV
from nsla.processors.proc_json import ProcJSON
from nsla.processors.proc_grafana_dashboard import ProcGrafanaDashboard
