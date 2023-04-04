import random

def increase_by_random_proportion(value, rounding, minimum, maximum):
    proportion = random.uniform(-0.15, 0.25)
    new_value = value * (1 + proportion)
    if new_value < minimum:
        new_value = minimum
    if maximum == "inf":
        pass
    else:
        max_value = float(maximum)
        if new_value > max_value:
            new_value = max_value  
    if rounding == 0:
        return int(round(new_value, rounding))
    else:
        return round(new_value, rounding)

input_string = "19,59,11,0.2524,0.3001,0.227,23.2532,0.1813,30.138,0.2635,20.3602,0.3148,29.3794,0.2263,38.7672,0.5021,36.7829,0.2587,0.2953,0.3247,8.9967,1237.7478,3302091.5543,72.6766,45.1205,37.5409,29.3105,275.5779,10.4171,24.5146,0.1131,1.0529,0.0355,0.0378,0.0,378.8219,43.3695,63.2421"
values = list(map(float, input_string.split(",")))

rounding_string = "0,0,0,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4"
min_string = "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-90,0,0,0,0,0,0,0,0,0"
max_string = "inf,inf,inf,1,1,1,100,1,100,1,100,1,100,1,100,1,100,1,1,1,inf,inf,inf,100,100,100,100,360,90,100,inf,100,inf,inf,inf,inf,100,1000"
rounding = list(map(int, rounding_string.split(",")))
minimums = list(map(float, min_string.split(",")))
maximums = list(map(str, max_string.split(",")))

for i in range(200):
    modified_values = [increase_by_random_proportion(value, rounding_digits, min_val, max_val) for value, rounding_digits, min_val, max_val in zip(values, rounding, minimums, maximums)]
    modified_string = ",".join(map(str, modified_values))
    print(modified_string)