## Data visualisation on the map

This directory contains scripts that visualise the specific points on the map using the modified crdesigner module which can be found [here](../../../python_libraries/crdesigner/).

Please note that I am not the author of the crdesigner module. It is a slightly modified version allowing for additional files to be specified when launching it resulting in a map representation on the screen is just one line of code.

To use the map drawing tool, please refer to the `draw_map_example.sh` script.

This script takes a CommonRoad type XML map description and a list of points from the analysed data. An example of how files containing points look like can be found [here](../../../../data/analysed_data/data/example_analysis/points/). Each file contains points indicating places where different violations occurred. These points can be used to study patterns and see where participants fail the most.

The `draw_map_example.sh` script also allows to provide a second file containing points.

Points from the first file are marked in blue color and points form the second file are marked in red color. This can be useful to analyse where human drivers and where AI agents make mistakes and then compare the results.