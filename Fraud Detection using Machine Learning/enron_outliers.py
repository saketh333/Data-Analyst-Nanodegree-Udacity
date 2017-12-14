#!/usr/bin/python

import pickle
import sys
import matplotlib.pyplot
sys.path.append("../tools/")
from feature_format import featureFormat, targetFeatureSplit


### read in data dictionary, convert to numpy array
data_dict = pickle.load( open("../final_project/final_project_dataset.pkl", "r") )


print ("\nWe have following people in our dataset :")
for key in data_dict.keys():
    print "\n{}".format(key)


features = ["salary", "bonus"]
data = featureFormat(data_dict, features)

### your code below
for point in data:
    salary = point[0]
    bonus = point[1]
    matplotlib.pyplot.scatter( salary, bonus )

matplotlib.pyplot.xlabel("salary")
matplotlib.pyplot.ylabel("bonus")
matplotlib.pyplot.show()

# finding the outlier
for key in data_dict:
    if data_dict[key]["salary"] != 'NaN' and data_dict[key]["bonus"] != 'NaN':
        if data_dict[key]["salary"] > 2000000 and data_dict[key]["bonus"] > 1000000:
            print key


data_dict.pop('TOTAL')


features = ["salary", "bonus"]
data = featureFormat(data_dict, features)

### your code below
for point in data:
    salary = point[0]
    bonus = point[1]
    matplotlib.pyplot.scatter( salary, bonus )

matplotlib.pyplot.xlabel("salary")
matplotlib.pyplot.ylabel("bonus")
matplotlib.pyplot.show()


# YEAP SOON
#print data_dict['YEAP SOON']
# this 'YEAP SOON' has most of the values as NaN' so removing it

# THE TRAVEL AGENCY IN THE PARK
#print data_dict['THE TRAVEL AGENCY IN THE PARK']
# this 'THE TRAVEL AGENCY IN THE PARK' has most of the values as NaN' and does not fit as name of a person



