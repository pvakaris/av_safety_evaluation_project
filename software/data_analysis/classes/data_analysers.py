import os
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString

# DataAnalysers are used to parse data from files according to their type and then save it to analysed data files
class DataAnalyser:
    def __init__(self, scenarios, participants):
        self.path_to_recordings = '../../data/recordings/'
        self.scenarios = scenarios
        self.participants = participants
        
        # A list of pairs: (participant, score_on_all_scenarios)
        self.participant_score = {participant: 0.0 for participant in participants}
        
        # A list of pairs: (scenario, score_of_all_participants)
        self.scenario_score = {scenario: 0.0 for scenario in scenarios}
        
        # A list of pairs: (scenario, interesting points of all participants)
        self.scenario_points = {scenario: [] for scenario in scenarios}
    
    # This method goes through the recording files and processes files that are relevant    
    def analyse_files(self, xml_category):
        try:
            # First it looks for a directory for each participant according to the participants specified
            # in the analysis.parameters.json
            for participant in self.participants:
                participant_directories = os.listdir(self.path_to_recordings)
                if participant in participant_directories:
                    item_path = os.path.join(self.path_to_recordings, participant)
                    if os.path.isdir(item_path):
                        # Then it looks for a directory for each scenario specified in the analysis.parameters.json
                        for scenario in self.scenarios:
                            scenario_directories = os.listdir(item_path)
                            if scenario in scenario_directories:
                                path = os.path.join(item_path, scenario, "{}.xml".format(self.category))
                                # And then it looks for a file according to the analysers category
                                # If one is found, it is processed
                                if os.path.isfile(path):
                                    try:
                                        self.process_file(path, scenario, participant, xml_category)   
                                    except Exception as e:
                                        print("An exception occured trying to process file {}:".format(path), e)            
        except Exception as e:
            print("An exception occured trying to gather data from recording files:", e)
    
    # Used to process a single file
    def process_file(self, path_to_file, scenario_name, participant_name, xml_category):
        tree = ET.parse(path_to_file)
        root = tree.getroot()
        if self.category == "route_data":
            penalty_points_total = root.find("ProportionOfRouteCompleted").text
            location_data = []
            for instance in root.findall("{}/Instance".format(xml_category)):
                if instance.find("WasReached").text == "0":
                    x = instance.find("Location").find("X").text
                    y = instance.find("Location").find("Y").text
                    location_data.append((x, y))
        else:
            penalty_points_total = root.find("PenaltyPointsTotal").text
            location_data = []
            for instance in root.findall("{}/Instance/Location".format(xml_category)):
                x = instance.find("X").text
                y = instance.find("Y").text
                location_data.append((x, y))
        
        self.scenario_points[scenario_name].extend(location_data)
        self.scenario_score[scenario_name] += float(penalty_points_total)
        self.participant_score[participant_name] += float(penalty_points_total)
    
    # Used to write all gathered point to the points directory.
    def save_points(self, path):
        try:
            for scenario, points_list in self.scenario_points.items():
                root = ET.Element("Points")
                for x, y in points_list:
                    point = ET.SubElement(root, "Point")
                    ET.SubElement(point, "X").text = str(x)
                    ET.SubElement(point, "Y").text = str(y)
                    
                xml_str = ET.tostring(root, 'utf-8', method='xml')
                xml_formatted = parseString(xml_str).toprettyxml(indent="  ")
                
                with open("{}/{}_{}.xml".format(path, scenario, self.category), "w+") as file_writer:
                    file_writer.write(xml_formatted)
        except IOError as e:
            print("An error occured trying to save points of {}:".format(self.category), e)
        except Exception as e:
            print("Something wrong happened trying to save participants analytics:", e)
            
    # Run the data analyser
    def run(self):
        self.process_data()
    
    # Abstract method
    def process_data(self):
        raise NotImplemented("The method being called is abstract")
    
    

# Different data analysers that look for different metrics
class CollisionDataAnalyser(DataAnalyser):
    def __init__(self, scenarios, participants):
        self.category = "collision_data"
        self.save_file_xml_element_name_average = "CollisionPenaltyPointsAverage"
        super().__init__(scenarios, participants)
        
    def process_data(self):
        self.analyse_files("CollisionInstances")


class VehicleLightDataAnalyser(DataAnalyser):
    def __init__(self, scenarios, participants):
        self.category = "vehicle_light_misuse_data"
        self.save_file_xml_element_name_average = "VehicleLightMisusePenaltyPointsAverage"
        super().__init__(scenarios, participants)
    
    def process_data(self):
        self.analyse_files("VehicleLightsMisuseInstances")
    
class RouteDataAnalyser(DataAnalyser):
    def __init__(self, scenarios, participants):
        self.category = "route_data"
        self.save_file_xml_element_name_average = "ProportionOfRouteCompletedAverage"
        super().__init__(scenarios, participants)
    
    def process_data(self):
        self.analyse_files("Waypoints")
    

class LaneMarkingDataAnalyser(DataAnalyser):
    def __init__(self, scenarios, participants):
        self.category = "lane_marking_violation_data"
        self.save_file_xml_element_name_average = "LaneMarkingViolationPenaltyPointsAverage"
        super().__init__(scenarios, participants)
    
    def process_data(self):
        self.analyse_files("LaneMarkingViolationInstances")
    
    
class SpeedingDataAnalyser(DataAnalyser):
    def __init__(self, scenarios, participants):
        self.category = "speeding_data"
        self.save_file_xml_element_name_average = "SpeedingPenaltyPointsAverage"
        super().__init__(scenarios, participants)
    
    def process_data(self):
        self.analyse_files("SpeedingInstances")
    
    
class RoadTrafficDataAnalyser(DataAnalyser):
    def __init__(self, scenarios, participants):
        self.category = "road_traffic_violation_data"
        self.save_file_xml_element_name_average = "RoadTrafficViolationPenaltyPointsAverage"
        super().__init__(scenarios, participants)
    
    def process_data(self):
        self.analyse_files("RoadTrafficViolationInstances")