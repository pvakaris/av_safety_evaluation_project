import carla
import weakref
import math
import time
import sys
from recording.route_monitor import RouteMonitor
from recording.lane_monitor import LaneMonitor
from recording.collision_monitor import CollisionMonitor
from recording.traffic_monitor import TrafficMonitor
from recording.speeding_monitor import SpeedingMonitor
from recording.vehicle_light_monitor import VehicleLightMonitor
from recording.recorder import Recorder

import logging
logger = logging.getLogger(__name__)
class Manager():
    
    def __init__(self, path_locations, world, player, participant_name, scenario_name):
        self.path_locations = path_locations
        self.world = world
        self.player = player
        self.participant_name = participant_name
        self.scenario_name = scenario_name
        self.map = self.world.get_map()
        self.time = 0
        
        self.speeding = False
        self.junction_visited_in_last_timestep = False
        
        self.collision_sensor = CollisionSensor(self.player, self.world, self)
        self.lane_invasion_sensor = LaneInvasionSensor(self.player, self.world, self)
        save_file = '../../data/recordings/{}/{}/'.format(participant_name, scenario_name)
        self.route_monitor = RouteMonitor(self.path_locations, self.map, save_file)
        self.lane_monitor = LaneMonitor(save_file)
        self.collision_monitor = CollisionMonitor(save_file)
        self.speeding_monitor = SpeedingMonitor(save_file)
        self.traffic_monitor = TrafficMonitor(save_file)
        self.vehicle_light_monitor = VehicleLightMonitor(save_file)
        
        self.recorder = Recorder(participant_name, scenario_name)
        self.recorder.start_recording()
        
        self.time_of_last_collision = None
        self.actor_of_last_collision = None
        logger.info("Manager was successfully initialised")
    
    # Called at each timestep. Checks for violations and records to respective monitors
    def record(self, simulation_time):
        # logger.info("Manager recording at {}".format(str('%.3f' % (simulation_time / 1000))+"s"))
        try:
            player_location = self.player.get_location()
            self.time = simulation_time
            # Check if turn indicators are on
            weather = self.world.get_weather()
            self.set_lights(weather, self.time, player_location)
            # Check if turn indicators are on
            is_changing_lane = False
            if self.vehicle_light_monitor.turning_left() or self.vehicle_light_monitor.turning_right():
                is_changing_lane = True
            
            self.route_monitor.update(player_location, is_changing_lane)
            speeding = self.check_speeding()
            violating_traffic = self.check_traffic_violations()
            if speeding:
                self.speeding_monitor.add_to_buffer(speeding[1], speeding[0], self.time, player_location)
            if violating_traffic:
                self.traffic_monitor.add_to_buffer(self.speeding, self.time, player_location, "redlight")
            # logger.info("Observations were added to the buffers successfully.")
            if self.route_monitor.finish_reached(player_location):
                logger.info("Finish was reached. Terminating the simulation.")
                self.shut_down(True)
                return True
        except Exception as e:
            logger.error("Something went wrong adding observations to monitor buffers.", e)
        
    # Called when finish is reached or simulation is quit manually
    def shut_down(self, finish_reached):
        logger.info("Shutting the manager down. Saving data from monitors to files.")
        try:
            self.route_monitor.write_to_file(finish_reached, self.time)
            self.lane_monitor.write_to_file()
            self.collision_monitor.write_to_file()
            self.traffic_monitor.write_to_file()
            self.speeding_monitor.write_to_file()
            self.vehicle_light_monitor.write_to_file()
            self.recorder.stop_recording()
        except Exception as e:
            logger.error("Something went wrong saving data from monitors to files.", e)
        try:
            logger.info("Destroying sensors.")
            self.delete_sensors()
        except Exception as e:
            logger.error("Something went wrong destroying sensors owned by the Manager.", e)
    # After the simulation is over, delete sensors
    def delete_sensors(self):
        self.collision_sensor.sensor.stop()
        self.collision_sensor.sensor.destroy()
        self.lane_invasion_sensor.sensor.stop()
        self.lane_invasion_sensor.sensor.destroy()
    
    # Record the collision to the collision monitor buffer
    def record_collision(self, intensity, other_actor, player_location):
        # If there was a collision witht the same actor in the past 2sec, disregards this (collision sensor sometimes counts a collision multiple times)
        if(self.actor_of_last_collision and self.actor_of_last_collision == other_actor.id and (self.time - self.time_of_last_collision)/1000 < 2):
            pass
        else:
            self.time_of_last_collision = self.time
            self.actor_of_last_collision = other_actor.id
            self.collision_monitor.add_to_buffer(intensity, other_actor, player_location, self.time, self.speeding)
    
    # Record the lane marking violations to the lane monitor buffer
    def record_lane_invasion(self, text):
        if self.vehicle_light_monitor.turning_left():
            light_indicator_text = "Left"
        elif self.vehicle_light_monitor.turning_right():
            light_indicator_text = "Right"
        else:
            light_indicator_text = "None"
        self.lane_monitor.add_to_buffer(text, self.time, self.player, self.speeding, light_indicator_text)
        
    # Check if the vehicle speeding
    def check_speeding(self):
        current_speed = self.player.get_velocity().x
        # Convert from m/ to km/h and round to 2 places after comma
        current_speed = float('%.2f' % (abs(current_speed)*3.6))
        speed_limit = self.player.get_speed_limit()
        if current_speed and speed_limit and current_speed > speed_limit:
            self.speeding = True
            return (current_speed, speed_limit)
        else:
            self.speeding = False
            return None
    
    # Check if any traffic violations occurred (for now checks only for red lights)
    def check_traffic_violations(self):
        waypoint = self.map.get_waypoint(self.player.get_location())
        if waypoint.is_junction:
            if not self.junction_visited_in_last_timestep and str(self.player.get_traffic_light_state()) == "Red":
                self.junction_visited_in_last_timestep = True
                return True
            else:
                return False
        else:
            self.junction_visited_in_last_timestep = False
            return False
        
    # Update vehicle light monitor state (update which ligths are on)
    def set_lights(self, weather, time, player_location):
        light_state = self.player.get_light_state()
        self.vehicle_light_monitor.set_lights(light_state, weather, time, player_location)
        
            
