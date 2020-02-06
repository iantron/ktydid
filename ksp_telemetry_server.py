#!/usr/bin/env python3

# A script to fetch streaming telemetry from KSP and plot it in a browser

# Ian Dahlke, 2020

# import argparse
import pandas as pd
import numpy as np
import time
import datetime
try:
    import krpc
except ImportError:
    krpc_exists = False
    pass

from bokeh.layouts import row, column, gridplot
from bokeh.plotting import curdoc, figure
from bokeh.models import ColumnDataSource
from bokeh.driving import count

#########################
# Set Up KRPC streaming #
#########################
# Define/load logging items
# This may only support property access right now
# Also it'll put list items directly into the dataframe rather than breaking them up.
log_items = {
    'space_center':['ut'],
    'vessel':['met', 'thrust', 'mass'],
    'flight':['mean_altitude', 'speed', 'dynamic_pressure', 'lift', 'drag', 'angle_of_attack', 'pitch', 'heading'],
    'orbit':['apoapsis_altitude', 'periapsis_altitude']
    }
columns = ["{}_{}".format(category, item) for category in log_items for item in log_items[category]]

# Set up krpc connection and objects
if krpc_exists:
    print("Setting up krpc connection")
    conn = krpc.connect(name='ksp_telemetry_server')

    space_center = conn.space_center
    vessel = space_center.active_vessel
    flight = vessel.flight(vessel.orbit.body.reference_frame)
    orbit = vessel.orbit
#     auto_pilot = vessel.auto_pilot

    # Set up streams for telemetry
    print("Creating data streams...")
    stream_list = []
    for category in log_items:
        for log_name in log_items[category]:
            print("...", category, log_name)
            stream_list += [conn.add_stream(getattr, globals()[category], log_name)]
else:
    # set up fake data
    stream_list = [ datetime.datetime.now ]
    stream_list += [ lambda: tuple(np.random.ranf(3)) ]
    stream_list += [ np.random.ranf for i in range(len(columns)-2) ]

def update_streams():
    line = [stream() for stream in stream_list]
    new_columns = columns.copy()
    for field_name, value in zip(columns, line):
        if type(value) is tuple:
            new_columns += ['{}_{}'.format(field_name, i) for i in range(len(value))]
            line += [sub_value for sub_value in value]
        
    df_new = pd.DataFrame([line], columns=new_columns)
    return(df_new)

######################
# Set up Bokeh plots #
######################
df = update_streams()
source = ColumnDataSource(df)
print(df.columns)

p = figure(plot_height=500, tools="xpan,xwheel_zoom,xbox_zoom,reset", x_axis_type="datetime")
p.x_range.follow = "end"
# p.x_range.follow_interval = 100
p.x_range.range_padding = 0
p.line(x='space_center_ut', y='flight_pitch', source=source)

p2 = figure(plot_height=500, tools="xpan,xwheel_zoom,xbox_zoom,reset", x_axis_type="datetime")
p2.x_range.follow = "end"
# p2.x_range.follow_interval = 100
p2.x_range.range_padding = 0
p2.line(x='space_center_ut', y='flight_heading', source=source)

def update():
    df_new = update_streams()
    source.stream(df_new, 300)

curdoc().add_root(column(p, p2))
curdoc().add_periodic_callback(update, 500)