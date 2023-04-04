import numpy

# Get distance between start and finish locations
# start and finish are both of type carla.Location
def distanceBetweenTwoLocations(start, finish):
    first = numpy.array((start.x, start.y, start.z))
    second = numpy.array((finish.x, finish.y, finish.z))
    return numpy.linalg.norm(first-second)

# The following list is used to match the vehicle light state and figure out what lights are on
# The first element of the tuple is the "code" that the simualtion returns about the state of car's lights
# The second element is a tuple of five True/False values representing the states of the following
# (LeftBlinker, RightBlinker, LowBeam, HighBeam, FogLights)
pairs = [
        ("NONE",(False, False, False, False, False)),
        # Left
        ("LeftBlinker",(True, False, False, False, False)),
        ("40",(True, False, False, False, False)),
        ("96",(True, False, False, False, False)),
        ("104",(True, False, False, False, False)),
        # Left Position
        ("33",(True, False, False, False, False)),
        ("41",(True, False, False, False, False)),
        ("97",(True, False, False, False, False)),
        ("105",(True, False, False, False, False)),
        # Left Low
        ("99",(True, False, True, False, False)),
        ("107",(True, False, True, False, False)),
        ("35",(True, False, True, False, False)),
        ("43",(True, False, True, False, False)),
        # Left Fog
        ("227",(True, False, True, False, True)),
        ("235",(True, False, True, False, True)),
        ("163",(True, False, True, False, True)),
        ("171",(True, False, True, False, True)),
        # Right
        ("RightBlinker",(False, True, False, False, False)),
        ("24",(False, True, False, False, False)),
        ("80",(False, True, False, False, False)),
        ("88",(False, True, False, False, False)),
        # Right Position
        ("17",(False, True, False, False, False)),
        ("25",(False, True, False, False, False)),
        ("81",(False, True, False, False, False)),
        ("89",(False, True, False, False, False)),
        # Right Low
        ("19",(False, True, True, False, False)),
        ("27",(False, True, True, False, False)),
        ("83",(False, True, True, False, False)),
        ("91",(False, True, True, False, False)),
        # Right Fog
        ("211",(False, True, True, False, True)),
        ("219",(False, True, True, False, True)),
        ("147",(False, True, True, False, True)),
        ("155",(False, True, True, False, True)),
        # Low
        ("3",(False, False, True, False, False)),
        ("11",(False, False, True, False, False)),
        ("67",(False, False, True, False, False)),
        ("75",(False, False, True, False, False)),
        # Fog
        ("131",(False, False, True, False, True)),
        ("139",(False, False, True, False, True)),
        ("195",(False, False, True, False, True)),
        ("203",(False, False, True, False, True)),
        # High
        ("HighBeam",(False, False, False, True, False)),
        ("12",(False, False, False, True, False)),
        ("68",(False, False, False, True, False)),
        ("76",(False, False, False, True, False)),
        # Left High
        ("36",(True, False, False, True, False)),
        ("44",(True, False, False, True, False)),
        ("100",(True, False, False, True, False)),
        ("108",(True, False, False, True, False)),
        # Right High
        ("20",(False, True, False, True, False)),
        ("28",(False, True, False, True, False)),
        ("84",(False, True, False, True, False)),
        ("92",(False, True, False, True, False)),
        # Low High
        ("7",(False, False, True, True, False)),
        ("71",(False, False, True, True, False)),
        ("79",(False, False, True, True, False)),
        ("15",(False, False, True, True, False)),
        # Fog High
        ("135",(False, False, False, True, True)),
        ("143",(False, False, False, True, True)),
        ("199",(False, False, False, True, True)),
        ("207",(False, False, False, True, True)),
        # Left High Low
        ("39",(True, False, True, True, False)),
        ("47",(True, False, True, True, False)),
        ("103",(True, False, True, True, False)),
        ("111",(True, False, True, True, False)),
        # Left High Fog
        ("167",(True, False, True, True, True)),
        ("175",(True, False, True, True, True)),
        ("231",(True, False, True, True, True)),
        ("239",(True, False, True, True, True)),
        # Right High Low
        ("23",(False, True, True, True, False)),
        ("31",(False, True, True, True, False)),
        ("87",(False, True, True, True, False)),
        ("95",(False, True, True, True, False)),
        # Right High Fog
        ("151",(False, True, True, True, True)),
        ("159",(False, True, True, True, True)),
        ("215",(False, True, True, True, True)),
        ("223",(False, True, True, True, True))
    ]

# The default value to return in case the match among the pairs was not found (NO LIGHTS ARE ON)
default_match = (False, False, False, False, False)
