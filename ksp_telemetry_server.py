#!/usr/bin/env python3

# A script to fetch streaming telemetry from KSP and plot it in a browser

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
    help="simulate connection KSP/krpc",
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
args = parser.parse_args()

simulate_krpc = args.simulate_krpc
period = args.period

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
    flight = None
else:
    print("Setting up krpc connection")
    conn = krpc.connect(name='ksp_telemetry_server')
    space_center = conn.space_center
    vessel = space_center.active_vessel
    flight = vessel.flight(vessel.orbit.body.reference_frame)

sc_logger = krpc_logger.LoggableSpaceCenter(conn, space_center, "sc")
# vessel_logger = krpc_logger.LoggableVessel(conn, vessel, "active_vessel")
flight_logger = krpc_logger.LoggableFlight(conn, flight, "flight")
loggable_list = [sc_logger, flight_logger]

def update_streams():
    dfs_new = [loggable.update() for loggable in loggable_list]
    df_new = pd.concat(dfs_new, axis=1)
    return(df_new)

######################
# Set up Bokeh plots #
######################
df = update_streams()
source = ColumnDataSource(df)
tools = "xpan,xwheel_zoom,xbox_zoom,reset"

p = figure(tools=tools, x_axis_type="datetime")
p.x_range.follow = "end"
p.x_range.range_padding = 0
p.toolbar.logo = None
p.line(x='sc_ut', y='flight_pitch', line_color='blue', source=source)
p.line(x='sc_ut', y='flight_heading', line_color='red', source = source)
p.line(x='sc_ut', y='flight_roll', line_color='green', source = source)

p2 = figure(tools=tools, x_axis_type='mercator', y_axis_type='mercator')
p2.xaxis.axis_label = "Longitude"
p2.yaxis.axis_label = "Latitude"
p2.toolbar.logo = None
p2.line(x='flight_longitude', y='flight_latitude', source=source)

def update():
    df_new = update_streams()
    source.stream(df_new, 300)

curdoc().add_root(
    layout(
        [
            [p, p2]
        ],
        sizing_mode="stretch_both",
    )
)
curdoc().add_periodic_callback(update, period*1000)