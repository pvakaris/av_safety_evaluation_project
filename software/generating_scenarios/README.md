## General information

This directory contains scripts needed to generate new driving scenarios.

The data used in learning is stored in the [learning_data](../../data/scenario_generation_data/learning_data/) directory.

Newly generated scenarios go to the [generated_scenarios](../../data/scenario_generation_data/generated_scenarios/) directory.

The `regressor` file contains the algorithm used to train the model and estimate new scenarios.

To create a new scenario, run the `create_scenario.py` file giving flags `-d` specifying the difficulty of the scenario, `-s` specifying the sun's altitude, `-w` specifying the wetness and `-f` the filename.

Example: `python create_scenario.py -d 200 -w 20 -s 30 -f new_scenario`