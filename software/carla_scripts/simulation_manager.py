import json
import logging
import sys
from scenarios.scenario_factory import ScenarioFactory
from scenarios.path_builder import PathBuilder
import glob
import os
import time
import pickle
import subprocess
import base64
from threading import Thread

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla


logger = logging.getLogger(__name__)

class SimulationManager():
    
    def __init__(self, scenario_name, path_name, participant_name, vehicle_blueprint, randomization_seed, ai):
        self.vehicle_blueprint = vehicle_blueprint
        self.scenario_name = scenario_name
        self.path_name = path_name
        self.participant_name = participant_name
        self.ai = ai
        self.seed = randomization_seed
        self.scenario = None
        
    def begin_simulation(self):
        try:
            scenario_data = self.load_scenario()
            path_details = self.determine_path_details(scenario_data)
            self.change_map(path_details["town"])
            self.change_weather(scenario_data)
            self.scenario = ScenarioFactory.make_scenario(scenario_data, path_details, self.seed)
            self.launch_driving_mode(self.scenario, path_details)
            
        except Exception as e: 
            raise e
    
    # Either generate the path or get it from file if such is defined
    def determine_path_details(self, scenario_data):
        if self.path_name:
            details = self.read_path_details()
        else:
            logger.info("No predefined details to load. The details will be generated automatically.")
            details = PathBuilder.generate_details(scenario_data)
        return details
    
    # Read path details to predefine the scenario if the path is specified
    def read_path_details(self):
        logger.info("Loading predefined details for the scenario")
        file_path = "../../data/paths/{}.json".format(self.path_name)
        try:
            with open(file_path) as file:
                details = json.load(file)
                logger.info("Successfully read additional scenario details from {}.json data".format(self.path_name))
                return details
        except FileNotFoundError as e:
            logger.error("Path {} file could not be found.".format(self.path_name), exc_info=True)
            raise e
        except json.JSONDecodeError as e:
            logger.error("The file {}.json could not be decoded as JSON".format(self.path_name), exc_info=True)
            raise e
    
    
    # Get a file indicating scenario parameters
    def load_scenario(self):
        logger.info("Loading {} data".format(self.scenario_name))
        file_path = "../../data/scenario_generation_data/generated_scenarios/{}.json".format(self.scenario_name)
        try:
            with open(file_path) as file:
                scenario_data = json.load(file)
                logger.info("Successfully read scenario {}.json data".format(self.scenario_name))
                return scenario_data
        except FileNotFoundError as e:
            logger.error("Scenario {} file could not be found.".format(self.scenario_name), exc_info=True)
            raise e
        except json.JSONDecodeError as e:
            logger.error("The file {}.json could not be decoded as JSON".format(self.scenario_name), exc_info=True)
            raise e
    
    # Used to kill all the actors in the simulation
    def close_scenario(self):
        client = carla.Client('127.0.0.1', 2000)
        client.set_timeout(20.0)
        if(self.scenario is not None and self.scenario.populated):
            logger.info("The scenario was running. Finishing it.")
            self.scenario.finish(client)

    # Change the weather in the simulation        
    def change_weather(self, scenario_data):
        try:
            logger.info("Changing the weather")
            client = carla.Client('localhost', 2000)
            world = client.get_world()
            weather = carla.WeatherParameters(
                cloudiness = scenario_data["cloudiness"],
                precipitation = scenario_data["precipitation"],
                precipitation_deposits = scenario_data["precipitation_deposits"],
                wind_intensity = scenario_data["wind_intensity"],
                sun_azimuth_angle = scenario_data["sun_azimuth_angle"],
                sun_altitude_angle = scenario_data["sun_altitude_angle"],
                fog_density = scenario_data["fog_density"],
                fog_distance = scenario_data["fog_distance"],
                wetness = scenario_data["wetness"],
                fog_falloff = scenario_data["fog_falloff"],
                scattering_intensity = scenario_data["scattering_intensity"],
                mie_scattering_scale = scenario_data["mie_scattering_scale"],
                rayleigh_scattering_scale = scenario_data["rayleigh_scattering_scale"],
                # dust_storm = scenario_data["dust_storm"],
            )
            
            world.set_weather(weather)
            logger.info("Finished changing the weather")
        except Exception as e:
            logger.error("Something wrong happened trying to change the weather. Aborting...", exc_info=True)
            raise e
    
    # Change the simulation map
    def change_map(self, map):
        try:
            logger.info("Changing the map to {}.".format(map))
            client = carla.Client('localhost', 2000)
            client.set_timeout(10.0)
            world = client.load_world(map)
            # Give 2 sec for the map to load
            time.sleep(2)
            logger.info("Finished changing the map")
        except Exception as e:
            logger.exception("Something wrong happened trying to change the map. Aborting...", exc_info=True)
            raise e
    
    
    # Launch the first person driving mode    
    def launch_driving_mode(self, scenario, path_details):
        scenario_bytes = pickle.dumps(scenario)
        path_bytes = pickle.dumps(path_details)
        
        s_b64 = base64.b64encode(scenario_bytes).decode()
        p_b64 = base64.b64encode(path_bytes).decode()
        try:
            if self.ai:
                logger.info("Launching self_driver.py script as a subprocess to let AI implementation drive the scenarios.")
                process = subprocess.run(["python3", "self_driver.py", s_b64, p_b64, "-n{}".format(self.participant_name), "--sync", "-s{}".format(self.scenario_name), "-f{}".format(self.vehicle_blueprint)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                logger.info("Launching driver.py script as a subprocess to drive the generated scenario.")
                process = subprocess.run(["python3", "driver_keyboard.py", s_b64, p_b64, "-n{}".format(self.participant_name), "--sync", "-s{}".format(self.scenario_name), "-f{}".format(self.vehicle_blueprint)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                # process = subprocess.run(["python3", "driver_steeringwheel.py", s_b64, p_b64, "-n{}".format(self.participant_name), "--sync", "-s{}".format(self.scenario_name), "-f{}".format(self.vehicle_blueprint)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # Uncomment to print statemennts coming from driver.py to the terminal
            # print(process.stdout.decode(), process.stderr.decode())
        except Exception as e:
            logger.error("Could not launch driving script properly", exc_info=True)
            raise e
    
    # # MULTI-THREADING
    
    # # Launch the first person driving mode    
    # def launch_driving_mode(self, scenario, path_details):
    #     try:
    #         flag = [False]
            
    #         threads = [
    #             Thread(target=simulate, args=[scenario, path_details, self.participant_name, self.scenario_name, self.vehicle_blueprint, self.ai, flag]),
    #             Thread(target=draw_lanes, args=[path_details["path_checkpoints"], self.participant_name]),
    #             Thread(target=draw_hero, args=[self.participant_name])
    #         ]
            
    #         for thread in threads:
    #             thread.start()  
                
    #         while True:
    #             time.sleep(1)
    #             if flag[0]:
    #                 for thread in threads:
    #                     thread.join()
    #             break
    #     except Exception as e:
    #         logger.error("Something went wrong when starting the threads.", e)
                       
def simulate(scenario, path_details, participant_name, scenario_name, vehicle_blueprint, ai, flag):
    try:
        scenario_bytes = pickle.dumps(scenario)
        path_bytes = pickle.dumps(path_details)
        
        s_b64 = base64.b64encode(scenario_bytes).decode()
        p_b64 = base64.b64encode(path_bytes).decode()
        if ai:
            logger.info("Launching self_driver.py script as a subprocess to let AI implementation drive the scenarios.")
            simulating = subprocess.Popen(["python3", "self_driver.py", s_b64, p_b64, "-n{}".format(participant_name), "--sync", "-s{}".format(scenario_name), "-f{}".format(vehicle_blueprint)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)         
        else:
            logger.info("Launching driver.py script as a subprocess to drive the generated scenario.")
            simulating = subprocess.Popen(["python3", "driver.py", s_b64, p_b64, "-n{}".format(participant_name), "--sync", "-s{}".format(scenario_name), "-f{}".format(vehicle_blueprint)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  
    except Exception as e:
        logger.error("Could not the simulation", e)

def draw_lanes(locations, participant_name):
    try:
        locations_bytes = pickle.dumps(locations)
        locations_b64 = base64.b64encode(locations_bytes).decode()
        
        log_path = "../../data/recordings/{}/session_logs.log".format(participant_name)
        
        logger.info("Launching draw_lines.py script as a subprocess to mark the lanes and the driver on the map.")
        drawing = subprocess.Popen(["python3", "helper_scripts/draw_lanes.py", locations_b64, "-l{}".format(log_path)])
    except Exception as e:
        logger.error("Could not start drawing lines", e)
        
def draw_hero(participant_name):
    try:
        log_path = "../../data/recordings/{}/session_logs.log".format(participant_name)

        logger.info("Launching draw_hero.py script as a subprocess to mark the location of the participant on the map.")
        drawing = subprocess.Popen(["python3", "helper_scripts/draw_hero.py", "-l{}".format(log_path)])
    except Exception as e:
        logger.error("Could not start hero vehicle", e)