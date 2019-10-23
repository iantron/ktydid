#!/usr/bin/env python3

# A simple logging script for kRPC

# Ian Dahlke, 2019
#    credit Alexander Korsunsky, 2016
#    https://gist.github.com/fat-lobyte/4326afa551fa04dd028f

import argparse
import csv
import krpc
import numpy as np
import sys
import time

# Parse Arguments
parser = argparse.ArgumentParser()
parser.add_argument("outfile", help="Output filename")
parser.add_argument("configfile", help="Config filename")
parser.add_argument("-i", "--interval", help="Interval", type=float, default=1.0)
args = parser.parse_args()

outfilename = args.outfile
config_filename = args.configfile
interval = args.interval

# Get Connection
print("Setting up connection")
conn = krpc.connect(name='log_launch_telemetry')
print(conn.krpc.get_status().version)

space_center = conn.space_center
vessel = space_center.active_vessel
flight = vessel.flight(vessel.orbit.body.reference_frame)
orbit = vessel.orbit
auto_pilot = vessel.auto_pilot

# Define/load logging items
log_items = {
    'space_center':['ut'],
    'vessel':['met', 'thrust', 'mass'],
    'flight':['mean_altitude', 'speed', 'dynamic_pressure', 'lift', 'drag', 'angle_of_attack', 'pitch', 'heading'],
    'orbit':['apoapsis_altitude', 'periapsis_altitude']
    }

# Set up streams for telemetry
stream_list = []

print("Logging items:")
for category in log_items:
    for log_name in log_items[category]:
        print("...", category, log_name)
        stream_list += [conn.add_stream(getattr, globals()[category], log_name)]

# Set up output file and log
print("Logging CSV data to: ", outfilename)
with open(outfilename, 'w') as out_file:
    csv_writer = csv.writer(out_file, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    header = [item for category in log_items for item in log_items[category]]
    csv_writer.writerow(header)
    out_file.flush()

    # Main Logging Loop
    print("Starting log. Please stop it by pressing Control-C")
    try:
        while True:
            line = [stream() for stream in stream_list]
            csv_writer.writerow(line)
            out_file.flush()
            time.sleep(interval)
    except KeyboardInterrupt as e:
        print("\nThanks for logging. Bye!")