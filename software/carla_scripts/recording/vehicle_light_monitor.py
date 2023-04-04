import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
from classes.helpers import pairs, default_match
from config import FPS, NO_BEAMS_NO_FOG_LIGHTS, NO_BEAMS, NO_FOG_LIGHTS, NO_BEAMS_NO_FOG_LIGHTS_TEXT, NO_BEAMS_TEXT, NO_FOG_LIGHTS_TEXT

import logging
logger = logging.getLogger(__name__)
class VehicleLightMonitor():
    
    def __init__(self, save_file):
        self.save_file = save_file
        self.buffer = []
        self.sum = 0
        self.just_wrote = True
        
        self.left_turn_indicator = False
        self.right_turn_indicator = False
        self.fog_lights = False
        self.low_beam = False
        self.high_beam = False
        
    def set_lights(self, code, weather, time, location):
        lights = self.match_lights(code)
        self.left_turn_indicator = lights[0]
        self.right_turn_indicator = lights[1]
        self.low_beam = lights[2]
        self.high_beam = lights[3]
        self.fog_lights = lights[4]
        # Write every 10s
        value = (time/1000) % 10
        if not self.just_wrote and (value > 0 and value <= 0.2):
            data = self.check_lights(weather)
            if(data):
                self.add_to_buffer(data[0], data[1], data[2], data[3], time, location)
            self.just_wrote = True
        elif value > 0.2:
            self.just_wrote = False
        else:
            pass
        
    def check_lights(self, weather):
        sun_altitude_angle = weather.sun_altitude_angle
        fog_density = weather.fog_density
        if(sun_altitude_angle < 30):
            if(fog_density > 50):
                if(not self.fog_lights):
                    if(not self.low_beam):
                        return (NO_BEAMS_NO_FOG_LIGHTS, NO_BEAMS_NO_FOG_LIGHTS_TEXT, sun_altitude_angle, fog_density)
                    else:
                        return (NO_FOG_LIGHTS, NO_FOG_LIGHTS_TEXT, sun_altitude_angle, fog_density)
                else:
                    if(not self.low_beam):
                        return (NO_BEAMS, NO_BEAMS_TEXT, sun_altitude_angle, fog_density)
            else:
                if(not self.low_beam):
                    return (NO_BEAMS, NO_BEAMS_TEXT, sun_altitude_angle, fog_density)
        else:
            if(fog_density > 50):
                if(not self.fog_lights):
                    if(not self.low_beam):
                        return (NO_BEAMS_NO_FOG_LIGHTS, "Foggy - no lights at all", sun_altitude_angle, fog_density)
                    else:
                        return (NO_FOG_LIGHTS, "Foggy - no fog lights", sun_altitude_angle, fog_density)
                else:
                    if(not self.low_beam):
                        return (NO_BEAMS, "Foggy - no low beams", sun_altitude_angle, fog_density)
            else:
                return None   
        
    def turning_left(self):
        return self.left_turn_indicator
    
    def turning_right(self):
        return self.right_turn_indicator
        
    def add_to_buffer(self, points_given, type, sun_altitude_angle, fog_density, timestep, location):
        self.sum += points_given
        self.buffer.append({
            'points': points_given,
            'message': type,
            'sun_altitude_angle': sun_altitude_angle,
            'fog_density': fog_density,
            'time': str('%.3f' % (timestep / 1000)) + "s",
            'location': {
                'x': '%.6f' % location.x,
                'y': '%.6f' % location.y,
                'z': '%.6f' % location.z
            }
        })
        
    def write_to_file(self):
        length = len(self.buffer)
        root = ET.Element("VehicleLightMisuseData")
        ET.SubElement(root, "PenaltyPointsTotal").text = str(self.sum)
        ET.SubElement(root, "NumberOfVehicleLightMisuseInstances").text = str(length)
        
        entries = ET.SubElement(root, "VehicleLightMisuseInstances")
        for entry in self.buffer:
            entry_xml = ET.SubElement(entries, "Instance")
            ET.SubElement(entry_xml, "PenaltyPoints").text = str(entry['points'])
            ET.SubElement(entry_xml, "Description").text = entry['message']
            ET.SubElement(entry_xml, "SunAltitudeAngle").text = str(entry['sun_altitude_angle'])
            ET.SubElement(entry_xml, "FogDensity").text = str(entry['fog_density'])
            ET.SubElement(entry_xml, "Time").text = str(entry['time'])
            location = ET.SubElement(entry_xml, "Location")
            ET.SubElement(location, "X").text = str(entry['location']['x'])
            ET.SubElement(location, "Y").text = str(entry['location']['y'])
            ET.SubElement(location, "Z").text = str(entry['location']['z'])
        
        xml_str = ET.tostring(root, 'utf-8', method='xml')
        xml_formatted = parseString(xml_str).toprettyxml(indent="  ")
        
        try:
            path = "{}vehicle_light_misuse_data.xml".format(self.save_file)
            with open(path, 'w+') as file_writer:
                file_writer.write(xml_formatted)
            logger.info("Vehicle light misuse monitor successfully saved recordings to the file {}".format(path))
        except Exception as e:
            logger.error("Vehicle light misuse monitor did not save data to the file {}".format(path), e)

            
    def match_lights(self, code):
        for pair in pairs:
            if pair[0] == str(code):
                return pair[1]
        return default_match
    
    