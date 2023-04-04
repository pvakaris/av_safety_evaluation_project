# Simulation Recordings

This directory contains the results of simulated scenarios for different participants.

## Participants
Each participant is given a unique name and a list of scenarios to participate in. More information on how the participants are assigned to the scenarios can be found in the [run.sh](../../software/carla_scripts/run.sh) file.

## Directory Structure
The directory is structured as follows:
- Each participant has their own directory named after their name.
- Within each participant directory, there are `n` directories, where `n` is the number of scenarios they participated
- Moreover each participant directory has a `session_logs.log` file which contains logs received during the session (when participant was driving one scenario after the other).
- Each scenario directory is named after the scenario it represents.
- Within each scenario directory are .xml files containing data captured during the simulation of that scenario.
  
**In addition to the .xml files, a .log file is present in the directory of each scenario. That is the recording of the simulation itself.**
**It can be used to replay the simulation in CARLA. For more information, refer to the [replay.sh](../../software/carla_scripts/replay.sh/) script.**