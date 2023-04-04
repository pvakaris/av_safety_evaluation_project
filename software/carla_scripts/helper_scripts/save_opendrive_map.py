#!/usr/bin/env python

# Copyright (c) 2019 Computer Vision Center (CVC) at the Universitat Autonoma de
# Barcelona (UAB).
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

import glob
import os
import sys

import carla

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

# Used to save the current map in the simulation to an .xml file
def main():

    try:
        client = carla.Client('127.0.0.1', 2000)
        client.set_timeout(10)
        world = client.get_world()
        map = world.get_map()
        
        name = map.name.rsplit('/', 1)[-1]
        world.get_map().save_to_disk("maps/{}.xml".format(name))

    except Exception as e:
        print("Something wrong happened:", e)
    finally:
        print("Finished")


if __name__ == '__main__':
    main()