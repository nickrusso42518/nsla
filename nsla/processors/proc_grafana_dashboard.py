#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: A concrete processor that stores the packet-tracer
results in JSON format.
"""

import json
import xmltodict
from grafana_api.grafana_face import GrafanaFace
from nsla.processors.proc_base import ProcBase
from jinja2 import Environment, FileSystemLoader


class ProcGrafanaDashboard(ProcBase):
    """
    Represents a processor object, inheriting from ProcBase,
    for the JSON format.
    """

    def __init__(self, host=None, user="admin", password="admin", port=3000):
        """
        """

        # Create the GrafanaFace object to interface with the API
        self.grafana_api = GrafanaFace(
            host=host,
            auth=(user, password), port=port
        )

    def task_instance_completed(self, task, host, mresult):
        """
        When each host finishes running the task, assemble
        the Grafana dashboards then create/update them via the API.
        """

        # Build a jinja2 environment referencing the templates directory
        j2_env = Environment(
            loader=FileSystemLoader("nsla/processors/templates"),
            autoescape=True,
        )

        # Reference the panel template first and initialize empty panel list
        panel_temp = j2_env.get_template("grafana_panel.j2.json")
        panels = []

        # Build panels first, one per inventory host
        for k, v in task.nornir.inventory.hosts.items():

            # Define data variables for jinja2 templates
            data = {
                "local_hostname": host.name,
                "remote_hostname": k,
                "remote_node_id": v["node_id"],
                # "local_node_id": host["node_id"],  # not used; maybe later
            }

            # Render template, convert text to JSON, and add to panel list
            panel_config = panel_temp.render(data=data)
            panels.append(json.loads(panel_config))

        # Encapsulate the panels in a dashboard using same jinja2/json process
        dboard_temp = j2_env.get_template("grafana_dashboard.j2.json")
        dboard_config = dboard_temp.render(data=data)
        dboard_data = json.loads(dboard_config)
        dboard_data["panels"] = panels

        # Create the dashboards on Grafana using the API
        body = {"dashboard": dboard_data, "overwrite": True}
        resp = self.grafana_api.dashboard.update_dashboard(dashboard=body)
        print(f"{host.name} dashboard URL: {resp['url']}")
