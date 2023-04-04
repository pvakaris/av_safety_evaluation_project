## Introduction
This directory contains the `crdesigner` python library and the requirements.txt file containing a list of python libraries needed to work with this framework.

`crdesigner` is a modified version of the `crdesigner` library (version 0.6.0). This version was the most recent release available at the time of the research.
More about crdesigner can be found [here](https://gitlab.lrz.de/tum-cps/commonroad-scenario-designer).

## Modification
The original `commonroad-scenario-designer` library was modified because it could not read input map files correctly and could not draw a list of specific points on the map when launched. The modifications made to the library have resolved these issues and made the library fit the purpose of recording data analysis and representation. In order for the map drawing to work, use this folder as the module instead of the original version. The original crdesigner module is installed using requirements.txt file.

## Requirements
The `requirements.txt` file lists the dependencies required to use this project.
These dependencies can be installed by creating a virtual environment at the root of this project and running the command
``pip install -r requirements.txt``