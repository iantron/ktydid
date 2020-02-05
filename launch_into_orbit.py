#!/usr/bin/env python3

# A launch script for kRPC. Initially this has very few deviations from the original.

# Ian Dahlke, 2019
#    credit kRPC launch tutorial

import math
import time
import krpc

# Get Connection
print('Setting up connection')
conn = krpc.connect(name='launch_into_orbit')
vessel = conn.space_center.active_vessel

# Set up streams for telemetry
ut = conn.add_stream(getattr, conn.space_center, 'ut')
altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')
stage_2_resources = vessel.resources_in_decouple_stage(stage=2, cumulative=False)
srb_fuel = conn.add_stream(stage_2_resources.amount, 'SolidFuel')

# Configure Ascent
turn_start_altitude = 500
turn_end_altitude = 70000
target_altitude = 80000

# Configure Vessel
vessel.control.sas = False
vessel.control.rcs = False
vessel.control.throttle = 1.0

# Countdown...
duration = 10
count = list(range(1,duration+1))
count.reverse()
for i in count:
	print(i, "...")
	time.sleep(1)
print("Launch!")

# Launch
vessel.control.activate_next_stage()
vessel.auto_pilot.engage()
vessel.auto_pilot.target_pitch_and_heading(90, 90)
# vessel.auto_pilot.target_roll(180)
# vessel.auto_pilot.roll_threshold = 1
# vessel.auto_pilot.stopping_time = (1,1,1)

# Main ascent loop
srbs_separated = False
turn_angle_start = 7
turn_angle_end = 90
turn_angle = 0
while True:

    # Gravity turn
    if altitude() > turn_start_altitude and altitude() < turn_end_altitude:
        frac = ((altitude() - turn_start_altitude) /
                (turn_end_altitude - turn_start_altitude))
        new_turn_angle = frac * (turn_angle_end - turn_angle_start) + turn_angle_start
        if abs(new_turn_angle - turn_angle) > 0.5:
            turn_angle = new_turn_angle
            print(turn_angle)
            vessel.auto_pilot.target_pitch_and_heading(90-turn_angle, 90)

    # Separate SRBs when finished
    # if not srbs_separated:
        # if srb_fuel() < 0.1:
            # vessel.control.activate_next_stage()
            # srbs_separated = True
            # print('SRBs separated')

    # Decrease throttle when approaching target apoapsis
    if apoapsis() > target_altitude*0.9:
        print('Approaching target apoapsis')
        break

# Disable engines when target apoapsis is reached
vessel.control.throttle = 0.25
while apoapsis() < target_altitude:
    pass
vessel.control.throttle = 0.0
print('Target apoapsis reached')

# Wait until out of atmosphere
print('Coasting out of atmosphere')

while altitude() < 70500:
    pass

# Remove thrust limit
for engine in vessel.parts.engines:
	engine.thrust_limit = 1

# Plan circularization burn (using vis-viva equation)
print('Planning circularization burn')
mu = vessel.orbit.body.gravitational_parameter
r = vessel.orbit.apoapsis
a1 = vessel.orbit.semi_major_axis
a2 = r
v1 = math.sqrt(mu*((2./r)-(1./a1)))
v2 = math.sqrt(mu*((2./r)-(1./a2)))
delta_v = v2 - v1
node = vessel.control.add_node(
    ut() + vessel.orbit.time_to_apoapsis, prograde=delta_v)

# Calculate burn time (using rocket equation)
F = vessel.available_thrust
Isp = vessel.specific_impulse * 9.82
m0 = vessel.mass
m1 = m0 / math.exp(delta_v/Isp)
flow_rate = F / Isp
burn_time = (m0 - m1) / flow_rate

# Orientate ship
print('Orientating ship for circularization burn')
vessel.auto_pilot.disengage()
vessel.auto_pilot.engage()
vessel.auto_pilot.reference_frame = node.orbital_reference_frame
vessel.auto_pilot.target_direction = (0, 1, 0)
vessel.auto_pilot.wait()

# Wait until burn
print('Waiting until circularization burn')
# burn_ut = ut() + vessel.orbit.time_to_apoapsis - (burn_time/2.)
# lead_time = 5
# conn.space_center.warp_to(burn_ut - lead_time)

# Execute burn
print('Ready to execute burn')
time_to_apoapsis = conn.add_stream(getattr, vessel.orbit, 'time_to_apoapsis')
while time_to_apoapsis() - (burn_time/2.) > 0:
    pass
print('Executing burn')
vessel.control.throttle = 1.0
time.sleep(burn_time)
# time.sleep(burn_time - 0.1)
# print('Fine tuning')
# vessel.control.throttle = 0.05
# remaining_burn = conn.add_stream(node.remaining_burn_vector, node.reference_frame)
# while remaining_burn()[1] > 0:
    # pass
vessel.control.throttle = 0.0
node.remove()

print('Launch complete')
