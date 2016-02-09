#*-* coding:utf-8 *-*

import snap
import MySQLdb as mysql

db = mysql.connect(
    host   =    "localhost", 
    user   =    "root", 
    passwd =    "root",
    db     =    "pldac",
    charset=    "utf8"
)
db.set_character_set('utf8')


def bigram(l):
    bi = []
    for i in range( len(l)-1 ):
        bi.append( [ l[i], l[i+1] ] )
    return bi


metro_stations = [
	'1','2','3','3b','4',
	'5','6','7','7b','8',
	'9','10', '11', '12',
	'13', '14'
]

metro_stations = ['14']

cur = db.cursor(mysql.cursors.DictCursor)
cur.execute('SET NAMES utf8;')
cur.execute('SET CHARACTER SET utf8;')
cur.execute('SET character_set_connection=utf8;')

cur2 = db.cursor(mysql.cursors.DictCursor)
cur2.execute('SET NAMES utf8;')
cur2.execute('SET CHARACTER SET utf8;')
cur2.execute('SET character_set_connection=utf8;')

cur3 = db.cursor(mysql.cursors.DictCursor)
cur3.execute('SET NAMES utf8;')
cur3.execute('SET CHARACTER SET utf8;')
cur3.execute('SET character_set_connection=utf8;')

    
for route_short_name in metro_stations: # la 1 aller
    
    G1 = snap.TNGraph.New()

    trips_query = """
    select trip_id from trips
        where route_id in ( select route_id from routes where route_short_name = "%s" )
        and trip_id in ( select trip_id from trips where service_id in ( SELECT service_id FROM calendar /* where start_date <= now() */ ) and direction_id= 0)
    """ % route_short_name
    
    # trips_query = 'select trip_id from trips where route_id in (select route_id from routes where route_short_name = "%s") and direction_id = 0' % route_short_name
    
    
    # print "for each trip of route ", route_short_name, "..."
    trans = dict()
    S = snap.TIntStrH()
    cur.execute( trips_query )
    for row in cur.fetchall() :
        # For each trip 
        
        trip_query = "select stop_times.stop_id, stop_name from stop_times, stops where trip_id = %d and stop_times.stop_id = stops.stop_id order by stop_sequence" % row['trip_id']
        cur2.execute( trip_query )
        stop_ids = []
        # for each stop_time
        #ajouter les stop_id au graph
        for row2 in cur2.fetchall():
            try:
                stop_ids.append( row2['stop_id'] )
                if ( not G1.IsNode(row2['stop_id']) ):
                    G1.AddNode(row2['stop_id'])    
                S.AddDat(row2['stop_id'], str(row2['stop_id']) +" "+ row2['stop_name'].encode('utf8'))
                
            except Exception, e:
                pass

        # compter le nombre d'occurence
        for a,b in bigram(stop_ids):
            if ( trans.has_key((a,b)) ):
                trans[(a,b)] += 1
            else:
                trans[(a,b)] = 1
                
    # ajouter les arcs        
    for (a,b),occ in trans.items():
        if ( occ > 1000 and a !=b ):
            G1.AddEdge(a, b)
            pass

    sequences = {}
    if ( G1.GetNodes() > 0 ): # si des noeds ont été trouvé
        # for i, NI in enumerate(G1.Nodes()):
        #     if not NI.GetId() in sequences:
        #         sequences = {NI.GetId(): 0} # ajouter le noeud s'il n'existe pas déja
        #     for Id in NI.GetOutEdges():
        #         sequences[Id] = sequences[NI.GetId()] + 1
        #         add_station_query = 'insert into lignes (route_short_name, stop_before, stop_after) VALUES ("%s", "%s", "%s")' % ( route_short_name, NI.GetId(), Id )
        #         print add_station_query;
        #         cur3.execute( add_station_query )
        #         db.commit()
        
        # for stop_id, seq in sequences.items():
        #     add_station_query = 'insert into lignes (route_short_name, stop_before, stop_after) VALUES ("%s", "%s", "%s")' % ( route_short_name, stop_id, seq )
        #     print add_station_query;
        #     cur3.execute( add_station_query )
        #     db.commit()

        snap.DrawGViz(G1, snap.gvlDot, route_short_name + "-gvlDot-graph.png", "Ligne 14", S )
        snap.DrawGViz(G1, snap.gvlNeato, route_short_name + "-gvlNeato-graph.png", "Ligne 14", S )
        snap.DrawGViz(G1, snap.gvlTwopi, route_short_name + "-gvlTwopi-graph.png", "Ligne 14", S )
        snap.DrawGViz(G1, snap.gvlCirco, route_short_name + "-gvlCirco-graph.png", "Ligne 14", S )
        snap.DrawGViz(G1, snap.gvlSfdp, route_short_name + "-gvlSfdp-graph.png", "Ligne 14", S )
        # print route_short_name + "-graph.png ... done!"