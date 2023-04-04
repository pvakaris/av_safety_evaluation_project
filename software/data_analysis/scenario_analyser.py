import glob
import os
import sys
import time
import random
import logging
import argparse
import xml.etree.ElementTree as ET
import numpy
import json
sys.path.append("..")
from carla_scripts.config import SAMPLING_RESOLUTION
from agents.navigation.global_route_planner import GlobalRoutePlanner

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla


argparser = argparse.ArgumentParser(description=__doc__)
argparser.add_argument(
    '--scenario', '-s',
    help='The scenario to consider')
argparser.add_argument(
    '--path', '-p',
    help='The path to consider')
args = argparser.parse_args()


# From location makes a route
def get_route(map, locations):
    waypoints = []
    grp = GlobalRoutePlanner(map, SAMPLING_RESOLUTION)
    
    for i in range(len(locations)-1):
        waypoints.extend(grp.trace_route(locations[i], locations[i+1]))
    return waypoints

# Read the path file      
def read_path_file():
    file_path = "../../data/paths/{}.json".format(args.path)
    try:
        with open(file_path) as file:
            data = json.load(file)
            locations = []
            for loc in data["path_checkpoints"]:
                locations.append(carla.Location(x=float(loc["x"]), y=float(loc["y"]), z=float(loc["z"])))
            return locations, data["town"]
    except Exception as e:
        print("Could not read the file {}".format(args.path))
    
# Retrieve road elements from the OpenDRIVE file
def get_road_elements(map):
        path_to_file = "../../data/maps/opendrive_format/{}.xodr".format(map)
        tree = ET.parse(path_to_file)
        root = tree.getroot()
        
        # Get all road elements from the XML
        roads = []
        for road in root.findall("./road"):
            roads.append(road)
        return roads

# Get total distance of all waypoints
def get_total_distance(waypoints):
    total_distance = 0
    for i in range(len(waypoints)-1):
        distance = waypoints[i][0].transform.location.distance(waypoints[i+1][0].transform.location)
        total_distance += distance
    return total_distance

# Calculate the intensity and retrieve the difficulty
def analyse_scenario(total_number_of_spawn_points):
    file_path = "../../data/scenario_generation_data/generated_scenarios/{}.json".format(args.scenario)
    try:
        with open(file_path) as file:
            data = json.load(file)
            total_vehicle_amount = int(data["number_of_vehicles"]) + int(data["number_of_two_wheel_vehicles"])
            # Assume that at most 80% of the spawn points are viable since if we were to put cars into all of them, it would result in the biggest gridlock in the history of simulations
            possible_spawn_point_amount = int(0.8 * total_number_of_spawn_points)
            intensity = total_vehicle_amount / possible_spawn_point_amount
            if intensity > 1: intensity = 1
            
            return int(data["difficulty"]), intensity
    except Exception as e:
        print("Could not read the file {}".format(file_path))
     
# Calculate the average speed of all waypoints and also return how many road elements do not have the speed specified at all
def get_average_speed(waypoints, roads):
    road_speed, how_many_elements_have_no_max_speed_specified = get_road_speed_dictionary(roads)
    average_speed = 0
    speed_limits = []
    
    for waypoint in waypoints:
        id = waypoint[0].road_id
        if waypoint[0].road_id is not None and id in road_speed:
            speed_limits.append(road_speed[waypoint[0].road_id])
        
    if len(speed_limits) > 0:
        average_speed = sum(speed_limits) / len(speed_limits) 
    
    return average_speed, how_many_elements_have_no_max_speed_specified

# Create a dictionary of road_id ---> max allowed speed
def get_road_speed_dictionary(roads):
    speed_dict = {}
    i = 0
    for road in roads:
        id = int(road.get('id'))
        type = road.find('type')
        speed_elem = None
        
        if type is not None:
            speed_elem = type.find('speed')
            
        if speed_elem is None:
            # The standard speed --> 50km/h converted to m/s
            i += 1
            speed_dict[id] = float(50 / 3.6)
        else:
            unit = speed_elem.get('unit')
            value = float(speed_elem.get('max'))
            if unit == 'mph':
                speed_dict[id] = value * 1.60934 / 3.6
            else:
                speed_dict[id] = value / 3.6
    
    return speed_dict, i
    
# For now count how many junctions there are and for each assign a time value
def get_stops(waypoints):
    stops = []
    junctions = 0
    last_waypoint = "road"
    for waypoint in waypoints:
        if waypoint[0].is_junction:
            if last_waypoint == "road":
                junctions += 1
                last_waypoint = "junction"
        else:
            if last_waypoint == "junction":
                last_waypoint = "road"
                
    for i in range (junctions):
        stops.append({
            'name': "Junction",
            'time': 12
        })
    return stops


# Save scenario to file
def write_to_file(obj):
    with open("../../data/simulation_details/{}.json".format(args.scenario), "w+") as f:
        json.dump(obj, f, indent = 4)
    
        
# Used to analyse the path and the scenario to retireve important data needed to evaluate the performance of the participants
def main():
    try:
        client = carla.Client("localhost", 2000)
        client.set_timeout(10)
        locations, map_name = read_path_file()

        # Change the map to get the map element
        world = client.load_world(map_name)
        map = world.get_map()
        
        waypoints = get_route(map, locations)
        roads = get_road_elements(map_name)
        
        total_distance = get_total_distance(waypoints)
        difficulty, intensity = analyse_scenario(len(map.get_spawn_points()))
        average_speed, how_many_elements_have_no_max_speed_specified = get_average_speed(waypoints, roads)
        
        stops = get_stops(waypoints)
        
        final_obj = {
            "path": args.path,
            "scenario": args.scenario,
            "difficulty": float('%.3f' % difficulty),
            "intensity": float('%.3f' % intensity),
            "distance": float('%.3f' % total_distance),
            "average_speed": float('%.3f' % average_speed),
            "stops": stops
        }
        
        write_to_file(final_obj)
        
        # Uncomment to see how (not) wll the OpenDRIVE maps in carla are specified
        # print("")
        # print("In {} only {}% of all road elements have speed values specified".format(map_name, ('%.2f' % (100 - how_many_elements_have_no_max_speed_specified / len(roads) * 100))))
        # print("")
        print("Successfully analysed and save data to data/scenario_details/{}.json file".format(args.scenario))
    except Exception as e:
        print("Something has gone wrong.", e)
       
if __name__ == '__main__':
    main()