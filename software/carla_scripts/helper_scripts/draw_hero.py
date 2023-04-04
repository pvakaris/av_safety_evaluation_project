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
    '-l', '--log',
    help='Log path')
args = argparser.parse_args()

logger = None
if args.log:
    logger = logging.getLogger("draw_hero-thread")
    logging.basicConfig(level=logging.INFO, filename=args.log, filemode="a", format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")   
        
# Used to draw the specified path on the current map
def main():
    client = carla.Client("localhost", 2000)
    client.set_timeout(10)
    world = client.get_world()
    
    try:
        message = "Begin marking the player's location in green"
        if logger is not None: logger.info(message)
        else: print(message)
        # Every step
        finished = False
        while(not finished):
            # Get the player
            player = None
            actors = world.get_actors()
            for actor in actors:
                if actor.attributes.get('role_name') == 'hero':
                    player = actor
            if player:
                world.debug.draw_string(player.get_location(), 'O', draw_shadow=False,color=carla.Color(r=0, g=255, b=0), life_time=0.2,persistent_lines=True)
            else:
                time.sleep(2)    
            time.sleep(0.1)
    except KeyboardInterrupt:
        if logger is None: print("Stopped marking the player's location.")
    except Exception as e:
        message = "Something wrong happened trying to mark the player's location. Aborting..."
        if logger is not None: logger.error(message, e)
        else:  print(message)
    finally:
        message = "Stopped drawing lanes."
        if logger is not None: logger.info(message)
        else: print(message)
       
if __name__ == '__main__':
    main()