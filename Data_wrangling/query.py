# Sql query on our hyderbad database

import sqlite3

# connecting to our database

db = sqlite3.connect('hyderbad.db')

cur = db.cursor()

def unique_users():
    print(cur.execute('SELECT COUNT(DISTINCT(uid)) \
    FROM (SELECT uid FROM nodes\
    UNION ALL SELECT uid FROM ways);').fetchone()[0])

def no_of_nodes():
    print(cur.execute('SELECT COUNT(*) FROM nodes').fetchone()[0])
    
def no_of_ways():
    print(cur.execute('SELECT COUNT(*) FROM ways').fetchone()[0])

def top_contributions():
    print(cur.execute('SELECT user, COUNT(*) as num \
FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) \
GROUP BY user \
ORDER BY num DESC \
LIMIT 10;').fetchall())
    
def contribution_just_once():
    print(cur.execute('SELECT COUNT(*) \
FROM (SELECT user, COUNT(*) as num \
     FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) \
     GROUP BY user \
     HAVING num=1);').fetchone()[0])
    
def amenities():
    print(cur.execute('SELECT value, COUNT(*) as num \
FROM nodes_tags \
WHERE key = "amenity" \
GROUP BY value \
ORDER BY num DESC \
LIMIT 10;').fetchall())

def popular_religion():
    print(cur.execute('SELECT nodes_tags.value, COUNT(*) as num \
FROM nodes_tags \
JOIN (SELECT DISTINCT(id) \
    FROM nodes_tags WHERE value="place_of_worship") i \
    ON nodes_tags.id=i.id \
WHERE nodes_tags.key="religion" \
GROUP BY nodes_tags.value \
ORDER BY num DESC \
LIMIT 3;').fetchall())
    
def cuisines():
    for row in cur.execute('SELECT nodes_tags.value, COUNT(*) as num \
FROM nodes_tags \
    JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value="restaurant") i\
    ON nodes_tags.id=i.id \
WHERE nodes_tags.key="cuisine" \
GROUP BY nodes_tags.value \
ORDER BY num DESC;'):
        print row

db.commit()