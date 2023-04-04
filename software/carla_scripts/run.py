import argparse
import json
import os
import shutil
import logging
import random
from simulation_manager import SimulationManager
import subprocess

parser = argparse.ArgumentParser(description="Run all the scenarios for the participant")
parser.add_argument('-n', '--name', default='example', help='Name of the participant')
parser.add_argument(
    '--ai',
    action='store_true',
    help='Is the ai driving?')
args = parser.parse_args()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, filename="../../data/recordings/{}/session_logs.log".format(args.name), filemode="a", format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

scenario_list_file = "scenario_list.json"

# Read the scenario json file and extract all names of the scenarios to run
def get_scenarios():
    try:
        with open(scenario_list_file) as file:
            scenarios = json.load(file)
            logger.info("Successfully extracted scenarios from file {}".format(scenario_list_file))
            return scenarios
    except FileNotFoundError as e:
        logger.error("Scenario list file could not be found.", exc_info=True)
        raise e
    except json.JSONDecodeError as e:
        logger.error("The file {} could not be decoded as JSON".format(scenario_list_file), exc_info=True)
        raise e

# Create a directory in the participant's results directory to store results about the simulation of a particular scenario
def create_directory_for_scenario(scenario_name):
    path = "../../data/recordings/{}/{}".format(args.name, scenario_name)
    if os.path.exists(path):
        shutil.rmtree(path)
    try:
        os.makedirs(path)
    except OSError:
        logger.error("Could not create a directory for scenario {} for participant {}".format(scenario_name, args.name))
        raise Exception
    logger.info("Successfully created a directory for scenario {}".format(scenario_name))

def try_to_get_name_for_new_scenario():
    path = "../../data/scenario_generation_data/generated_scenarios/"
    i = 0
    # Try to find a name for a new scenario file for a 1000000 times
    while i < 1000000:
        name = "scenario{}".format(i)
        path = os.path.join(path, name)
        if not os.path.exists("{}.json".format(path)):
            return name
        i += 1
    raise Exception("Could not find an unoccupied name for the new scenario. Most likely names scenario[1-1000000] are taken")

def check_scenario(scenario):
    if scenario["name"] is not None:
        return scenario["name"]
    else:
        logger.info("The scenario name was null. Predicting a new scenario.")
        # Generate a new scenario and give it a name and return it
        try:
            name = try_to_get_name_for_new_scenario()
            difficulty = random.randint(1, 1000)
            logger.info("Scenario generator will now try to create a new scenario named {} of difficulty {}".format(name, difficulty))
            # Launch the first person driving mode    
        except Exception as e:
            logger.error("The scenario file was not specified and also a new one could not be created", exc_info=True)
            raise e
        
        try:
            logger.info("Launching create_scenario.py script.")
            # python3: can't open file '../software/generating_scenarios/create_scenario.py'
            process = subprocess.run(["python3", "../../software/generating_scenarios/create_scenario.py", "-d{}".format(difficulty), "-f{}".format(name)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # Uncomment to print to the terminal
            # print(process.stdout.decode(), process.stderr.decode())
            logger.info("Successfully generated a new scenario {}".format(name))
            return name
        except Exception as e:
            logger.error("Could not open the driver.py script", exc_info=True)
            raise e

current_simulation_manager = None

# Launch a simulation manager for the scenario
def launch_scenario(scenario):
    name = check_scenario(scenario)
    create_directory_for_scenario(name)
    global current_simulation_manager
    current_simulation_manager = SimulationManager(name, scenario["details"], args.name, scenario["vehicle"], scenario["randomization_seed"], args.ai)
    current_simulation_manager.begin_simulation()
    

# The main script
def main(agrs):
    logger.info("THE SIMULATIONS BEGIN NOW")
    failed_scenarios = []
    try:
        data = get_scenarios()
        for scenario in data["scenarios"]:
            try:
                logger.info("Starting to work on scenario {}".format(scenario["name"]))
                launch_scenario(scenario)
            except Exception as e:
                failed_scenarios.append(scenario["name"])
                logger.error("Failed to simulate the scenario {}".format(scenario), exc_info=True)
                
        # The end of all the simulations        
        logger.info("Successfully completed {} out of {} simulations".format((len(data["scenarios"])-len(failed_scenarios)), len(data["scenarios"])))
        if len(failed_scenarios) > 0:
            logger.warning("The failed scenarios are:")
            for f_s in failed_scenarios:
                logger.warning(f_s)
    except KeyboardInterrupt:
        logger.warning("The simulation was quit manually.")
    except Exception as e:
        logger.error("Something went horribly wrong.", exc_info=True)
    finally:
        global current_simulation_manager
        if current_simulation_manager is not None:
            current_simulation_manager.close_scenario()
        logger.info("Shutting down the simulation.")
        
if __name__ == '__main__':
    main(args)