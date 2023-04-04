import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
from config import LIGHT_SPEEDING_PENALTY, HEAVY_SPEEDING_PENALTY, LIGHT_SPEEDING_TEXT, HEAVY_SPEEDING_TEXT, HEAVY_SPEEDING_THRESHOLD

import logging
logger = logging.getLogger(__name__)
class SpeedingMonitor():
    
    def __init__(self, save_file):
        self.save_file = save_file
        self.buffer = []
        self.sum = 0
        
    def add_to_buffer(self, allowed_speed, player_speed, timestep, location):
        points_message = self.points_given_and_message(allowed_speed, player_speed)
        self.sum += points_message[0]
        self.buffer.append({
            'points': points_message[0],
            'message': points_message[1],
            'allowed_speed': allowed_speed,
            'player_speed': player_speed,
            'time': str('%.3f' % (timestep / 1000)) + "s",
            'location': {
                'x': '%.6f' % location.x,
                'y': '%.6f' % location.y,
                'z': '%.6f' % location.z
            }
        })
        
    def write_to_file(self):
        length = len(self.buffer)
        root = ET.Element("SpeedingData")
        ET.SubElement(root, "PenaltyPointsTotal").text = str(self.sum)
        ET.SubElement(root, "NumberOfSpeedingInstances").text = str(length)
        
        entries = ET.SubElement(root, "SpeedingInstances")
        for entry in self.buffer:
            entry_xml = ET.SubElement(entries, "Instance")
            ET.SubElement(entry_xml, "PenaltyPoints").text = str(entry['points'])
            ET.SubElement(entry_xml, "Description").text = entry['message']
            ET.SubElement(entry_xml, "AllowedSpeed").text = str(entry['allowed_speed'])
            ET.SubElement(entry_xml, "PlayerSpeed").text = str(entry['player_speed'])
            ET.SubElement(entry_xml, "Time").text = str(entry['time'])
            location = ET.SubElement(entry_xml, "Location")
            ET.SubElement(location, "X").text = str(entry['location']['x'])
            ET.SubElement(location, "Y").text = str(entry['location']['y'])
            ET.SubElement(location, "Z").text = str(entry['location']['z'])
        
        xml_str = ET.tostring(root, 'utf-8', method='xml')
        xml_formatted = parseString(xml_str).toprettyxml(indent="  ")
        
        try:
            path = "{}speeding_data.xml".format(self.save_file)
            with open(path, 'w+') as file_writer:
                file_writer.write(xml_formatted)
            logger.info("Speeding monitor successfully saved recordings to the file {}".format(path))
        except Exception as e:
            logger.error("Speeding monitor did not save data to the file {}".format(path), e)
        
    def points_given_and_message(self, allowed_speed, player_speed):
        absolute_value = player_speed - allowed_speed
        if absolute_value <= HEAVY_SPEEDING_THRESHOLD:
            return (LIGHT_SPEEDING_PENALTY, LIGHT_SPEEDING_TEXT)
        else:
            return (HEAVY_SPEEDING_PENALTY, HEAVY_SPEEDING_TEXT)