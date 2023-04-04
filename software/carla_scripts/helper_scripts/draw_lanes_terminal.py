import glob
import os
import sys
import time
import random
import logging
import argparse
import numpy
import json
import base64
import pickle
sys.path.append("..")
from classes.route import Route
from config import *
from agents.navigation.global_route_planner import GlobalRoutePlanner

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

argparser = argparse.ArgumentParser(
        description=__doc__)
argparser.add_argument(
    '-p', '--path',
    metavar='F',
    default="path1",
    help='Path filename (path1)')
args = argparser.parse_args()

# Reads file and extracts locations
def get_route(map):
    waypoints = []
    grp = GlobalRoutePlanner(map, SAMPLING_RESOLUTION)
    locations = read_path_file()
    
    for i in range(len(locations)-1):
        waypoints.extend(grp.trace_route(locations[i], locations[i+1]))
    return Route(waypoints)
            
def read_path_file():
    file_path = "../../../data/paths/{}.json".format(args.path)
    try:
        with open(file_path) as file:
            data = json.load(file)
            locations = []
            for loc in data["path_checkpoints"]:
                locations.append(carla.Location(x=float(loc["x"]), y=float(loc["y"]), z=float(loc["z"])))
            return locations
    except Exception as e:
        print("Could not read the file {}".format(args.path))
        
        
# Used to draw the specified path on the current map
def main():
    client = carla.Client("localhost", 2000)
    client.set_timeout(10)
    world = client.get_world()
    map = world.get_map()
    

    route = get_route(map)
    try:
        print("Started drawing {}.".format(args.path))
        finished = False
        all_waypoints = route.get_all_waypoints()
        start_color = carla.Color(r=0, g=0, b=255)
        finish_color = carla.Color(r=255, g=0, b=0)
        num_waypoints = len(all_waypoints)
        while(not finished):
            
            # Draw lanes that can be driven
            for i, waypoint in enumerate(all_waypoints): 
                color_progress = float(i) / (num_waypoints - 1)
                
                r = (finish_color.r - start_color.r) / (num_waypoints - 1)
                g = (finish_color.g - start_color.g) / (num_waypoints - 1)
                b = (finish_color.b - start_color.b) / (num_waypoints - 1)
                color = carla.Color(
                    r = int(start_color.r + i * r),
                    g = int(start_color.g + i * g),
                    b = int(start_color.b + i * b)
                )
                world.debug.draw_string(waypoint.transform.location, 'o', draw_shadow=False,color=color, life_time=10,persistent_lines=True)
                
            time.sleep(9)
    except KeyboardInterrupt:
        print("Stopped drawing the path.")
    except Exception as e:
        print("Something wrong happened trying to draw the path. Aborting...", e)
       
if __name__ == '__main__':
    main()