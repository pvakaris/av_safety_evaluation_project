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

# Used to print coordinates of the spectator (the one flying in the simulator and observing the world) to the terminal
# Mainly used to assist in scenario designing to know exact coordinates of specific locations
def main():
    client = carla.Client('localhost', 2000)
    client.set_timeout(2.0)
    world = client.get_world()
    try:
        print("Started printing spectator's coordinates.")
        while(True):
            spectator = world.get_spectator().get_transform()
            coordinates_string = "{}, {}, {}  |  x, y, z".format('%.3f' % spectator.location.x, '%.3f' % spectator.location.y, '%.3f' % spectator.location.z)
            print(coordinates_string)
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopped printing coordinates.")
    except:
        print("Something wrong happened trying to print the spectator's coordinates.")
        
        
    
if __name__ == '__main__':
    main()