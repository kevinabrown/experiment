#!/usr/bin/env python3
'''
    This scripts writes the period.file with flow rate adjustments
    
    This script converts the BW demands and inflection points
    into the format required for CODES simulations"

    To set the injection rate in CODES, you set the message size and 
    the delay between successive messages.
'''

import sys
import json
import argparse
from pprint import pprint

parser = argparse.ArgumentParser(description='Generate CODES flow configs for ModSim25 experiments.')
parser.add_argument('flows_file', help='The path to the flow rate information JSON-formatted file.')
parser.add_argument('--codes_flows_file', help='The path to the CODES config file to create', default='../multiflow/period.file')

# Parse arguments
args = parser.parse_args()
flowsfile = args.flows_file
codesflowsfile = args.codes_flows_file

# Open and read the JSON file
flowrates = {}
with open(flowsfile, 'r') as file:
    flowrates = json.load(file)

pprint(flowrates)

# Set base rate for 25GB bandwidth
message_size = 64
bw = 25*(1024*1024*1024)/(1000*1000*1000)
base_rate = message_size/bw


# Reshape schedules to isolate individual flows
flows = {}
for key in flowrates.keys():
    for k, v in flowrates[key].items():
        k = int(k)
        key = int(key)
        if v == 0:
            v = 0.1
        tmp = (v/25)*100
        myrate = base_rate * (100/tmp)
        if not k in flows.keys():
            flows[k] = []
        flows[k].append((key, round(myrate, 6)))

pprint(flows)

# RATE FILE
# Create/overwrite rate file
rate_file = open('../multiflow/period.file', 'w')

# Set and write injection delays for given rate changes
for flow in sorted(flows.keys()):
    rate_file.write( "%d " % (len(flows[flow])) )
    for i, rate in flows[flow]:
        timestamp = i*1000
        rate_file.write( "%d:%f " % (timestamp, rate) )
    rate_file.write("\n")

# Write rate entry for allreduce SWM
rate_file.write("0\n")
rate_file.close()


# WORKLOAD ALLOCATION FILES
flowconfigs = {
        0: {'workload' : '2 synthetic0 0 4.0', 'allocation' : '14 3'},
        1: {'workload' : '2 synthetic0 0 4.0', 'allocation' : '15 0'},
        2: {'workload' : '2 synthetic0 0 4.0', 'allocation' : '1 2'}
        }

# Create/overwrite workload file
workload_file = open('../conf/work.load', 'w')
for flow in sorted(flows.keys()):
    workload_file.write(flowconfigs[flow]['workload'] + '\n')

# Write workload entry for allreduce SWM
workload_file.write('4 allreduce 0 0.0\n')
workload_file.close()

# Create/overwrite allocation file
allocation_file = open('../conf/alloc.conf', 'w')
for flow in sorted(flows.keys()):
    allocation_file.write(flowconfigs[flow]['allocation'] + '\n')

# Write allocation entry for allreduce SWM
allocation_file.write('50 51 52 53\n')
allocation_file.close()
