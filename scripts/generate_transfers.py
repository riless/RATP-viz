#*-* coding:utf-8 *-*

import MySQLdb as mysql

db = mysql.connect(
    host   =    "localhost", 
    user   =    "root", 
    passwd =    "root",
    db     =    "pldac",
    charset=    "utf8"
)
db.set_character_set('utf8')

cur = db.cursor(mysql.cursors.DictCursor)
cur.execute('SET NAMES utf8;')
cur.execute('SET CHARACTER SET utf8;')
cur.execute('SET character_set_connection=utf8;')

cur2 = db.cursor(mysql.cursors.DictCursor)
cur2.execute('SET NAMES utf8;')
cur2.execute('SET CHARACTER SET utf8;')
cur2.execute('SET character_set_connection=utf8;')


query_station_ids = "select distinct from_stop_id from transfers"
cur.execute( query_station_ids )
for row in cur.fetchall():
    query = u"""
    select distinct route_short_name from routes where route_id in (
        select distinct route_id from trips where trip_id in (
            select distinct trip_id from stop_times where stop_id in (
                select distinct to_stop_id from transfers where from_stop_id = '%s'   
            )
        )
    )""" % row['from_stop_id']
    print "#", row['from_stop_id']
    cur2.execute(query)
    for row2 in cur2.fetchall():
        insert_transfer = 'insert into transfers_lignes (from_stop_id, to_route_short_name) VALUES ("%s", "%s")' % ( row['from_stop_id'], row2['route_short_name'] )
        print insert_transfer
        cur2.execute( insert_transfer )
        db.commit()
 