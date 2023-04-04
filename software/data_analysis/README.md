# Data Analysis

## Introduction
This directory is dedicated to processing the recorded simulation data and presenting it in a meaningful way. In addition, it contains tools to evaluate the performance of participants.
## Content
The directory contains the following:
- analysis_parameters.json: A JSON file that holds information about the participants, scenarios, and metrics to be analyzed.
- analysis.py: A Python script that performs the data analysis based on the parameters defined in the analysis_parameters.json file.
- run_analysis.sh: A shell script to run the analysis using the analysis.py script.
- visualisation: Subdirectory containing scripts that for graphical representation.
- classes: Additional classes to help the analysis of recorded data files.
- score_calculator.py: a script to calculate the score of the participant in the given scenario
- scenario_analyser.py: a script to analyse the scenarios generating files that help to evaluate the performance of a participant

## analysis_parameters.json
Imagine that analysis_parameters.json file has the following structure:

```
{
    "participants": [
        "ParticipantA",
        "ParticipantB"
    ],
    "scenarios": [
        "scenario1"
    ],
    "metrics": [
        "collision_data",
        "road_traffic_violation_data"
    ]
}
```
This file states that we want to analyze the collisions and road traffic violation data from scenario1 driven by Participants A and B.

**The list of all possible metrics:**

```
    "collision_data",
    "lane_marking_violation_data",
    "vehicle_light_misuse_data",
    "route_data",
    "speeding_data",
    "road_traffic_violation_data"
```

## Running the Analysis
To run the analysis, simply execute the following command in the terminal:

```
bash run_analysis.sh name_of_analysis
```

Analysed data will be saved in the ./analysed_data/data/name_of_analysis directory.

Replace "name_of_analysis" with a desired name for the analysis instance.

## Results
The analysis tool will process the recording according to the parameters specified in the analysis_parameters.json file and produce the following files:
- participants.xml: Contains information about each of the specified participants and their average scores.
- scenarios.xml: Contains information about each of the specified scenarios and the average scores of participants.
- n .xml files in the points subdirectory: Each file contains a list of x and y coordinates, representing interesting patterns in the data.

For instance, the file scenario1_collision_data.xml will contain all the collision points for Participants A and B driving scenario1.

## Visual Representation
For visual representation of the data, please refer to the subdirectory [visualisation](./visualisation/).

## Scenario analyser
Before evaluating the score of a participant, we need to run the scenario analyser that will gather data from the simulated world and will create a file that will assist in evaluation.

The `scenario_analyser.py` script takes two arguments: -p indicating the path file and -s indicating the scenario file. It creates a file in the [simulation_details](../../data/simulation_details/) directory. The file is given the same name as the scenario specified in the arguments. **Please note that scenario_analyser.py script requires the CARLA simulator to be running.**

## Score evaluation
The score evaluation is performed using the `score_calculator.py` script. The script takes arguments -n indicating the name of the participant and -s argument indicating the scenario. Note, that there has to be a run of the scenario by that specific participant saved in the [recordings](../../data/recordings/) directory.