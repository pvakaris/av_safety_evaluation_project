import glob
import os
import sys
import time
import random

from agents.navigation.behavior_agent import BehaviorAgent, BasicAgent

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

# Used to print the bounding box of the "hero" vehicle
def main():
    client = carla.Client("localhost", 2000)
    client.set_timeout(10)
    world = client.get_world()
    try:
        # Get the player
        player = None
        actors = world.get_actors()
        for actor in actors:
            if actor.attributes.get('role_name') == 'hero':
                player = actor
        
        box = player.bounding_box.extent
        print("The bounding box (x, y, z):")
        print(box.x)
        print(box.y)
        print(str(box.z) + "\n")
    except Exception as e:
        print("Something wrong happened trying to get the bounding box of the actor named hero:", e)
    
if __name__ == '__main__':
    main()