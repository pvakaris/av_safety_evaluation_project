from scenarios.scenario import Scenario
import sys
import os
import glob
import logging

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

logger = logging.getLogger(__name__)


class ScenarioFactory():
    
    @staticmethod
    def make_scenario(parameters, path_details, seed):
        logger.info("Creating a scenario according to the generated path and scenario details")
        return Scenario(parameters, path_details, seed)
        