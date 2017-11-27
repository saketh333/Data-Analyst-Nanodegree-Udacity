#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
"""
"k" value for each "<tag>" and see if there are any potential problems.

3 regular expressions are provided to check for certain patterns
in the tags. As we would like to change the data
model and expand the "addr:street" type of keys to a dictionary like this:
{"address": {"street": "Some value"}}
So, we have to see if we have such tags, and if we have any tags with
problematic characters.
"""


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


def key_type(element, keys):
	'''
	function 'key_type', gives us count of each categorie in a dictionary
    four tag categories in a dictionary:
	"lower", for tags that contain only lowercase letters and are valid,
	"lower_colon", for otherwise valid tags with a colon in their names,
	"problemchars", for tags with problematic characters, and
	"other", for other tags that do not fall into the other three categories.
	'''

    if element.tag == "tag":
        k = element.attrib['k']
        if re.match(lower, k) != None:
            keys['lower'] += 1
        elif re.match(lower_colon, k) != None:
            keys['lower_colon'] += 1
        elif problemchars.search(element.attrib['k']):
                keys['problemchars'] += 1
        else:
            keys['other'] += 1
    return keys



def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys