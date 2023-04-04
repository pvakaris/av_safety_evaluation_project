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

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, filename="log.log", filemode="a", format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

argparser = argparse.ArgumentParser(description=__doc__)
argparser.add_argument(
    '-n', '--name',
    default='scenario1',
    help='Specify the name of the scenario')
argparser.add_argument(
    '--log',
    action='store_true',
    help='Activate logging')
args = argparser.parse_args()

# Logging is used only when maps are changed during the simulations (logged to the participant's directory)
if args.log:
    logging.basicConfig(level=logging.INFO, filename='/recording/recordings/{}/session_logs.log'.format(args.name), filemode="a", format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger("ChangeWeather")

# Log INFO message
def inform(message):
    logger.info(message) if args.log else print(message)

def main():
    try:
        inform("Changing the weather for {}.".format(args.name))
        if args.name == "scenario1":
            pass
        else:
            pass
        inform("Finished changing the weather")
    except KeyboardInterrupt:
        message = "Manually exited the weather changing script."
        logger.warn(message) if args.log else print(message)
    except:
        message = "Something wrong happened trying to change the weather. Aborting..."
        logger.exception(message) if args.log else print(message)
        
    
if __name__ == '__main__':
    main()