from regressor import Regressor
import argparse

# The purpose of this script is to create new scenario.json file according to the difficulty, wetness amd sun altitude angle
# and save it in the file specified in the arguments
def main():
    parser = argparse.ArgumentParser(description='Create a new scenario based on difficulty.')
    parser.add_argument('--difficulty', '-d', type=float, default='70', help='Difficulty value')
    parser.add_argument('--sun', '-s', type=float, default='68', help='Sun altitude angle')
    parser.add_argument('--wetness', '-w', type=float, default='10', help='Wetness value')
    parser.add_argument('--filename', '-f', type=str, default='example', help='Filename to save the scenario')
    parser.add_argument('--random', '-r', action='store_false', help='Everytime build and train the algortithm differently')
    args = parser.parse_args()
    
    try:
        regressor = Regressor(args.random)
        regressor.create_new_scenario(args.difficulty, args.wetness, args.sun, args.filename)
        print("New scenario was created and save into {}.json file.".format(args.filename))
    except Exception as e:
        print("An error occurred trying to create a new scenario:", str(e))

if __name__ == '__main__':
    main()