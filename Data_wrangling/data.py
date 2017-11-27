#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

The process for this transformation is as follows:
- Use iterparse to iteratively step through each top level element in the XML
- Shape each element into several data structures using a custom function
- Utilize a schema and validation library to ensure the transformed data is in the correct format
- Write each data structure to the appropriate .csv files

We've already provided the code needed to load the data, perform iterative parsing and write the
output to csv files. Your task is to complete the shape_element function that will transform each
element into the correct format. To make this process easier we've already defined a schema (see
the schema.py file in the last code tab) for the .csv files and the eventual tables. Using the 
cerberus library we can validate the output against this schema to ensure it is correct.

## Shape Element Function
The function should take as input an iterparse Element object and return a dictionary.

### If the element top level tag is "node":
The dictionary returned should have the format {"node": .., "node_tags": ...}

The "node" field should hold a dictionary of the following top level node attributes:
- id
- user
- uid
- version
- lat
- lon
- timestamp
- changeset
All other attributes can be ignored

The "node_tags" field should hold a list of dictionaries, one per secondary tag. Secondary tags are
child tags of node which have the tag name/type: "tag". Each dictionary should have the following
fields from the secondary tag attributes:
- id: the top level node id attribute value
- key: the full tag "k" attribute value if no colon is present or the characters after the colon if one is.
- value: the tag "v" attribute value
- type: either the characters before the colon in the tag "k" value or "regular" if a colon
        is not present.

Additionally,

- if the tag "k" value contains problematic characters, the tag should be ignored
- if the tag "k" value contains a ":" the characters before the ":" should be set as the tag type
  and characters after the ":" should be set as the tag key
- if there are additional ":" in the "k" value they and they should be ignored and kept as part of
  the tag key. For example:

  <tag k="addr:street:name" v="Lincoln"/>
  should be turned into
  {'id': 12345, 'key': 'street:name', 'value': 'Lincoln', 'type': 'addr'}

- If a node has no secondary tags then the "node_tags" field should just contain an empty list.


### If the element top level tag is "way":
The dictionary should have the format {"way": ..., "way_tags": ..., "way_nodes": ...}

The "way" field should hold a dictionary of the following top level way attributes:
- id
-  user
- uid
- version
- timestamp
- changeset

All other attributes can be ignored

The "way_tags" field should again hold a list of dictionaries, following the exact same rules as
for "node_tags".

Additionally, the dictionary should have a field "way_nodes". "way_nodes" should hold a list of
dictionaries, one for each nd child tag.  Each dictionary should have the fields:
- id: the top level element (way) id
- node_id: the ref attribute value of the nd tag
- position: the index starting at 0 of the nd tag i.e. what order the nd tag appears within
            the way element


