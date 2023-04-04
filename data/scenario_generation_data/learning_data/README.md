
## Directory Contents

This directory contains these files:

1. `scenarios.csv` - a file containing entries of different scenarios. The data is used to train the machine learning algorithm to predict the attributes of a new scenario given the difficulty value.
2. `rounding.csv` - a file containing a 1 or 0 value for each attribute. The value indicates whether an attribute needs to be rounded to the nearest integer value after prediction.

For example, the algorithm may predict that a scenario of difficulty 20 should contain 25.678 pedestrians and the proportion of disobedient drivers on the road is 0.184.

While 0.184 represents 18.4% of all drivers disobeying road rules, 25.678 pedestrians does not make much sense. Therefore, some values need to be rounded, and the `rounding.csv` file specifies which attributes need to be rounded.

3. `minimums.csv` - a file indicating what min value each attribute can have. It is used to avoid predicting invalid values in the case of algorithm malfunction.

4. `maximums.csv` - a file indicating what max value each attribute can have. It is used to avoid predicting invalid values in the case of algorithm malfunction.

5. `quick_scenario_generation.py` - a Python script allowing for quick pseudo-scenario generation given an existing scenario.

6. `attribute_information.pdf` -  a file containing explanations and ranges of each of the attributes used by the algorithm.
