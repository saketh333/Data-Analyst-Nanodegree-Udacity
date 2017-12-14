# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 23:40:39 2017

@author: Saketh
"""

import sys
import pickle
sys.path.append("../tools/")

features_list = ['poi', 'salary', 'deferral_payments', 'total_payments', 
                 'loan_advances', 'bonus', 'restricted_stock_deferred',
                 'deferred_income', 'total_stock_value', 'expenses',
                 'exercised_stock_options', 'long_term_incentive', 'restricted_stock',
                 'director_fees', 'to_messages', 'from_poi_to_this_person', 
                 'from_messages', 'from_this_person_to_poi', 'shared_receipt_with_poi', 'other', 'email_address'] # You will need to use more features

### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)



def missing_values():
    nan = {}
    for feature in features_list:
        nan[feature] = 0    
    for key in data_dict:
        for feature in features_list:
            if data_dict[key][feature] == 'NaN':
                nan[feature] += 1
    return nan


NaN = missing_values()
print NaN