"""

import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET

import cerberus

import schema


OSM_PATH = "Hyderabad_sample.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# names to map using the update function

mapping = { "St": "Street",
            "St.": "Street",
            "Ave": "Avenue",
            "Rd." : "Road",
            "Rd" : "Road",
            "alwal":"Alwal",
            "road":"Road",
            "colony":"Colony",
            "society":"Society",
            "enclave":"Enclave",
            "office":"Office",
            "substation":"Substation",
            "gangaram":"Gangaram",
            "nagar,amberpet" : "Nagar, Amberpet",
            "street" : "Street",
            "x-roads" : "Cross Road",
            "x;road" : "Cross Road",
            "raod" : "Road",
            "No-92" : "Number 92",
            "No.3" : "Number 3",
            "No.7" : "Number 7",
            "Marg" : "Road",
            "Hydera" : "Hyderabad",
            "Gachibowlo" : "Gachibowli",
            "Balkumpet" : "Balkampet",
            "Colony, " : "Colony",
            "no": "Number",
            "No." : "Number",
            "number" : "Number",
            "ROAD" : "Road",
            "ROADS" : "Roads",
            "roads" : "Roads",
            "street" : "Street"
            }

# function to update the name

def update(name, mapping):
    '''This fucntion takes a string and a dictionary
    it checks if the string is in the dictionary key,
    if yes it replaces it with the dictionary value for the key
    '''
    words = name.split()
    for w in range(len(words)):
        if words[w] in mapping:
            words[w] = mapping[words[w]] 
            name = " ".join(words)
    return name

# error mappings in postal code that needed to be changed
postal_mapping = { "50" : "500050",
                  "50046": "500046",
                  "34500034":"500034",
                  "5000000" : "500000",
                  "5021377" : "502137"
                 }

def update_postalCode(name, postal_mapping):
    '''This fuction takes a postalcode and checks if its
    correct or not, if incorrect it fixes it'''
    # correct postal codes but have space in between 
    if (' ' in name) == True:
        return re.sub('(?<=\d) (?=\d)', '', name) # removing space
    elif name in postal_mapping.keys():
        #substitute with correct one
        return re.sub(name, postal_mapping[name], name) 
    else:
        return name

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']



def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,

                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):

    node_attributes = {}

    way_attributes = {}

    way_nodes = []

    tags = []  

    # checking if the element is node 

    if element.tag == 'node':

        for attribute in element.attrib:

            if attribute in NODE_FIELDS: # attributes in NODE_FIELDS

                node_attributes[attribute] = element.attrib[attribute]

        for child in element:

            node_tags = {}

            if re.match(LOWER_COLON, child.attrib['k']): 

                node_tags['type'] = child.attrib['k'].split(':',1)[0]

                node_tags['key'] = child.attrib['k'].split(':',1)[1]

                node_tags['id'] = element.attrib['id']
                
                # to check if the attribute k is a street address
                if child.attrib['k'] == "addr:street":
                    
                    # updating the names with inconsistencies present in mapping 
                    node_tags['value'] = update(child.attrib['v'], mapping)
                    
                    
                # to check if the attribute k is a postalcode    
                elif child.attrib['k'] == "addr:postcode":
                    
                    node_tags['value'] = update_postalCode(child.attrib['v'], postal_mapping)
                                                                                                
                else:
                    node_tags['value'] = child.attrib['v']

                tags.append(node_tags)

            elif PROBLEMCHARS.search(child.attrib['k']):

                continue

            else:
                
                node_tags['type'] = 'regular'

                node_tags['key'] = child.attrib['k']

                node_tags['id'] = element.attrib['id']
                
                # to check if the attribute k is a street address
                if child.attrib['k'] == "addr:street":
                    
                    # updating the names with inconsistencies present in mapping 
                    node_tags['value'] = update(child.attrib['v'], mapping)
                    
                    
                # to check if the attribute k is a postalcode    
                elif child.attrib['k'] == "addr:postcode":
                    
                    node_tags['value'] = update_postalCode(child.attrib['v'], postal_mapping)
                                                                                                
                else:
                    node_tags['value'] = child.attrib['v']

                tags.append(node_tags)

        return {'node': node_attributes, 'node_tags': tags}


    elif element.tag == 'way':

        for attribute in element.attrib:

            if attribute in WAY_FIELDS:

                way_attributes[attribute] = element.attrib[attribute]

        position = 0

        for child in element:
            

            way_tag = {}

            way_node = {}

            if child.tag == 'tag':

                if re.match(LOWER_COLON,child.attrib['k']):

                    way_tag['type'] = child.attrib['k'].split(':',1)[0]

                    way_tag['key'] = child.attrib['k'].split(':',1)[1]

                    way_tag['id'] = element.attrib['id']

                    way_tag['value'] = child.attrib['v']

                    tags.append(way_tag)

                elif PROBLEMCHARS.search(child.attrib['k']):

                    continue

                else:

                    way_tag['type'] = 'regular'

                    way_tag['key'] = child.attrib['k']

                    way_tag['id'] = element.attrib['id']

                    way_tag['value'] = child.attrib['v']

                    tags.append(way_tag)

                    

            elif child.tag == 'nd':

                way_node['id'] = element.attrib['id']

                way_node['node_id'] = child.attrib['ref']

                way_node['position'] = position

                position += 1

                way_nodes.append(way_node)
        return {'way': way_attributes, 'way_nodes': way_nodes, 'way_tags': tags}
    
# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=True)
