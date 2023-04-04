import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
from config import SOLID_PENALTY_SPEEDING, SOLID_TEXT, SOLID_PENALTY, DOUBLE_SOLID_PENALTY_SPEEDING, DOUBLE_SOLID_TEXT,DOUBLE_SOLID_PENALTY, BROKEN_NO_TURN_INDICATOR_PENALTY_SPEEDING, BROKEN_NO_TURN_INDICATOR_PENALTY, BROKEN_NO_TURN_INDICATOR_TEXT

import logging
logger = logging.getLogger(__name__)
class LaneMonitor():
    
    def __init__(self, save_file):
        self.save_file = save_file
        self.buffer = []
        self.sum = 0
        
    def add_to_buffer(self, lane_type, timestep, player, is_speeding, turn_indicator_text):
        location = player.get_location()
        steering_angle = player.get_control().steer
        points_message = self.points_given_and_message(lane_type, is_speeding, steering_angle, turn_indicator_text)
        # Add only violations and lleave-out 0 penalty-point entries
        if(points_message and points_message[0] != 0):
            self.sum += points_message[0]
            self.buffer.append({
                'points': points_message[0],
                'message': points_message[1],
                'time': str('%.3f' % (timestep / 1000)) + "s",
                'location': {
                    'x': '%.6f' % location.x,
                    'y': '%.6f' % location.y,
                    'z': '%.6f' % location.z
                }
            })
            
    def write_to_file(self):
        length = len(self.buffer)
        root = ET.Element("LaneMarkingViolationData")
        ET.SubElement(root, "PenaltyPointsTotal").text = str(self.sum)
        ET.SubElement(root, "NumberOfLaneMarkingViolationInstances").text = str(length)
        
        entries = ET.SubElement(root, "LaneMarkingViolationInstances")
        for entry in self.buffer:
            entry_xml = ET.SubElement(entries, "Instance")
            ET.SubElement(entry_xml, "PenaltyPoints").text = str(entry['points'])
            ET.SubElement(entry_xml, "Description").text = entry['message']
            ET.SubElement(entry_xml, "Time").text = str(entry['time'])
            location = ET.SubElement(entry_xml, "Location")
            ET.SubElement(location, "X").text = str(entry['location']['x'])
            ET.SubElement(location, "Y").text = str(entry['location']['y'])
            ET.SubElement(location, "Z").text = str(entry['location']['z'])
        
        xml_str = ET.tostring(root, 'utf-8', method='xml')
        xml_formatted = parseString(xml_str).toprettyxml(indent="  ")
        
        try:
            path = "{}lane_marking_violation_data.xml".format(self.save_file)
            with open(path, 'w+') as file_writer:
                file_writer.write(xml_formatted)
            logger.info("Lane monitor successfully saved recordings to the file {}".format(path))
        except Exception as e:
            logger.error("Lane monitor did not save data to the file {}".format(path), e)
            
    def points_given_and_message(self, lane_type, speeding, steering_angle, turn_indicator_text):
        if lane_type == "Solid":
            if speeding:
                return(SOLID_PENALTY_SPEEDING, SOLID_TEXT + " speeding")
            else:
                return(SOLID_PENALTY, SOLID_TEXT)
        elif lane_type == "SolidSolid":
            if speeding:
                return(DOUBLE_SOLID_PENALTY_SPEEDING, DOUBLE_SOLID_TEXT + " speeding")
            else:
                return(DOUBLE_SOLID_PENALTY, DOUBLE_SOLID_TEXT)
        elif lane_type == "Broken":
            if turn_indicator_text == "Left" and steering_angle <= 0:
                # Turning left legally
                pass
            elif turn_indicator_text == "Right" and steering_angle >= 0:
                # Turning right legally
                pass
            else:
                if speeding:
                    return(BROKEN_NO_TURN_INDICATOR_PENALTY_SPEEDING, BROKEN_NO_TURN_INDICATOR_TEXT + " speeding")
                else:
                    return(BROKEN_NO_TURN_INDICATOR_PENALTY, BROKEN_NO_TURN_INDICATOR_TEXT)
        else:
            return(0, 'None')