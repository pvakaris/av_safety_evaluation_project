import carla
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
from classes.route import Route
from agents.navigation.global_route_planner import GlobalRoutePlanner
from config import SAMPLING_RESOLUTION
import json

import logging
logger = logging.getLogger(__name__)

class RouteMonitor():
    def __init__(self, path_locations, map, save_file):
        self.route = self.get_route(path_locations, map)
        self.save_file = save_file
    
    # Takes a location as an argument and checks if it belongs to the route
    def is_on_path(self, location):
        pass
    
    def update(self, location, is_changing_lane):
        self.route.advanced_recalculate(location, is_changing_lane)
        
    def finish_reached(self, player_location):
        if self.route.is_finished(player_location):
            return True
        
    def write_to_file(self, finish_reached, simulation_time):
        root = ET.Element("RouteData")
        ET.SubElement(root, "SimulationTime").text = str('%.3f' % (simulation_time / 1000))+"s"
        ET.SubElement(root, "ProportionOfRouteCompleted").text = str(self.route.get_route_completion())
        ET.SubElement(root, "FinishReached").text = str(finish_reached)
        ET.SubElement(root, "NumberOfWaypoints").text = str(len(self.route.routepoints))
        waypoints = ET.SubElement(root, "Waypoints")
        for routepoint in self.route.routepoints:
            location = routepoint[0][0].transform.location
            entry_xml = ET.SubElement(waypoints, "Instance")
            ET.SubElement(entry_xml, "WasReached").text = str(routepoint[1])
            location_elem = ET.SubElement(entry_xml, "Location")
            ET.SubElement(location_elem, "X").text = str('%.6f' % location.x)
            ET.SubElement(location_elem, "Y").text = str('%.6f' % location.y)
            ET.SubElement(location_elem, "Z").text = str('%.6f' % location.z)
        
        xml_str = ET.tostring(root, 'utf-8', method='xml')
        xml_formatted = parseString(xml_str).toprettyxml(indent="  ")
        try:
            path = "{}route_data.xml".format(self.save_file)
            with open(path, 'w+') as file_writer:
                file_writer.write(xml_formatted)
            logger.info("Route monitor successfully saved recordings to the file {}".format(path))
        except Exception as e:
            logger.error("Route monitor did not save data to the file {}".format(path), e)
        
        
    def get_route(self, path_locations, map):
        waypoints = []
        grp = GlobalRoutePlanner(map, SAMPLING_RESOLUTION)
        locations = self.transform_to_carla_locations(path_locations)
        for i in range(len(locations)-1):
            waypoints.extend(grp.trace_route(locations[i], locations[i+1]))
        return Route(waypoints)
    
    def transform_to_carla_locations(self, path_locations):
        locations = []
        for loc in path_locations:
            locations.append(carla.Location(x=float(loc["x"]), y=float(loc["y"]), z=float(loc["z"])))
        return locations
    
    # WORKS WHERE THERE ARE ONLY TWO LOCATIONS PROVIDED
    #
    #
    # def get_route(self, pathName, map):
    #     grp = GlobalRoutePlanner(map, SAMPLING_RESOLUTION)
    #     locations = self.read_path_file(pathName)
    #     # Define a route
    #     waypoints = grp.trace_route(locations[0], locations[1])
    #     return Route(waypoints)
        
    # def read_path_file(self, pathName):
    #     start = None
    #     finish = None
    #     with open("./paths/{}.txt".format(pathName), "r") as file:
    #         i = 0
    #         for line in file.readlines():
    #             values = [float(j) for j in line.split(',') if j.strip()]
    #             if i == 0:
    #                 start = carla.Location(x=values[0], y=values[1], z=values[2])
    #             else:
    #                 finish = carla.Location(x=values[0], y=values[1], z=values[2])
    #             i+=1
    #     return (start, finish)