import argparse
from classes.parsing import Parser
import json

parameters_file = "analysis_parameters.json"

argparser = argparse.ArgumentParser(description=__doc__)
argparser.add_argument(
    '--save_location', '-s',
    required=True,
    help='Where to save the analysis')
args = argparser.parse_args()

def main():
    try:
        parameters = read_parameters()
        parser = Parser(parameters, args.save_location)
        try:
            parser.parse()
        except Exception as e:
            print("An exception occured parsing the recording files: ", e)
        try:
            parser.save()
        except Exception as e:
            print("An exception occured saving the analysed data: ", e)
    finally:
        print("Finished analysing.")
          
def read_parameters():
    try:
        with open("analysis_parameters.json", "r") as file:
            parameters = json.load(file)
        return parameters
    except Exception as e:
        print("Something wrong happened trying to get data from {}".format(parameters_file), e)
        
if __name__ == '__main__':
    main()