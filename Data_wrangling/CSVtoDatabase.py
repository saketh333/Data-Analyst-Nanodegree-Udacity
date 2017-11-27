# Creating a Sql database using CSV files

import csv, sqlite3

db = sqlite3.connect("hyderbad.db") # creating database

# to use 8 bit strings instead of unicode string
db.text_factory = str


curs = db.cursor()

# creating nodes table
curs.execute("CREATE TABLE nodes (id INTEGER PRIMARY KEY NOT NULL, \
lat REAL, lon REAL, user TEXT, uid INTEGER, version INTEGER, \
changeset INTEGER, timestamp TEXT);")

# reading csv file using dictreader
reader = csv.DictReader(open('nodes.csv', 'rb'))


to_db = [(row['id'], row['lat'], row['lon'], row['user'], row['uid'], \
          row['version'], row['changeset'], row['timestamp']) for row in reader]

curs.executemany("INSERT INTO nodes (id, lat, lon, user, uid, version, \
changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?);", to_db)

db.commit()

# creating nodes_tags table
curs.execute("CREATE TABLE nodes_tags ( id INTEGER, key TEXT, value TEXT, \
type TEXT, FOREIGN KEY (id) REFERENCES nodes(id));")

# reading csv file using dictreader
reader2 = csv.DictReader(open('nodes_tags.csv', 'rb'))


to_db = [(row['id'], row['key'], row['value'], row['type']) \
         for row in reader2]

curs.executemany("INSERT INTO nodes_tags (id, key, value, type) \
VALUES (?, ?, ?, ?);", to_db)

db.commit()

# creating ways table
curs.execute("CREATE TABLE ways (id INTEGER PRIMARY KEY NOT NULL, \
user TEXT, \
uid INTEGER, \
version TEXT, \
changeset INTEGER, \
timestamp TEXT);")

# reading csv file using dictreader
reader3 = csv.DictReader(open('ways.csv', 'rb'))


to_db = [(row['id'], row['user'], row['uid'], row['version'],\
          row['changeset'], row['timestamp']) \
         for row in reader3]

curs.executemany("INSERT INTO ways (id, user, uid, version, changeset, timestamp) \
VALUES (?, ?, ?, ?, ?, ?);", to_db)

db.commit()

# creating way_tags table
curs.execute(" CREATE TABLE ways_tags (id INTEGER NOT NULL, \
key TEXT NOT NULL, \
value TEXT NOT NULL, \
type TEXT, \
FOREIGN KEY (id) REFERENCES ways(id));")

# reading csv file using dictreader
reader4 = csv.DictReader(open('ways_tags.csv', 'rb'))


to_db = [(row['id'], row['key'], row['value'], row['type']) \
         for row in reader4]

curs.executemany("INSERT INTO ways_tags (id, key, value, type) \
VALUES (?, ?, ?, ?);", to_db)

db.commit()

# creating way_nodes table
curs.execute("CREATE TABLE ways_nodes ( id INTEGER NOT NULL, \
node_id INTEGER NOT NULL, \
position INTEGER NOT NULL, \
FOREIGN KEY (id) REFERENCES ways(id), \
FOREIGN KEY (node_id) REFERENCES nodes(id));")

# reading csv file using dictreader
reader5 = csv.DictReader(open('ways_nodes.csv', 'rb'))


to_db = [(row['id'], row['node_id'], row['position']) \
         for row in reader5]

curs.executemany("INSERT INTO ways_nodes (id, node_id, position) \
VALUES (?, ?, ?);", to_db)

db.commit()

db.close()