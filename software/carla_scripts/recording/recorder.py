import glob
import os
import sys

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

import argparse
import random
import time
import logging

import logging
logger = logging.getLogger(__name__)

class Recorder():
    
    def __init__(self, participant_name, scenario_name):
        self.client = carla.Client('127.0.0.1', 2000)
        self.participant_name = participant_name
        self.scenario_name = scenario_name
    
    def start_recording(self):
        try:
            path = '{}_{}_recording.log'.format(self.participant_name, self.scenario_name)
            self.client.start_recorder(path, True)
            logger.info("Successfully started recording the simultion to {}".format(path))
        except Exception as e:
            logger.error("An exception occurred trying to start recording", e)
        
    def stop_recording(self):
        try:
            self.client.stop_recorder()
            logger.info("Stopped the recorder. The recording log file can be found in CarlaUE4/Saved/")
        except Exception as e:
            logger.error("Could not stop the recorder", e)