# this code will be used to count no of different top - level tags avalable in our data set

import xml.etree.cElementTree as ET
from xml.etree.cElementTree import iterparse
import pprint

def count_tags(filename):
'''
this fucntion takes a OSM file as argument
and returns a dictionary containing all the top level tags in file
'''
        count_tags = {}
        for _,elem in iterparse(filename): 
            if elem.tag not in count_tags:
                count_tags[elem.tag] = 1
            elif elem.tag in count_tags:
                count_tags[elem.tag] += 1
        return count_tags