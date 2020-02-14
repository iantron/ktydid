#!/usr/bin/env python3
# Ian Dahlke, 2020

"""
KRPC Logger
This module is a handler for streaming data from krpc objects. It creates update methods for gathering and formatting data for many relevant object types.
"""

import datetime
import krpc
import numpy as np
import pandas as pd

class Loggable:
    def __init__(self, connection, loggable_object, name):
        self.connection = connection
        self.loggable_object = loggable_object
        self.name = name
        
        self.column_labels = []
        self.stream_list = []
        
        if self.attribute_config is None:
            print("No attributes to stream. Assign attribute_config and call setup_streams().")
        else:
            self.setup_streams()
    
    def setup_streams(self):
        for attribute, config in self.attribute_config.items():
            if self.connection is None:
                stream = config['sim_fun']
            else:
                stream = self.connection.add_stream(**(config['stream_params'](self.loggable_object, attribute)))
            example_return = stream()
            base_label = "{}_{}".format(self.name, attribute)
            if type(example_return) is tuple:
                column_labels = ["{}_{}".format(base_label, i) for i in range(len(example_return))]
                self.stream_list.append(stream)
            else:
                column_labels = [ base_label ]
                self.stream_list.append(lambda: [stream()])
                
            self.column_labels += column_labels
    
    def update(self):
        line = [stream() for stream in self.stream_list]
        line = [li for sublist in line for li in sublist]
        assert(len(line) == len(self.column_labels))
        df_new = pd.DataFrame([line], columns=self.column_labels)
        return(df_new)
    
    stream_params_attribute = lambda self, x, y: [getattr, x, y]
    stream_params_method = None
    attribute_template_ranf = lambda self, n: {
                'sim_fun': np.random.ranf if (n is 1) else (lambda: tuple(np.random.ranf(n))),
                'stream_params': self.stream_params_attribute
            }

class LoggableSpaceCenter(Loggable):
    def __init__(self, connection, loggable_object, name):
        self.attribute_config = {
            'ut': {
                'sim_fun': datetime.datetime.now,
                'stream_params': self.stream_params_attribute
            }
        }
        Loggable.__init__(self, connection, loggable_object, name)

class LoggableFlight(Loggable):
    def __init__(self, connection, loggable_object, name):
        self.attribute_config = {
            'g_force': self.attribute_template_ranf(1),
            'mean_altitude': self.attribute_template_ranf(1),
            'surface_altitude': self.attribute_template_ranf(1),
            'elevation': self.attribute_template_ranf(1),
            'latitude': self.attribute_template_ranf(1),
            'longitude': self.attribute_template_ranf(1),
            'velocity': self.attribute_template_ranf(3),
            'speed': self.attribute_template_ranf(1),
            'horizontal_speed': self.attribute_template_ranf(1),
            'vertical_speed': self.attribute_template_ranf(1),
            'center_of_mass': self.attribute_template_ranf(3),
            'rotation': self.attribute_template_ranf(4),
            'direction': self.attribute_template_ranf(3),
            'pitch': self.attribute_template_ranf(1),
            'heading': self.attribute_template_ranf(1),
            'roll': self.attribute_template_ranf(1),
            'prograde': self.attribute_template_ranf(3),
            'retrograde': self.attribute_template_ranf(3),
            'normal': self.attribute_template_ranf(3),
            'anti_normal': self.attribute_template_ranf(3),
            'radial': self.attribute_template_ranf(3),
            'anti_radial': self.attribute_template_ranf(3),
            'atmosphere_density': self.attribute_template_ranf(1),
            'dynamic_pressure': self.attribute_template_ranf(1),
            'static_pressure': self.attribute_template_ranf(1),
            'static_pressure_at_msl': self.attribute_template_ranf(1),
            'aerodynamic_force': self.attribute_template_ranf(3),
            'lift': self.attribute_template_ranf(3),
            'drag': self.attribute_template_ranf(3),
            'speed_of_sound': self.attribute_template_ranf(1),
            'mach': self.attribute_template_ranf(1),
            'reynolds_number': self.attribute_template_ranf(1),
            'true_air_speed': self.attribute_template_ranf(1),
            'equivalent_air_speed': self.attribute_template_ranf(1),
            'terminal_velocity': self.attribute_template_ranf(1),
            'angle_of_attack': self.attribute_template_ranf(1),
            'sideslip_angle': self.attribute_template_ranf(1),
            'total_air_temperature': self.attribute_template_ranf(1),
            'static_air_temperature': self.attribute_template_ranf(1),
            'stall_fraction': self.attribute_template_ranf(1),
            'drag_coefficient': self.attribute_template_ranf(1),
            'lift_coefficient': self.attribute_template_ranf(1),
            'ballistic_coefficient': self.attribute_template_ranf(1),
            'thrust_specific_fuel_consumption': self.attribute_template_ranf(1),
        }
        Loggable.__init__(self, connection, loggable_object, name)

    
