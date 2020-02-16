#!/usr/bin/env python3

# A script to fetch streaming telemetry from KSP and plot it in a browser with bokeh and krpc

# Ian Dahlke, 2020

import argparse
import datetime
import krpc
import krpc_logger
import numpy as np
import pandas as pd

from bokeh.layouts import row, column, gridplot, layout
from bokeh.plotting import curdoc, figure
from bokeh.models import ColumnDataSource
from bokeh.driving import count

# Parse Arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    "-s",
    "--simulate_krpc",
    help="simulate connection to KSP/krpc",
    type=bool,
    default=False
)
parser.add_argument(
    "-p",
    "--period",
    help="Data polling period in seconds",
    type=float,
    default=1.0
)

parser.add_argument(
    "-a",
    "--address",
    help="ip address",
    type=str,
    default="localhost"
)
args = parser.parse_args()

simulate_krpc = args.simulate_krpc
period = args.period
address = args.address

#########################
# Set Up KRPC streaming #
#########################
# Define/load logging items
# This may only support property access right now

# Set up krpc connection and objects
if simulate_krpc:
    print("Simulating krpc connection")
    conn = None
    space_center = None
    vessel = None
    orbit = None
    flight = None
    autopilot = None
    
else:
    print("Setting up krpc connection")
    conn = krpc.connect(name='ksp_telemetry_server', address=address)
    space_center = conn.space_center
    vessel = space_center.active_vessel
    orbit = vessel.orbit
    flight = vessel.flight(vessel.orbital_reference_frame)
    autopilot = vessel.auto_pilot

sc_logger = krpc_logger.LoggableSpaceCenter(conn, space_center, "sc")
vessel_logger = krpc_logger.LoggableVessel(conn, vessel, "vessel")
orbit_logger = krpc_logger.LoggableOrbit(conn, orbit, "orbit")
flight_logger = krpc_logger.LoggableFlight(conn, flight, "flight")
autopilot_logger = krpc_logger.LoggableAutopilot(conn, autopilot, "autopilot")
loggable_list = [sc_logger, autopilot_logger, vessel_logger, orbit_logger, flight_logger]

def update_streams():
    dfs_new = [loggable.update() for loggable in loggable_list]
    df_new = pd.concat(dfs_new, axis=1)
    df_new.sc_ut = pd.to_timedelta(df_new.sc_ut, unit='s')
    df_new.vessel_met = pd.to_timedelta(df_new.vessel_met, unit='s')
    return(df_new)

######################
# Set up Bokeh plots #
######################
df = update_streams()
# df.sc_ut = pd.to_datetime(df.sc_ut, unit='s')
# df.vessel_met = pd.to_timedelta(df.vessel_met, unit='s')
source = ColumnDataSource(df)
tools = "xpan,xwheel_zoom,xbox_zoom,reset"

p = figure(tools=tools, x_axis_type='datetime')
p.xaxis.axis_label = "Time"
p.x_range.follow = "end"
p.x_range.follow_interval = pd.Timedelta(10, unit='s')
p.x_range.range_padding = 0
p.toolbar.logo = None
p.line(x='vessel_met', y='flight_pitch', line_color='blue', source=source, legend_label="Pitch")
p.line(x='vessel_met', y='flight_heading', line_color='red', source = source, legend_label="Heading")
p.line(x='vessel_met', y='flight_roll', line_color='green', source = source, legend_label="Roll")
p.line(x='vessel_met', y='autopilot_target_pitch', source=source, line_color='lightblue', legend_label="Pitch Target")
p.line(x='vessel_met', y='autopilot_target_heading', source=source, line_color='orangered', legend_label="Heading Target")
p.line(x='vessel_met', y='autopilot_target_roll', source=source, line_color='lightgreen', legend_label="Roll Target")
p.legend.click_policy = 'hide'

p2 = figure(x_range=(-180, 180), y_range=(-90,90)) #, x_axis_type='mercator', y_axis_type='mercator')
p2.xaxis.axis_label = "Longitude"
p2.yaxis.axis_label = "Latitude"
# p2.x_range.follow = "end"
# p2.x_range.range_padding = 0
p2.x_range.bounds = (-180, 180)
p2.y_range.bounds = (-90, 90)
p2.toolbar.logo = None
p2.line(x='flight_longitude', y='flight_latitude', source=source, line_width=10, line_cap='square')

p3 = figure(tools=tools, x_axis_type='datetime')
p3.xaxis.axis_label = "Time"
p3.x_range.follow = "end"
p3.x_range.follow_interval = pd.Timedelta(10, unit='s')
p3.x_range.range_padding = 0
p3.toolbar.logo = None
p3.line(x='vessel_met', y='autopilot_pitch_error', source=source, line_color='lightblue', legend_label="Pitch Error")
p3.line(x='vessel_met', y='autopilot_heading_error', source=source, line_color='orangered', legend_label="Heading Error")
p3.line(x='vessel_met', y='autopilot_roll_error', source=source, line_color='lightgreen', legend_label="Roll Error")

p3.legend.click_policy="hide"

def update():
    df_new = update_streams()
    source.stream(df_new, 10000)

curdoc().add_root(
    layout(
        [
            [p3],
            [p, p2]
        ],
        sizing_mode="stretch_both",
    )
)
curdoc().add_periodic_callback(update, period*1000)