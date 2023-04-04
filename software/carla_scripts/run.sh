#!/bin/bash

name=$1
ai=$2

if [ -z "$name" ]; then
    echo "If you want to run simulations, you need to provide the name of the participant"
    echo "Example use: ./run.sh participant1"
    echo "The name is needed to associate each participant with their simualtion results"
    exit 1
fi

# First create a directory for the participant
cd ../../data/recordings/
mkdir -p $name

# Create a log file for the session inside
touch $name/session_logs.log
chmod 666 $name/session_logs.log

cd ../../software/carla_scripts

if [ -n "$ai" ]; then
    if [ "$ai" = "ai" ]; then
        echo "Starting the simulations for AI agent. For the logs, check the $name/session_logs.log file in the recordings directory."
        python3 run.py -n "$name" --ai > /dev/null 2>&1
    else
        echo "If you want the AI implementation to run the scenarios write ai as the second argument of this script"
        exit 1
    fi
else
    echo "Starting the simulations in manual control. For the logs, check the $name/session_logs.log file in the recordings directory."
    python3 run.py -n "$name" > /dev/null 2>&1
fi
echo "Finished."