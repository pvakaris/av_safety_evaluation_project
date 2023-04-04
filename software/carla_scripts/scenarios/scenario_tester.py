import glob
import os
import sys
import argparse
import argparse

try:
    sys.path.append('..')
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla
from scenarios import ScenarioOne

argparser = argparse.ArgumentParser(description=__doc__)
argparser.add_argument(
    '-n', '--name',
    default='scenario1',
    help='Specify the name of the scenario')
args = argparser.parse_args()

# When a new scenario needs to be simulated
# Its subclass has to be imported and used in this function to retrieve it in the main
def get_scenario(traffic_manager, sim_world):
    if(args.name == "scenario1"):
        return ScenarioOne(traffic_manager, sim_world)
    else:
        return ScenarioOne(traffic_manager, sim_world)

# Used to run and test if the scenario is working as expected
# Spawns all the actors, runs them and then destroys
def main():
    try:
        print("Beginning to simulate {}".format(args.name))
        client = carla.Client('localhost', 2000)
        client.set_timeout(20.0)
        sim_world = client.get_world()
        original_settings = sim_world.get_settings()
        settings = sim_world.get_settings()
        if not settings.synchronous_mode:
            settings.synchronous_mode = True
            settings.fixed_delta_seconds = 0.05
        sim_world.apply_settings(settings)

        traffic_manager = client.get_trafficmanager()
        traffic_manager.set_synchronous_mode(True)
        scenario  = get_scenario(traffic_manager, sim_world)
        scenario.spawn(client)
        scenario.start()
        while True:
            sim_world.tick()
    except KeyboardInterrupt:
        print("Finished simulating the scenario.")
    except:
        print("Something wrong happened trying to simulate the scenario.")
    finally:
        scenario.finish(client)
        sim_world.apply_settings(original_settings)
    
if __name__ == '__main__':
    main()