# The foundations of this sensor were borrowed from CARLA developers            
class LaneInvasionSensor(object):
    def __init__(self, parent_actor, world, manager):
        self.sensor = None
        self.manager = manager
        bp = world.get_blueprint_library().find('sensor.other.lane_invasion')
        self.sensor = world.spawn_actor(bp, carla.Transform(), attach_to=parent_actor)
        # We need to pass the lambda a weak reference to self to avoid circular
        # reference.
        weak_self = weakref.ref(self)
        self.sensor.listen(lambda event: LaneInvasionSensor._on_invasion(weak_self, event))

    @staticmethod
    def _on_invasion(weak_self, event):
        self = weak_self()
        if not self:
            return
        lane_types = set(x.type for x in event.crossed_lane_markings)
        text = ['%r' % str(x).split()[-1] for x in lane_types]
        self.manager.record_lane_invasion(text[0].replace("'", ""))

        
# The foundations of this sensor were borrowed from CARLA developers        
class CollisionSensor(object):
    def __init__(self, parent_actor, world, manager):
        self.sensor = None
        self.player = parent_actor
        self.manager = manager
        bp = world.get_blueprint_library().find('sensor.other.collision')
        self.sensor = world.spawn_actor(bp, carla.Transform(), attach_to=self.player)
        # We need to pass the lambda a weak reference to self to avoid circular
        # reference.
        weak_self = weakref.ref(self)
        self.sensor.listen(lambda event: CollisionSensor._on_collision(weak_self, event))

    @staticmethod
    def _on_collision(weak_self, event):
        self = weak_self()
        if not self:
            return
        impulse = event.normal_impulse
        intensity = math.sqrt(impulse.x**2 + impulse.y**2 + impulse.z**2)
        self.manager.record_collision(intensity, event.other_actor, self.player.get_location())
        