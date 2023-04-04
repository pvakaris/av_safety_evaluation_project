#!/bin/bash

# map specified which commonroad format file to use to depict the map layout
map=$1

# first_file is path to an .xml file containing the locations to mark on the map
first_file=$2

# second_file contains locations the same way the first_file does
second_file=$3

# For this, neccessary python libraties need to be installed
# More information on this can be found in the python_libraries directory

# Check if any of the arguments were provided
if [[ -z "$map" || -z "$first_file" ]]; then
    # If either map or first_file is missing, exit the script and echo a message
    echo "Error: missing arguments. Please specify map and first_file with points."
    exit 1
fi

# Check if map or first_file is missing
if [[ ! -f "../../../../data/maps/commonroad_format/$map" || ! -f "../../../../data/analysed_data/data/$first_file" ]]; then
    # If either map or first_file is missing, exit the script and echo a message
    echo "Error: map file or first_file does not exist. Please check the paths provided."
    exit 1
fi

# Launch crdesigner with appropriate arguments and disable any output to the terminal
echo "Drawing the map and marking the points."
if [ -n "$second_file" ]; then
    crdesigner -p1 "../../../../data/analysed_data/data/$first_file" -i "../../../../data/maps/commonroad_format/$map" -p2 "../../../../data/analysed_data/data/$second_file" > /dev/null 2>&1
else
    crdesigner -p1 "../../../../data/analysed_data/data/$first_file" -i "../../../../data/maps/commonroad_format/$map" > /dev/null 2>&1
fi
echo "Finished drawing the map and points."

# Remove files directory and its contents
rm -rf "files"