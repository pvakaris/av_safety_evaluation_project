import argparse
import json
import xml.etree.ElementTree as ET

# The gamma value
GAMMA = 0.7

metrics =  [
        "collision_data",
        "lane_marking_violation_data",
        "vehicle_light_misuse_data",
        "route_data",
        "speeding_data",
        "road_traffic_violation_data"
    ]

argparser = argparse.ArgumentParser(description=__doc__)
argparser.add_argument(
    '--scenario', '-s',
    help='The simulation to consider')
argparser.add_argument(
    '--name', '-n',
    help='The name of the participant')
args = argparser.parse_args()

# Used to print the final score of the participant to the screen
def main():
    try:
        details = read_details()
        try:
            score, ideal_score = calculate_the_score(details)
            print("The score for {} in {} is: ".format(args.name, args.scenario) + str(score))
            print("The ideal score is: {} and above".format(ideal_score))
        except Exception as e:
            print("An exception occured calculating the score:", e)
    except Exception as e:
        print("Something went wrong...", e)
     
# Function that calculates the final score according to the formula specified in the final report Chapter 7   
def calculate_the_score(details):
    score = 0
    d = details["difficulty"]
    alpha = details["intensity"]
    v_avg = details["average_speed"]
    s = details["distance"]
    c, t, penalty_points = do_route_analysis(args.scenario, args.name)
    time_for_additional_stops = sum([entry["time"] for entry in details["stops"]])
    
    # The final formula in action
    t_o = (s / v_avg) * (1 + alpha) + time_for_additional_stops
    score = (c * (t_o / t) * d) - GAMMA * penalty_points
    return float('%.3f' % score), d

# Sum up all the penalty points
def do_route_analysis(scenario, name):
    penalty_points = 0
    try:
        for metric in metrics:
            tree = ET.parse("../../data/recordings/{}/{}/{}.xml".format(name, scenario, metric))
            root = tree.getroot()
            if metric == "route_data":
                c = float(root.find("ProportionOfRouteCompleted").text)
                t = float(root.find("SimulationTime").text[:-1])
            else:
                penalty_points += float(root.find("PenaltyPointsTotal").text)
    except Exception as e:
        print("An exception occured trying to gather data from recording files:", e)
        
    return c, t, penalty_points

# Read the details of the simulation
def read_details():
    try:
        with open("../../data/simulation_details/{}.json".format(args.scenario), "r") as file:
            details = json.load(file)
        return details
    except Exception as e:
        print("Something wrong happened trying to get data from {}.json".format(args.scenario), e)
        
if __name__ == '__main__':
    if args.name and args.scenario:
        main()
    else:
        "Please make sure that you pass the required arguments -s (scenario name) and -n (participant's name)"