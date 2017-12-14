#!/usr/bin/python

import sys
import pickle
import matplotlib.pyplot as plt
import numpy as np  
from sklearn import metrics  
sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data

### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".
features_list = ['poi', 'salary', 'total_payments', 'bonus',
                 'deferred_income', 'total_stock_value', 'expenses',
                 'exercised_stock_options', 'long_term_incentive', 'restricted_stock', 'to_messages', 'from_poi_to_this_person', 
                 'from_messages', 'from_this_person_to_poi', 'shared_receipt_with_poi'] # You will need to use more features


print "No of features Selected {}".format(len(features_list))

### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)

print "\nWe have data on {} people".format(len(data_dict))

def explore_poi():
    # Number of poi's in our dataset
    poi = 0
    notPoi = 0
    for key in data_dict:
        if data_dict[key]['poi']:
            poi += 1
        elif data_dict[key]['poi'] == False:
            notPoi += 1
                
    print "\nNo of Poi's in our data: {}".format(poi)
    print "\nNo of Non Poi's in our data: {}".format(notPoi)
    
    
    objects = ('POI', 'NotPoi')
    y_pos = np.arange(len(objects))
    numberPoi = []
    numberPoi.append(poi)
    numberPoi.append(notPoi)
 
    plt.bar(y_pos, numberPoi, align='center', alpha=0.5)
    plt.xticks(y_pos, objects)
    plt.title('Poi/nonPoi in the data')
 
    plt.show()

#explore_poi()  


#print ("\nWe have following people in our dataset :")
#for key in data_dict.keys():
#    print "\n{}".format(key)

        
### Task 2: Remove outliers
# Detected outliers using enron_outliers.py
# Some names that stood out to me after looking at dictionary keys in our datset
# 'TOTAL', 'YEAP SOON', 'THE TRAVEL AGENCY IN THE PARK'

# removing outliers
data_dict.pop('THE TRAVEL AGENCY IN THE PARK', 0)
data_dict.pop("LOCKHART EUGENE E", 0)
#data_dict.pop('YEAP SOON')
data_dict.pop('TOTAL', 0) # this must be an excel error and its the total of all the values


### Task 3: Create new feature(s)
### Store to my_dataset for easy export below.
my_dataset = data_dict


# created two features
# Messages from this person to poi ratio and poi to this person ratio
def feature_engineering():
    for key, value in my_dataset.iteritems():
        value['from_poi_to_this_person_ratio'] = 0
        if value['to_messages'] and value['from_poi_to_this_person']!= 'NaN':
            if value['from_poi_to_this_person'] > 0:
                value['from_poi_to_this_person_ratio'] = value['from_poi_to_this_person']/float(value['to_messages'])
                
    for key, value in my_dataset.iteritems():
        value['from_this_person_to_poi_ratio']=0
        if value['from_messages'] and value['from_this_person_to_poi']!= 'NaN':
                if value['from_this_person_to_poi'] > 0:
                    value['from_this_person_to_poi_ratio'] = value['from_this_person_to_poi']/float(value['from_messages'])

    features_list.extend(['from_poi_to_this_person_ratio', 'from_this_person_to_poi_ratio'])

feature_engineering()

### Extract features and labels from dataset for local testing
data = featureFormat(my_dataset, features_list, sort_keys = True)
labels, features = targetFeatureSplit(data)

# scaling features using min-max scaler and selecting using KBest
from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler(copy=True, feature_range=(0, 1))
features = scaler.fit_transform(features)

# select best features SelectKbest
from sklearn.feature_selection import SelectKBest, f_classif, chi2

my_features_list = features_list[1:]
selection = SelectKBest(f_classif, k=5) # looked at the feature importance scores and decided to select 5 best features
selection.fit(features,labels)
scores = selection.scores_
for feature, score in zip(my_features_list, scores):
    print "\n{}:{}".format(feature,score)
    
    

features_selected = [my_features_list[feature_ind] for feature_ind in selection.get_support(indices=True)]
selection.fit_transform(features,labels)

print "\nSelected features are \n{}".format(features_selected)

# Updating features and lables with the new features selected by K- best by importance.
### Extract features and labels from dataset for local testing
data = featureFormat(my_dataset, features_selected, sort_keys = True)
labels, features = targetFeatureSplit(data)

### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html

# Provided to give you a starting point. Try a variety of classifiers.

# Gaussian Naive Bayes Classifier
from sklearn.naive_bayes import GaussianNB
clf = GaussianNB()

# K-neighbors Classifier
from sklearn import neighbors
clf2 = neighbors.KNeighborsClassifier()

# Decision tree Classifier
from sklearn import tree
clf3 = tree.DecisionTreeClassifier()

# Support Vector Classifier
from sklearn.svm import SVC
clf4 = SVC(kernel='rbf')

#Random Forest Classifer
from sklearn.ensemble import RandomForestClassifier
clf5 = RandomForestClassifier()

# Gradient Boosting
from sklearn.ensemble import GradientBoostingClassifier
clf6 = GradientBoostingClassifier()


### Task 5: Tune your classifier to achieve better than .3 precision and recall 
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info: 
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html

# Parameter Tuning
from sklearn .model_selection import GridSearchCV
tune_SVC = [{'kernel': ['linear', 'rbf'], 'C': [1,10,100,500]}]

tune_KNN = [{'n_neighbors': [1,2,10], 'leaf_size': [10,100]}]

tune_DTC = [{'min_samples_split' : [2, 3, 5, 10], 'criterion' : ['gini', 'entropy'],}]

tune_RFC = [{'n_estimators':[1,5,10,100,200]}]

def para_tuning(model,tune_grid):
    clf = GridSearchCV(estimator=model, param_grid= tune_grid, n_jobs=-1)
    return clf

#clf = para_tuning(KNN,tune_KNN)
#clf = para_tuning(clf3,tune_DTC)

# Example starting point. Try investigating other evaluation techniques!
from sklearn.cross_validation import train_test_split
features_train, features_test, labels_train, labels_test = \
    train_test_split(features, labels, test_size=0.3, random_state=42)
    
#from sklearn.model_selection import StratifiedShuffleSplit
#sss = StratifiedShuffleSplit(n_splits=3, test_size=0.9, random_state=33)
#sss.get_n_splits(features,labels)
#for train_index, test_index in sss.split(features,labels):
#    features_train = []
#    labels_train =[]
#    features_test = []
#    labels_test = []
#    for ii in train_index:
#        features_train.append( features[ii] )
#        labels_train.append( labels[ii] )
#    for jj in test_index:
#        features_test.append( features[jj] )
#        labels_test.append( labels[jj] ) 
        
# Evaluate Classifier
def evaluate_classifier(clf, features_train, labels_train, features_test, labels_test):
    clf.fit(features_train, labels_train)
    predict = clf.predict(features_test)
    acc = clf.score(features_test,labels_test)
    print "Accuracy is {}".format(acc)
    print "No of POI's predicted in test set {}".format(sum(predict))
    print "No of POI's in test set {}".format(sum(labels_test))
    print "Precision of classifier {}".format(metrics.precision_score(labels_test, predict))
    print "Recall of the Classifier {}".format(metrics.recall_score(labels_test, predict))

#evaluate_classifier(clf, features_train, labels_train, features_test, labels_test)

### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.

dump_classifier_and_data(clf, my_dataset, features_list)