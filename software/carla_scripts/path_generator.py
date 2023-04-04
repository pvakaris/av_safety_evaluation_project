import argparse
import json
import logging
from scenarios.path_builder import PathBuilder

parser = argparse.ArgumentParser(description="Generate path parameters for a given scenario")
parser.add_argument('-s', '--scenario', default='example', help='Name of scenario')
parser.add_argument('-f', '--filename', default='example', help='Filename')
args = parser.parse_args()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, filename="../../data/paths/logs/logs.log", filemode="w", format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Get a file indicating scenario parameters
def load_scenario():
    logger.info("Loading scenario {} data".format(args.scenario))
    file_path = "../../data/scenario_generation_data/generated_scenarios/{}.json".format(args.scenario)
    try:
        with open(file_path) as file:
            scenario_data = json.load(file)
            logger.info("Successfully read scenario {}.json data".format(args.scenario))
            return scenario_data
    except FileNotFoundError as e:
        logger.exception("Scenario {} file could not be found.".format(args.scenario), e)
    except json.JSONDecodeError as e:
        logger.exception("The file {}.json could not be decoded as JSON".format(args.scenario), e)

# The main script
def main(agrs):
    logger.info("Begin path generation")
    try:
        scenario_data = load_scenario()
        path = PathBuilder.generate_details(scenario_data, args.filename)
        if path: print("Generated and saved.")
    except Exception as e:
        logger.fatal("Fatal error. Shutting down the generation.")
        
if __name__ == '__main__':
    main(args)