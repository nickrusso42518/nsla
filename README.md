[![Build Status](
https://travis-ci.com/nickrusso42518/nsla.svg?branch=master)](
https://travis-ci.com/nickrusso42518/nsla)

# Nornir Service Level Agreement (NSLA)
This project uses Nornir and NETCONF to manage IP SLA probes
on IOS-XE (and IOS-XR in the future) devices. Given an inventory
of N nodes, it configures N probes on each node, one to each node
in the inventory. To collect the performance statistics, you
can run a script to generate JSON and CSV reports. Alternatively,
you can integrate gRPC dial-out telemetry subscriptions to a collector
(such as TIG or ELK stacks) to display dashboards for real-time monitoring.

> Contact information:\
> Email:    njrusmc@gmail.com\
> Twitter:  @nickrusso42518

  * [Installation](#installation)
  * [Components](#components)
  * [Operations](#operations)
  * [Variables](#variables)
  * [Output Formats](#output-formats)

## Installation
Follows these steps to get started. This assumes you have Python 3.6 or
newer already installed, along with `pip` for Python package management:
  1. Clone the repository: `git clone https://github.com/nickrusso42518/nsla.git`
  2. Create a new virtual environment (venv): `python3.6 -m venv ~/narc`
  3. Activate the new venv: `source ~/nsla/bin/activate`
  4. Install packages into the venv: `pip install -r requirements.txt`
  5. Type `make lint` and ensure all tests pass. See "Testing" for more details.

## Components
This project is built on two powerful Python-based tools:
  1. [Nornir](https://github.com/nornir-automation/nornir),
     a task execution framework with concurrency support
  2. [ncclient](https://github.com/ncclient/ncclient),
     a library for interacting with network devices using NETCONF

## Variables
This section explains the three tiers of variables you can adjust.

### Host-specific Variables
Each host in the inventory only needs to specify two variables.

  * `node_id`: Unique node ID as an unsigned 16-bit integer (greater than 0)
    that represents the current node. All other nodes in the inventory will
    use this ID as their SLA operation number towards this node.
  * `ipsla_addr`: The IP address on the node to use as the IP SLA endpoint.
    All other nodes in the inventory will target this IP address. Often
    times, this will be a loopback interface (not a management interface) so
    it is not appropriate to use the Nornir-accessible IP address.

### Group-specific Variables
For each supported platform, the following variables must be identified.
  * `measurement`: Top-level dict for required measurement parameters
    * `base`: The base xpath prefix that all measurements share
    * `rtt`: The round-trip time (RTT) xpath suffix
    * `jitter`: The jitter xpath suffix
    * `oneway`: The one-way latency xpath suffix

### System-wide Variables
It is less common to change these variables once they have been
established. These apply to the entire system.

  * `sla`: Top-level dict for Service Level Agreement (SLA) variables
    * `frequency_s`: How often the SLA operation runs, in seconds
    * `packet_count`: How many packets are sent in each SLA operation
    * `packet_interval_ms`: How much time between packets, in msec
    * `timeout_ms`: Time limit for successful SLA operations, in msec
    * `tos`: The Type of Service for QoS treatment, range 0-255
    * `destination_port`: The destination UDP port for each SLA operation

  * `mdt`: Top-level dict for Model-Driven Telemetry (MDT) variables
    * `sub_id`: Dial-out telemetry subscription ID
    * `interval_s`: Telemetry transmission interval, in seconds
    * `collector_ip_addr`: Telemetry collector IP address
    * `collector_grpc_port`: Telemetry colector gRPC port (TCP)

## Operations
There are two core scripts in this solution:
  * `collect_stats.py`: Once probes have been configured, run this script
    to generate an on-demand performance report. See "Output Formats" for
    additional details about these formats.
  * `manage_probes.py`: Based on the variables just described, configures
    the required SLA operations and telemetry subscriptions on each
    device. Note that SLA operations cannot be completely reconfigured
    after being defined, so changing a key parameter (such as destination
    port) requires a probe to be deleted and re-added. Use the `-r` option
    to perform this rebuild. This uses a NETCONF `edit-config` using
    a `delete` operation to the SLA tree first.

## Operations
There are two core scripts in this solution:
  * `collect_stats.py`: Once probes have been configured, run this script
    to generate an on-demand performance report. See "Output Formats" for
    additional details about these formats.
  * `manage_probes.py`: Based on the variables just described, configures
    the required SLA operations and telemetry subscriptions on each
    device. Note that SLA operations cannot be completely reconfigured
    after being defined, so changing a key parameter (such as destination
    port) requires a probe to be deleted and re-added. Use the `-r` option
    to perform this rebuild. This uses a NETCONF `edit-config` using
    a `delete` operation to the SLA tree first.

## Output Formats
The `collect_stats.py` script runs synchronously and creates two output
files for each host in the inventory in the `outputs/` directory:
  * `result.csv`: A comma-separated values (CSV) file which separates
    a useful subset of performance statistics from all probes. The file
    will have NxN rows and is easily readable in graphical interfaces
    (ie, yoru manager will love it).
  * `result.json`: A mostly-raw dump of the NETCONF `get` RPC response
    with a top-level key inserted representing each host. This file can
    be fed into other systems for programmatic dissection or display.

See the `samples/` directory for some example output files.

Alternatively, you can use a Grafana-based system (such as the TIG stack) to
collect and display telemetry data in real-time. The `manage_probes.py`
script, in addition to configure probes and subscriptions, also interfaces
with the Grafana REST API to automatically build the proper dashboards. Each
inventory host gets it's own dashboard, and within that dashboard, there is a
panel for each SLA target. Therefore, there are N dashboards and NxN panels
in total.
