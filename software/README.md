# Software directory

This directory is part of the CS Bachelor's thesis on the topic "Comparing human and AI behavior in simulated driving scenarios". It contains all the software implementations needed to automatically generate driving scenarios, let AI and human participants drive them, record their behavior on virtual roads, process the recorded data and draw graphical analysis on maps and diagrams while also evaluating drivers' performance.

## Technicalities

The software is working with [CARLA](https://carla.org) driving simulator.

- CARLA Version 0.9.13
- CARLA API Version 0.9.13
- OS: Ubuntu 18.04 and 20.04
- Python 3.6.9

All the required python libraries are listed [here](./python_libraries/requirements.txt).

## Structure

The following is the structure of this software bundle. More details can be found in the respective directories.

- [CARLA scripts](./carla_scripts/) - contains scripts for scenario processing and simulations.
- [Data analytics tools](./data_analysis/) - contains tools for parsing and analysing recorded data.
- [Python libraries](./python_libraries/) - required libraries for the software.
- [Scenario generation tool](./generating_scenarios/) - machine learning algorithm able to estimate the parameters of new scernarios.
- [Testing](./testing/) - directory containing various tests of software components.
