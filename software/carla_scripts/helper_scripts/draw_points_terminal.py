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

    locations = read_path_file()
    try:
        finished = False
        while(not finished):
            
            for l in locations[1:]: 
                world.debug.draw_string(l, 'o000o', draw_shadow=False,color=carla.Color(r=0, g=0, b=255), life_time=10,persistent_lines=True)
                
            world.debug.draw_string(locations[0], 'o000o', draw_shadow=False,color=carla.Color(r=255, g=0, b=0), life_time=10,persistent_lines=True)
            time.sleep(5)
    except KeyboardInterrupt:
        print("Stopped drawing the path.")
    except Exception as e:
        print("Something wrong happened trying to draw the path. Aborting...", e)
       
if __name__ == '__main__':
    main()