class LoggableVessel(Loggable):
    def __init__(self, connection, loggable_object, name):
        self.attribute_config = {
            'met': {
                'sim_fun': datetime.datetime.now,
                'stream_params': self.stream_params_attribute
            },
            'mass': self.attribute_template_ranf(1),
            'dry_mass': self.attribute_template_ranf(1),
            'thrust': self.attribute_template_ranf(1),
            'available_thrust': self.attribute_template_ranf(1),
            'max_thrust': self.attribute_template_ranf(1),
            'max_vacuum_thrust': self.attribute_template_ranf(1),
            'specific_impulse': self.attribute_template_ranf(1),
            'vacuum_specific_impulse': self.attribute_template_ranf(1),
            'moment_of_inertia': self.attribute_template_ranf(1),
            'inertia_tensor': self.attribute_template_ranf(1),
            
        }
        Loggable.__init__(self, connection, loggable_object, name)
        
class LoggableAutopilot(Loggable):
    def __init__(self, connection, loggable_object, name):
        self.attribute_config = {
            'error': self.attribute_template_ranf(1),
            'pitch_error': self.attribute_template_ranf(1),
            'heading_error': self.attribute_template_ranf(1),
            'roll_error': self.attribute_template_ranf(1),
            'target_pitch': self.attribute_template_ranf(1),
            'target_heading': self.attribute_template_ranf(1),
            'target_roll': self.attribute_template_ranf(1),
            'target_direction': self.attribute_template_ranf(3),
            'roll_threshold': self.attribute_template_ranf(1),
            'stopping_time': self.attribute_template_ranf(3),
            'deceleration_time': self.attribute_template_ranf(3),
            'attenuation_angle': self.attribute_template_ranf(3),
            'time_to_peak': self.attribute_template_ranf(3),
            'overshoot': self.attribute_template_ranf(3),
            'pitch_pid_gains': self.attribute_template_ranf(3),
            'roll_pid_gains': self.attribute_template_ranf(3),
            'yaw_pid_gains': self.attribute_template_ranf(3),
        }
        Loggable.__init__(self, connection, loggable_object, name)

class LoggableOrbit(Loggable):
    def __init__(self, connection, loggable_object, name):
        self.attribute_config = {
            'apoapsis': self.attribute_template_ranf(1),
            'periapsis': self.attribute_template_ranf(1),
            'apoapsis_altitude': self.attribute_template_ranf(1),
            'periapsis_altitude': self.attribute_template_ranf(1),
            'semi_major_axis': self.attribute_template_ranf(1),
            'semi_minor_axis': self.attribute_template_ranf(1),
            'radius': self.attribute_template_ranf(1),
            'speed': self.attribute_template_ranf(1),
            'period': self.attribute_template_ranf(1),
            'time_to_apoapsis': self.attribute_template_ranf(1),
            'time_to_periapsis': self.attribute_template_ranf(1),
            'eccentricity': self.attribute_template_ranf(1),
            'inclination': self.attribute_template_ranf(1),
            'longitude_of_ascending_node': self.attribute_template_ranf(1),
            'argument_of_periapsis': self.attribute_template_ranf(1),
            'epoch': self.attribute_template_ranf(1),
            'mean_anomaly': self.attribute_template_ranf(1),
            'eccentric_anomaly': self.attribute_template_ranf(1),
            'true_anomaly': self.attribute_template_ranf(1),
            'orbital_speed': self.attribute_template_ranf(1),
            'time_to_soi_change': self.attribute_template_ranf(1),
        }
        Loggable.__init__(self, connection, loggable_object, name)

class LoggableControl(Loggable):
    def __init__(self, connection, loggable_object, name):
        self.attribute_config = {
            'throttle': self.attribute_template_ranf(1),
            'pitch': self.attribute_template_ranf(1),
            'yaw': self.attribute_template_ranf(1),
            'roll': self.attribute_template_ranf(1),
            'forward': self.attribute_template_ranf(1),
            'up': self.attribute_template_ranf(1),
            'right': self.attribute_template_ranf(1),
            'wheel_throttle': self.attribute_template_ranf(1),
            'wheel_steering': self.attribute_template_ranf(1),
            'current_stage': self.attribute_template_ranf(1),
        }
        Loggable.__init__(self, connection, loggable_object, name)

class LoggableCommunications(Loggable):
    def __init__(self, connection, loggable_object, name):
        self.attribute_config = {
            'signal_strength': self.attribute_template_ranf(1),
            'signal_delay': self.attribute_template_ranf(1),
            'power': self.attribute_template_ranf(1),
        }
        Loggable.__init__(self, connection, loggable_object, name)
        
class LoggableResource(Loggable):
    def __init__(self, connection, loggable_object, name):
        self.attribute_config = {
            'amount': self.attribute_template_ranf(1),
            'max': self.attribute_template_ranf(1),
            'density': self.attribute_template_ranf(1),
        }
        Loggable.__init__(self, connection, loggable_object, name)

class LoggableNode(Loggable):
    def __init__(self, connection, loggable_object, name):
        self.attribute_config = {
            'prograde': self.attribute_template_ranf(1),
            'normal': self.attribute_template_ranf(1),
            'radial': self.attribute_template_ranf(1),
            'delta_v': self.attribute_template_ranf(1),
            'remaining_delta_v': self.attribute_template_ranf(1),
            'time_to': self.attribute_template_ranf(1),
        }
        Loggable.__init__(self, connection, loggable_object, name)