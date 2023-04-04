import logging
import xml.etree.ElementTree as ET
import os
import random
import json

logger = logging.getLogger(__name__)
# How many times to try and recreate the path if it keeps on failing or reaching a dead-end before 
MAX_SEARCH_LENGTH = 10000
path_to_save_path = "../../data/paths/"

class PathBuilder():
    
    @staticmethod
    # Used to find the path, the map and the start location automatically
    def generate_details(scenario_data, save_filename = None):
        try:
            map, road_elements = PathBuilder.find_map_and_path(scenario_data)
        except Exception as e:
            logger.exception("Something went wrong generating the path", e)
            raise Exception
        try:
            start_location = PathBuilder.find_start_location(road_elements[0])
            path_details = PathBuilder.form_json(map, road_elements, start_location, save_filename)
            logger.info(path_details)
            if save_filename:
                logger.info("Path was saved to file {}.json in paths directory amongst other data".format(save_filename))
            return path_details
        except Exception as e:
            logger.exception("Something went wrong combining the path object", e)
            raise Exception
    
    @staticmethod
    # Used to return the newly generated path and everything in a json-like python structure
    # And save it, if the save filename is specified
    def form_json(map, road_elements, start_location, save_filename):
        # Build a json-like file
        # Save if needed and return
        locations = []
        for i in range(len(road_elements)):
            if(i == len(road_elements)-1):
                locations.append(PathBuilder.get_road_location_object(road_elements[i], finish_road=True))
            else:
                locations.append(PathBuilder.get_road_location_object(road_elements[i]))
        attributes = {
            "path_checkpoints": locations,
            "start_location": start_location,
            "town": map.replace(".xodr", "")
        }
        if save_filename:
            with open("{}{}.json".format(path_to_save_path, save_filename), "w+") as f:
                json.dump(attributes, f, indent=4)
        return attributes
    
    @staticmethod
    # Used to find and return a start location among the given path_checkpoints
    def find_start_location(road_element):
        return PathBuilder.get_road_location_object(road_element, yaw=True)
    
    
    @staticmethod
    # Extract the location from the road object
    def get_road_location_object(road, finish_road = None, yaw = None):
        geometries = road.find("planView").findall("geometry")
        geometry = geometries[len(geometries)-1] if finish_road else geometries[0]
        x = float(geometry.attrib["x"])
        y = float(geometry.attrib["y"])
        rotation = float(geometry.attrib["hdg"])
        # Determine z according to the height in that place
        # yaw determine from the road_element
        z = 0.4
        start_location = {
            "x": x,
            "y": y,
            "z": z,
            "yaw": rotation
        }
        return start_location
    
    @staticmethod
    # Used to find the appropriate city
    def find_map_and_path(parameters):
        # Look for an appropriate map iterating through all files in maps/opendrive_format drirectory
        logger.info("Looking for a map that could be used in the scenario and that satisfies the scenario parameters.")
        map_filenames = os.listdir("../../data/maps/opendrive_format")
        already_considered_maps = []
        for i in range(len(map_filenames)):
            # Loop through all mapfiles randomly and if the match is found, return
            unconsidered_maps = [file for file in map_filenames if file not in already_considered_maps and file.endswith(".xodr")]
            random_map = random.sample(unconsidered_maps, 1)[0]
            processed_map = PathBuilder.process_map(random_map, parameters)
            if processed_map:
                return random_map, processed_map
            else:
                logger.warning("The algorithm was unable to find a path given the scenario parameters in the map {}".format(random_map))
                already_considered_maps.append(random_map)
                if i == (len(map_filenames)-1):
                    logger.warning("The search was exhausted and no valid path was found for the given scenario and all the map files. RETURNING NONE.")
        # If this place was reached, it is impossible to create a map
        return None
    
    @staticmethod
    # Process the map file to check if it is appropriate for this scenario
    def process_map(filename, parameters):
        logger.info("Checking if {} is a valid map for this scenario".format(filename))
        path_to_file = "../../data/maps/opendrive_format/{}".format(filename)
        tree = ET.parse(path_to_file)
        root = tree.getroot()
        
        # Get all road and junction elements from the XML
        roads = []
        junctions = []
        for road in root.findall("./road"):
            roads.append(road)
        for junction in root.findall("./junction"):
            junctions.append(junction)
            
        verified = PathBuilder.check_if_parameters_are_satisfied(parameters, roads, junctions, filename)
        if not verified: return None
        
        ## MAKE PATH
        #print("Working on map: {}".format(filename))
        logger.info("Working on map: {}".format(filename))
        return PathBuilder.make_path(roads, junctions, parameters)
        
        
    @staticmethod
    # Checks if the scenario parameters are satisfied in the map
    def check_if_parameters_are_satisfied(parameters, roads, junctions, filename):
        # Check if there are enough junctions in the map
        if len(junctions) >= parameters["number_of_junctions"]:
            logger.info("Junction parameter is satisfied")
        else:
            logger.warning("There are not enough junctions in {} to accomodate the scenario.".format(filename))
            return None
        
        # Check if there is distance requirement is satisfied
        total_road_length = 0.0
        for road in roads:
            total_road_length += float(road.attrib["length"])
        if total_road_length >= float(parameters["distance_in_metres"]):
            logger.info("Distance parameter is satisfied")
        else:
            logger.warning("There is not enough unique drivable road to accomodate the scenario {}".format(filename))
            return None
        return True
    
    @staticmethod
    # Used to run iteration and try to create a path from the given road and junction objects
    def make_path(roads, junctions, parameters):
        go = True
        i = 0
        path = None
        # Try to create a path for a MAX_SEARCH_LENGTH times
        while(go and i < MAX_SEARCH_LENGTH):
            temp = None
            try:
                temp = PathBuilder.get_path(roads, junctions, parameters["number_of_junctions"], parameters["distance_in_metres"])
            except Exception as e:
                logger.warning("Something went weong trying to create the path. Retrying.")
            if temp:
                logger.info("The path was successfully generated")
                go = False
                path = temp
            i += 1
        if not path:
            logger.warning("No success in {} tries to create a path".format(MAX_SEARCH_LENGTH))
            # print("No success in {} tries...".format(i))    
        return path
    
    @staticmethod
    # Used to generate a random path over the map
    def get_path(roads, junctions, max_number_of_junctions_allowed, min_distance):
        path = []
        chosen_road_queue = []
        current_road = random.choice(roads)
        path.append(current_road)
        id, length, predecessor, successor = PathBuilder.analyse_road_element(current_road)
        chosen_road_queue.append(id)
        # print("Id of the first one: {}".format(id))
        current_junctions = 0
        current_length = length
        while current_length < min_distance and current_junctions < max_number_of_junctions_allowed:
            if len(chosen_road_queue) > 7 and chosen_road_queue[-8:].count(id) >= 3:
                # Check if the same road id appeared among the last 8 roads chosen
                # It means that the algorithm got stuck and now is moving back and forth
                return None
            # print("Current length: {}".format(current_length))
            # print("Already used roads: {}".format(chosen_road_queue))
            if successor[0] == "junction":
                # print("Junction approached. Its id is: {}".format(successor[1]))
                current_junctions += 1
                junction = PathBuilder.get_the_right_junction(junctions, successor[1])
                all_exits = PathBuilder.analyse_junction_and_get_possible_exits(junction, id, chosen_road_queue)
                # If a dead-end was reached (no more exits)
                if len(all_exits) == 0:
                    # Return a failure, because a dead-end was reached
                    return None
                # print("All possible exits from this are: {}".format(all_exits))
                random_exit = random.choice(all_exits)
                new_road_to_take = PathBuilder.get_the_right_road(roads, random_exit)
                id, length, predecessor, successor = PathBuilder.analyse_road_element(new_road_to_take)
                # print("The chosen way is: {}".format(id))
                current_length += length
                chosen_road_queue.append(id)
            else:
                new_road_to_take = PathBuilder.get_the_right_road(roads, successor[1])
                id, length, predecessor, successor = PathBuilder.analyse_road_element(new_road_to_take)
                # print("The chosen way is: {}".format(id))
                current_length += length
                chosen_road_queue.append(id)
                path.append(new_road_to_take)
            # print("\n")
        
        return path
                
    
    @staticmethod
    # Used to parse the xml road element and retrieve useful data
    def analyse_road_element(road):
        id = road.attrib["id"]
        length = float(road.attrib["length"])
        link = road.findall("link")[0]
        predecessor = (link.find("predecessor").attrib["elementType"], link.find("predecessor").attrib["elementId"])
        successor = (link.find("successor").attrib["elementType"], link.find("successor").attrib["elementId"])
        return id, length, predecessor, successor
    
    @staticmethod
    # Used to 
    def analyse_junction_and_get_possible_exits(junction, incoming_road_id, already_used_ids):
        # First try to get new roads to drive on
        possible_next_roads = []
        id = junction.attrib["id"]
        for connection in junction.findall("connection"):
            if connection.attrib["incomingRoad"] == incoming_road_id and connection.attrib["connectingRoad"] not in already_used_ids:
                possible_next_roads.append(connection.attrib["connectingRoad"])
        
        # If there are no unique roads, allow picking of old ones
        if len(possible_next_roads) == 0:
            for connection in junction.findall("connection"):
                if connection.attrib["incomingRoad"] == incoming_road_id:
                    possible_next_roads.append(connection.attrib["connectingRoad"])
        # print("Possible next moves: ".format(possible_next_roads))
        return possible_next_roads
    
    @staticmethod
    # Used to find the right junction object from all junctions using its id
    def get_the_right_junction(junctions, id):
        for junction in junctions:
            if junction.attrib["id"] == id:
                return junction
        return None
    
    @staticmethod
    # Used to find the right road object from all road objects using its id
    def get_the_right_road(roads, id):
        for road in roads:
            if road.attrib["id"] == id:
                return road
        return None
        
                