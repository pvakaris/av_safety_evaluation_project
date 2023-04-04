import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
from config import HIT_PEDESTRIAN_PENALTY_SPEEDING, HIT_PEDESTRIAN_TEXT, HIT_PEDESTRIAN_PENALTY, HIT_VEHICLE_PENALTY_SPEEDING, HIT_VEHICLE_TEXT, HIT_VEHICLE_PENALTY, HIT_BICYCLE_PENALTY_SPEEDING
from config import HIT_BICYCLE_TEXT, HIT_BICYCLE_PENALTY, HIT_ROAD_OBJECT_PENALTY_SPEEDING, HIT_ROAD_OBJECT_TEXT, HIT_ROAD_OBJECT_PENALTY

import logging
logger = logging.getLogger(__name__)
class CollisionMonitor():
    
    def __init__(self, save_file):
        self.save_file = save_file
        self.buffer = []
        self.sum = 0
    
    def add_to_buffer(self, intensity, other_actor, location, timestep, is_speeding):
        points_message = self.points_given_and_message(other_actor.type_id, intensity, is_speeding)
        self.sum += points_message[0]
        self.buffer.append({
            'points': points_message[0],
            'message': points_message[1],
            'intensity': intensity,
            'time': str('%.3f' % (timestep / 1000)) + "s",
            'location': {
                'x': '%.6f' % location.x,
                'y': '%.6f' % location.y,
                'z': '%.6f' % location.z
            }
        })
        
    def write_to_file(self):
        length = len(self.buffer)
        root = ET.Element("CollisionData")
        ET.SubElement(root, "PenaltyPointsTotal").text = str(self.sum)
        ET.SubElement(root, "NumberOfCollisionInstances").text = str(length)
        
        speeding_entries = ET.SubElement(root, "CollisionInstances")
        for entry in self.buffer:
            entry_xml = ET.SubElement(speeding_entries, "Instance")
            ET.SubElement(entry_xml, "PenaltyPoints").text = str(entry['points'])
            ET.SubElement(entry_xml, "Description").text = str(entry['message'])
            ET.SubElement(entry_xml, "CollisionIntensity").text = str(entry['intensity'])
            ET.SubElement(entry_xml, "Time").text = str(entry['time'])
            location = ET.SubElement(entry_xml, "Location")
            ET.SubElement(location, "X").text = str(entry['location']['x'])
            ET.SubElement(location, "Y").text = str(entry['location']['y'])
            ET.SubElement(location, "Z").text = str(entry['location']['z'])
        
        xml_str = ET.tostring(root, 'utf-8', method='xml')
        xml_formatted = parseString(xml_str).toprettyxml(indent="  ")
        try:
            path = "{}collision_data.xml".format(self.save_file)
            with open(path, 'w+') as file_writer:
                file_writer.write(xml_formatted)
            logger.info("Collision monitor successfully saved recordings to the file {}".format(path))
        except Exception as e:
            logger.error("Collision monitor did not save data to the file {}".format(path), e)
    
    def points_given_and_message(self, victim_type, intensity, speeding):
        # Intensity to be used
        if victim_type.startswith("walker"):
            if speeding:
                return(HIT_PEDESTRIAN_PENALTY_SPEEDING, HIT_PEDESTRIAN_TEXT + " speeding")
            else:
                return(HIT_PEDESTRIAN_PENALTY, HIT_PEDESTRIAN_TEXT)
        elif victim_type.startswith("vehicle"):
            if speeding:
                return(HIT_VEHICLE_PENALTY_SPEEDING, HIT_VEHICLE_TEXT + " speeding")
            else:
                return(HIT_VEHICLE_PENALTY, HIT_VEHICLE_TEXT)
        elif victim_type.startswith("bicycle"):
            if speeding:
                return(HIT_BICYCLE_PENALTY_SPEEDING, HIT_BICYCLE_TEXT + " speeding")
            else:
                return(HIT_BICYCLE_PENALTY, HIT_BICYCLE_TEXT)
        else:
            if speeding:
                return(HIT_ROAD_OBJECT_PENALTY_SPEEDING, HIT_ROAD_OBJECT_TEXT + " speeding")
            else:
                return(HIT_ROAD_OBJECT_PENALTY, HIT_ROAD_OBJECT_TEXT)
    
    ### UNUSED
       
    def get_actor_display_name(self, actor, truncate=250):
        name = ' '.join(actor.type_id.replace('_', '.').title().split('.')[1:])
        return (name[:truncate - 1] + u'\u2026') if len(name) > truncate else name       