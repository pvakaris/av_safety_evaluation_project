#!/bin/bash

####### ONLY THIS BIT IS MEANT TO BE EDITED #######
category="LaneMarkingViolationPenaltyPointsAverage"
title="Lane Marking Violation Penalty Points Average in Scenario 1"
xlabel="Participants"
save_filename="example_participants"
data_filename="example_analysis/participants.xml"
####### ####### ####### ####### ####### ####### ###

data_path="../../../../data/analysed_data/data/$data_filename"
save_path="../../../../data/analysed_data/diagrams/$save_filename"

python draw_diagram.py --xml_file "$data_path" --category "$category" --save "$save_path" --title "$title" --xlabel "$xlabel"