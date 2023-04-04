from classes.data_analysers import CollisionDataAnalyser, VehicleLightDataAnalyser, RouteDataAnalyser, LaneMarkingDataAnalyser, SpeedingDataAnalyser, RoadTrafficDataAnalyser
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString

# Creates a DataAnalyser gicen the analysis type.
class DataAnalyserFactory:
    @staticmethod
    def create_analyser(analysis_type, scenarios, participants):
        if analysis_type == 'collision_data':
            return CollisionDataAnalyser(scenarios, participants)
        elif analysis_type == 'lane_marking_violation_data':
            return LaneMarkingDataAnalyser(scenarios, participants)
        elif analysis_type == 'vehicle_light_misuse_data':
            return VehicleLightDataAnalyser(scenarios, participants)
        elif analysis_type == 'route_data':
            return RouteDataAnalyser(scenarios, participants)
        elif analysis_type == 'speeding_data':
            return SpeedingDataAnalyser(scenarios, participants)
        elif analysis_type == 'road_traffic_violation_data':
            return RoadTrafficDataAnalyser(scenarios, participants)
        else:
            raise ValueError('Invalid analyser type')
        
# Used to read and process recorded data according to the specification provided
# in analysis_parameters.json
class Parser():
    
    def __init__(self, parameters, save_location):
        self.participants = parameters["participants"]
        self.scenarios = parameters["scenarios"]
        self.metrics = parameters["metrics"]
        self.save_location = '../../data/analysed_data/data/{}'.format(save_location)
        
        try:
            self.analysers = []
            for metric in self.metrics:
                analyser = DataAnalyserFactory.create_analyser(metric, self.scenarios, self.participants)
                self.analysers.append(analyser)
        except Exception as e:
            print("Could not initiate all the analysers correctly", e)
    
    # Make all the DataAnalysers do their analyses
    def parse(self):
        for analyser in self.analysers:
            analyser.run()
    
    # Save the analysed data    
    def save(self):
        try:
            for analyser in self.analysers:
                analyser.save_points(self.save_location + "/points")
            self.save_participants()
            self.save_scenarios()
        except Exception as e:
            print("Something wrong happened trying to save the analysed data:", e)
    
    # Write relevant data to the participants.xml file
    def save_participants(self):
        try:
            root = ET.Element("Participants")
            for participant in self.participants:
                participant_element = ET.SubElement(root, "Participant")
                ET.SubElement(participant_element, "Name").text = str(participant)
                analysis = ET.SubElement(participant_element, "Analysis")
                # For each participant write what each of the analysers calculated
                total_amount_of_points = 0
                for analyser in self.analysers:
                    ET.SubElement(analysis, analyser.save_file_xml_element_name_average).text = str('%.2f' % (analyser.participant_score[participant] / len(self.scenarios)))
                    if analyser.category != "route_data":
                        total_amount_of_points += analyser.participant_score[participant]
                    
                ET.SubElement(participant_element, "TotalNumberOfPenaltyPoints").text = str('%.2f' % total_amount_of_points)
            xml_str = ET.tostring(root, 'utf-8', method='xml')
            xml_formatted = parseString(xml_str).toprettyxml(indent="  ")
            with open("{}/participants.xml".format(self.save_location, participant), "w+") as file_writer:
                file_writer.write(xml_formatted)
        except IOError as e:
            print("An error occured trying to write analytics to participants.xml file:", e)
        except Exception as e:
            print("Something wrong happened trying to save participants analytics:", e)
                
    # Write relevant data to the scenarios.xml file
    def save_scenarios(self):
        try:
            root = ET.Element("Scenarios")
            for scenario in self.scenarios:
                scenario_element = ET.SubElement(root, "Scenario")
                ET.SubElement(scenario_element, "Name").text = str(scenario)
                analysis = ET.SubElement(scenario_element, "Analysis")
                # For each scenario write what each of the analysers calculated
                for analyser in self.analysers:
                    ET.SubElement(analysis, analyser.save_file_xml_element_name_average).text = str('%.2f' % (analyser.scenario_score[scenario] / len(self.participants)))
            # Write to file
            xml_str = ET.tostring(root, 'utf-8', method='xml')
            xml_formatted = parseString(xml_str).toprettyxml(indent="  ")
            with open("{}/scenarios.xml".format(self.save_location, scenario), "w+") as file_writer:
                file_writer.write(xml_formatted)
        except IOError as e:
            print("An error occured trying to write analytics to scenarios.xml file:", e)
        except Exception as e:
            print("Something wrong happened trying to save scenario analytics:", e)
    
    