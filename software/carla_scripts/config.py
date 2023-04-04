# General variables

DISTANCE_FROM_WAYPOINT = 0.7
FINISH_DISTANCE_FROM_WAYPOINT = 3.0
DISTANCE_FROM_WAYPOINT_CHANGING_LANE = 1.0
SAMPLING_RESOLUTION = 0.5
SAMPLING_RESOLUTION_AI = 5
FPS = 60
RANDOMIZATION_SEED = 187349

# Penalty related variables

NO_BEAMS_NO_FOG_LIGHTS = 50
NO_BEAMS_NO_FOG_LIGHTS_TEXT = "Dark and foggy - no lights at all"

NO_BEAMS = 30
NO_BEAMS_TEXT = "Dark - no low beams"

NO_FOG_LIGHTS = 10
NO_FOG_LIGHTS_TEXT = "Dark and foggy - no fog lights"

HIT_PEDESTRIAN_TEXT = "Hit pedestrian"
HIT_PEDESTRIAN_PENALTY = 600
HIT_PEDESTRIAN_PENALTY_SPEEDING = 1200

HIT_VEHICLE_TEXT = "Hit vehicle"
HIT_VEHICLE_PENALTY = 250
HIT_VEHICLE_PENALTY_SPEEDING = 500

HIT_BICYCLE_TEXT = "Hit bicycle"
HIT_BICYCLE_PENALTY = 400
HIT_BICYCLE_PENALTY_SPEEDING = 800

HIT_ROAD_OBJECT_TEXT = "Hit road object"
HIT_ROAD_OBJECT_PENALTY = 150
HIT_ROAD_OBJECT_PENALTY_SPEEDING = 300

RED_LIGHT_TEXT = "Red light"
RED_LIGHT_PENALTY = 50
RED_LIGHT_PENALTY_SPEEDING = 100

SOLID_TEXT = "Solid lane marking"
SOLID_PENALTY = 20
SOLID_PENALTY_SPEEDING = 60

DOUBLE_SOLID_TEXT = "Double solid lane marking"
DOUBLE_SOLID_PENALTY = 40
DOUBLE_SOLID_PENALTY_SPEEDING = 100

BROKEN_NO_TURN_INDICATOR_TEXT = "Broken line wrong or no turn indicator"
BROKEN_NO_TURN_INDICATOR_PENALTY = 10
BROKEN_NO_TURN_INDICATOR_PENALTY_SPEEDING = 30

LIGHT_SPEEDING_PENALTY = 1
LIGHT_SPEEDING_TEXT = "Speeding under 20km/h"

HEAVY_SPEEDING_PENALTY = 3
HEAVY_SPEEDING_TEXT = "Speeding over 20km/h"

# If speeding exceeds this amount, it is considered heavy speeding (50 allowed ---> 71+ is considered heavy speeding)
HEAVY_SPEEDING_THRESHOLD = 20
