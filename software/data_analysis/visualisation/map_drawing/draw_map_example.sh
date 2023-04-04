#!/bin/bash

first_file="example_analysis/points/scenario2_collision_data.xml"
#second_file="example_analysis/points/scenario1_collision_data.xml"
map="Town07_commonRoad.xml"

# Second file can also be passed into the draw_map script to draw two depict two different datasets on the map
bash draw_map.sh $map $first_file #$second_file