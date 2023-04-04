import pandas as pd
import numpy as np
from sklearn.multioutput import MultiOutputRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import json

SCENARIO_GENERATION_DATA_PATH = "../../data/scenario_generation_data"

# This class is responsible for initialising the MultiOutputRegressor algorithm which 
# is trained on the data contained in scenarios.csv file and is able to estimate new
# scenario parameters given difficulty
class Regressor():
    
    def __init__(self, randomise):
        # First read the .csv file containing scenario entries
        scenarios_dataframe = pd.read_csv("{}/learning_data/scenarios.csv".format(SCENARIO_GENERATION_DATA_PATH), delimiter = ",")
        random_state = 10 if randomise else None
        # Create a new dataset with only the difficulty as a feature and the rest of the attributes as targets
        X = scenarios_dataframe[["difficulty", "wetness", "sun_altitude_angle"]]
        y = scenarios_dataframe.drop(["difficulty", "wetness", "sun_altitude_angle"], axis=1)
        self.attribute_names = y.columns
        # Split the data into training and testing sets using the standard 80-20 approach
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size=0.1, random_state=random_state)
        # Train the multi-target regression model
        self.model = MultiOutputRegressor(RandomForestRegressor(n_estimators=100, random_state=random_state))
        self.model.fit(self.X_train.values, self.y_train)
        
    # This method will create a new scenario given the difficulty and then save it to the file
    def create_new_scenario(self, difficulty, wetness, sun, filename):
        attributes = self.predict_scenario_attributes(difficulty, wetness, sun)
        self.write_scenario_to_file(attributes, filename)
    
    # Given the difficulty, predict what attributes a scenario could have
    def predict_scenario_attributes(self, difficulty, wetness, sun):
        arr = np.array([difficulty, wetness, sun]).reshape(1, -1)
        attributes = self.model.predict(arr)[0]
        rounding = pd.read_csv("{}/learning_data/rounding.csv".format(SCENARIO_GENERATION_DATA_PATH))
        maximums = pd.read_csv("{}/learning_data/maximums.csv".format(SCENARIO_GENERATION_DATA_PATH))
        minimums = pd.read_csv("{}/learning_data/minimums.csv".format(SCENARIO_GENERATION_DATA_PATH))
        rounded_attributes = []
        # For each predicted value, check if it is not exceeding the maximum allowed value and is not lower than the mimum allowed value
        # Also round the final value accordingly
        list_of_attribute_names = self.attribute_names.tolist()
        for i in range(len(attributes)):
            value = self.format_attrbute_value(value = float(attributes[i]), minimum = float(minimums.loc[0, list_of_attribute_names[i]]), maximum = maximums.loc[0, list_of_attribute_names[i]], roundn = int(rounding.loc[0, list_of_attribute_names[i]]))
            rounded_attributes.append(value)
            
        # Also add difficulty, wetness and sun_altitude_angle to the final scenario file
        dictionary = dict(zip(self.attribute_names, rounded_attributes))
        dictionary["difficulty"] = self.format_attrbute_value(value = float(difficulty), minimum = float(minimums.loc[0, "difficulty"]), maximum = maximums.loc[0, "difficulty"], roundn = int(rounding.loc[0, "difficulty"]))
        dictionary["wetness"] = self.format_attrbute_value(value = float(wetness), minimum = float(minimums.loc[0, "wetness"]), maximum = maximums.loc[0, "wetness"], roundn = int(rounding.loc[0, "wetness"]))
        dictionary["sun_altitude_angle"] = self.format_attrbute_value(value = float(sun), minimum = float(minimums.loc[0, "sun_altitude_angle"]), maximum = maximums.loc[0, "sun_altitude_angle"], roundn = int(rounding.loc[0, "sun_altitude_angle"]))
        return dictionary

    def format_attrbute_value(self, value, minimum, maximum, roundn):
        if value < minimum:
            value = minimum
        if maximum == "inf":
            pass
        else:
            if value > float(maximum):
                value = float(maximum) 
        value = int(np.round(value)) if roundn == 0 else np.round(value, roundn)
        return value
            
    # Create a .json file and save the attribute values there
    def write_scenario_to_file(self, attributes, filename):
        with open("{}/generated_scenarios/{}.json".format(SCENARIO_GENERATION_DATA_PATH, filename), "w+") as f:
            json.dump(attributes, f, indent=4)