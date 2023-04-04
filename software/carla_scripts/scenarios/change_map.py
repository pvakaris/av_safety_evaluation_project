import glob
import os
import sys
import time
import random
import argparse

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
    '-m', '--map',
    default='Town04',
    help='Specify the name of the map')
argparser.add_argument(
    '--name',
    default="ParticipantA",
    help='Name of the participant')
args = argparser.parse_args()



def main():
    try:
        print("Changing the map to {}.".format(args.map))
        client = carla.Client('localhost', 2000)
        world = client.load_world('{}'.format(args.map))
        time.sleep(10)
        print("Finished changing the map")
    except KeyboardInterrupt:
        message = "Manually exited the weather changing script."
        print(message)
    except Exception as e:
        message = "Something wrong happened trying to change the map. Aborting..."
        print(message)
    
if __name__ == '__main__':
    main()