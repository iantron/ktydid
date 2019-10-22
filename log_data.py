#!/usr/bin/env python3

# A simple logging script for kRPC

# Ian Dahlke, 2019
#    credit Alexander Korsunsky, 2016
#    https://gist.github.com/fat-lobyte/4326afa551fa04dd028f

import argparse
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

# Define/load logging items
log_items = {
	'space_center':['ut'],
	'flight':['mean_altitude'],
	'orbit':['apoapsis_altitude']
	}

# Set up streams for telemetry
categories = ['space_center', 'flight', 'orbit']
stream_list = []

print("Logging items:")
for category in categories:
	for log_name in log_items[category]:
		print("...", category, log_name)
		stream_list += conn.add_stream(getattr, exec(category), log_name)

# Set up output file and log
print("Logging CSV data to: ", outfilename)
with open(outfilename, 'w') as out_file:
	csv_writer = csv.writer(out_file, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    header = [item for category in log_items for item in log_items[category]]
	csv_writer.writerow(header)
	
	# Main Logging Loop
	print("Starting log. Please stop it by pressing Control-C")
	try:
		while True:
			line = [stream() for stream in stream_list]
			csv_writer.writerow(line)
			sys.stdout.flush()
			time.sleep(interval)
	except KeyboardInterrupt as e:
		print("\nThanks for logging. Bye!")