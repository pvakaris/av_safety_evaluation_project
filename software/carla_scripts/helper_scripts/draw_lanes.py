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
argparser.add_argument(
    '-l', '--log',
    help='Log path')
argparser.add_argument("locations")
args = argparser.parse_args()

logger = None
if args.log:
    logger = logging.getLogger("draw_lanes-thread")
    logging.basicConfig(level=logging.INFO, filename=args.log, filemode="a", format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    
def extract_locations(path_details):
    locations = []
    for loc in path_details:
        locations.append(carla.Location(x=float(loc["x"]), y=float(loc["y"]), z=float(loc["z"])))
    return locations

# Reads file and extracts locations
def get_route(map, details):
    waypoints = []
    grp = GlobalRoutePlanner(map, SAMPLING_RESOLUTION)
    if details is not None: locations = extract_locations(details)
    else: locations = read_path_file
    
    for i in range(len(locations)-1):
        waypoints.extend(grp.trace_route(locations[i], locations[i+1]))
    return Route(waypoints)
            
def read_path_file():
    file_path = "../../data/paths/{}.json".format(args.path)
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
    
    locations = None
    if args.locations:
        locs = args.locations
        locs_decoded = base64.b64decode(locs.encode())
        locations = pickle.loads(locs_decoded)
    route = get_route(map, locations)
    try:
        if logger is not None: logger.info("Started drawing the path")
        else: print("Started drawing {}.".format(args.path))
        # Every step
        finished = False
        while(not finished):
            all_waypoints = route.get_all_waypoints()
            
            # Draw lanes that can be driven
            for waypoint in all_waypoints: 
                world.debug.draw_string(waypoint.transform.location, 'o', draw_shadow=False,color=carla.Color(r=0, g=0, b=255), life_time=10,persistent_lines=True)
                
            # Draw finish line
            for waypoint in route.finish_lane_waypoints: 
                world.debug.draw_string(waypoint.transform.location, 'o', draw_shadow=False,color=carla.Color(r=255, g=0, b=0), life_time=10,persistent_lines=True)
            time.sleep(9)
    except KeyboardInterrupt:
        if logger is None: print("Stopped drawing the path.")
    except Exception as e:
        if logger is not None: logger.error("Something wrong happened trying to draw the path. Aborting...", e)
        else:  print("Something wrong happened trying to draw the path. Aborting...", e)
    finally:
        if logger is not None: logger.info("Stopped drawing lanes.")
       
if __name__ == '__main__':
    main()