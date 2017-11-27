"""
- audit the OSMFILE and change the variable 'mapping' to reflect the changes needed to fix 
    the unexpected street types to the appropriate ones in the expected list.
    You have to add mappings only for the actual problems you find in this OSMFILE,
    not a generalized solution, since that may and will depend on the particular area you are auditing.
- update_name function, fixes the street name.
    The function takes a string with street name as an argument and should return the fixed name
    We have provided a simple test so that you see what exactly is expected
"""
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

postalcode_re = re.compile('^\d{6}$')

# expected street names
expected = ["Street", "Place", "Square", "Lane", "Road", "Colony", "Society", "Nagar", "Office",
            "Circle", "Area", "Lane", "Junction", "Hills"]

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


def audit_street_type(street_types, street_name):
    '''THis fuction checks if the street name is valid or not'''
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)
            

def audit_postal_type(postal_types,valid_codes, postal_code):
    '''This fuction checks if the postalcode is valid or not '''
    if postalcode_re.match(postal_code):
        valid_codes += 1
    else:    
        postal_types[postal_code].add(postal_code)
                 
            
def is_postal_code(elem):
    '''This fuction checks of the element key is a postalcode'''
    return (elem.attrib['k'] == "addr:postcode")


def is_street_name(elem):
    '''This fuction checks of the element key is a Street address'''
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    '''This fuction audits the osm file to look for inconsistencies with
    street names and postalcodes
    
    returns a two dictionary's having incoorect street names and postal codes
    '''
    osm_file = open(osmfile, 'rb')
    street_types = defaultdict(set)
    postal_types = defaultdict(set)
    valid_codes = 0
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):    
                    audit_street_type(street_types, tag.attrib['v'])
                elif is_postal_code(tag):
                    audit_postal_type(postal_types, valid_codes, tag.attrib['v'])
                    
                    
    osm_file.close()
    return (street_types, postal_types)

# to see if the code is working
def update_names():    
    st_types = audit(OSM_FILE)
    new_name = []
    for st_type, ways in st_types.items():
        for name in ways:
            new_name.append(update_name(name, mapping))
    return new_name   
            