#-*- coding:utf-8 -*-
import os
import json
import MySQLdb as mysql

db = mysql.connect(
    host   =    "localhost", 
    user   =    "root", 
    passwd =    "root",
    db     =    "pldac",
    charset=    "utf8"
)
db.set_character_set('utf8')

def new_cur():
	cur = db.cursor(mysql.cursors.DictCursor)
	cur.execute('SET NAMES utf8;')
	cur.execute('SET CHARACTER SET utf8;')
	cur.execute('SET character_set_connection=utf8;')
	cur.execute('SET session group_concat_max_len=150000;')
	return cur

def init_data(date):
	tmp_cur = new_cur();
	tmp_cur.execute("""
		DROP TABLE #route_geo;
		CREATE TABLE #route_geo
		(
		    route_short_name varchar(10),
		    color varchar(10),
		    route_linestring text
		)
		""")

# https://a.tiles.mapbox.com/v4/riless.lm6ba9ep/page.html?access_token=pk.eyJ1IjoicmlsZXNzIiwiYSI6ImtYOXM4c00ifQ.NXbIrxVogudcrysJMNHjZg#9/48.7770/2.4074

def get_routes( filters, date ):
	cur = new_cur()

	routes_str = ""
	for f in filters:
		routes_str += "'%s'," % f 
	routes_str = routes_str[:-1]

	query = """  SELECT sub.route_short_name, c.color_hex AS color, CONCAT(  '[', GROUP_CONCAT( distinct sub.route_linestring
				SEPARATOR  ',' ) ,  ']' ) AS multilinestring
				FROM (

				SELECT r.route_short_name, CONCAT(  '[', GROUP_CONCAT( distinct CONCAT(  '[', s.stop_lon,  ',', s.stop_lat,  ']' ) 
				ORDER BY st.stop_sequence ASC 
				SEPARATOR  ',' ) ,  ']' ) AS route_linestring
				FROM routes r, stop_times st, stops s, calendar_dates cd, trips t
				WHERE r.route_id = t.route_id
				AND cd.date =  '%s'
				AND cd.service_id = t.service_id
				AND t.trip_id = st.trip_id
				AND s.stop_id = st.stop_id
				AND r.route_short_name
				IN (
				%s
				)
				GROUP BY t.trip_id
				)sub, lines_colors lc, colors c
				WHERE c.color_id = lc.color_id
				AND lc.route_short_name = sub.route_short_name
				GROUP BY route_short_name
		

		""" % (date, routes_str)
	cur.execute( query )

	return cur.fetchall()

def get_color(line):
	cur = new_cur()
	query = u"""
		select c.color_hex as color
		from lines_colors lc, colors c
		where lc.route_short_name = "%s"
		and c.color_id = lc.color_id
	""" % line
	cur.execute(query)
	return cur.fetchone()['color']

def get_transfers(stop_name, date):
	cur = new_cur()
	cur.execute( """
		select distinct r.route_short_name
		from routes r, trips t, stop_times st, calendar_dates cd
		where cd.date = %s
		and t.service_id = cd.service_id
		and r.route_id = t.route_id
		and t.trip_id = st.trip_id
		and st.stop_id in ( select stop_id from stops where stop_name = %s )

 	""" , (date, stop_name, ) )

	
	corr_str = ""
	for corr in cur.fetchall():
		corr_str += str(corr["route_short_name"]) + ","
	return corr_str[:-1]

	# return cur.fetchall()

def del_distro(distro_id):
	cur= new_cur()

	cur.execute( " select data_icon from data_meta where data_id = %s", (distro_id,) )
	icon_filename = cur.fetchone()["data_icon"]
	os.remove(os.path.join('static', 'icons', icon_filename))

	cur.execute( "delete from data where data_id = %s" , (distro_id,) )
	cur.execute( "delete from data_meta where data_id = %s", (distro_id,) )
	
	db.commit()

	return json.dumps( {'stat': 'success'} )

def insert_new_data(label, file_name, data_id, data):
	cur = new_cur()
	for cp,d in data:
		cur.execute("INSERT INTO data(data_cp, data_id, data_value) VALUES(%s, %s, %s)", (cp,data_id,d,) )
	cur.execute("INSERT INTO data_meta VALUES(%s,%s,%s)", (data_id, label,file_name,) )
	db.commit()

def get_distro_list():
	cur = new_cur()
	query = "select data_label, data_icon, data_id from data_meta"
	cur.execute( query )
	return json.dumps( cur.fetchall() )

def get_route_list():
	cur = new_cur()
	query =  "SELECT distinct route_short_name FROM lignes"
	cur.execute( query )
	return json.dumps( cur.fetchall() )


def get_points(distro_id, filters, date):
	cur = new_cur()
	# cur2 = new_cur()

	properties = {"min_value": 0, "max_value": 0, "data_label": "", "avg_value": -1, "rapport_avg": 0 }
	points = {}
	if ( len( filters) > 0 ):

		format_strings = ','.join(['%s'] * len(filters))

		if ( distro_id != "0"):
			cur.execute( """
				SELECT distinct r.route_short_name, s.stop_name, s.stop_lat, s.stop_lon, s.stop_cp, d.data_value
				, ROUND(data_value-agg.avg_data_value, 1) as rapport_avg
				from trips t, calendar_dates cd, stop_times st, routes r, stops s, data d, 
				( SELECT AVG(data_value) AS avg_data_value FROM data where data_id = '%s') as agg
				where t.service_id = cd.service_id
				and t.route_id = r.route_id 
				and t.trip_id = st.trip_id
				and st.stop_id = s.stop_id
				and cd.date = '%s'
				and d.data_id = '%s'
				and d.data_cp = s.stop_cp
				and r.route_short_name IN (%s)
			""" % (distro_id, date, distro_id, format_strings), tuple(filters) )

			points = cur.fetchall()
			cur.execute( """
				SELECT MIN(data_value) as min_value,  MAX(data_value) as max_value, AVG(data_value) as avg_value, data_label
				FROM data d, data_meta dm
				WHERE d.data_id = %s
				and d.data_id = dm.data_id
			""", (distro_id,))
			row = cur.fetchone()
			properties = {'min_value': row['min_value'], 'max_value': row['max_value'], 'data_label': row['data_label'], "avg_value": row['avg_value']}
		else:
			cur.execute( """
				SELECT distinct s.stop_id, s.stop_lat, s.stop_lon, s.stop_name, s.stop_cp, 0 as rapport_avg
				from trips t, calendar_dates cd, stop_times st, routes r, stops s
				where t.service_id = cd.service_id
				and t.route_id = r.route_id 
				and t.trip_id = st.trip_id
				and st.stop_id = s.stop_id
				and cd.date = '%s'
				and r.route_short_name IN (%s)
			""" % ( date, format_strings ), tuple(filters) )
			points = cur.fetchall()
	
	return points, properties


def get_paris():
	cur = new_cur()
	cur.execute( """
		SELECT arr_geo, arr_name, arr_cp, barycentre_lon, barycentre_lat
		FROM arrondissements
	""" )

	return cur.fetchall()


def get_polygone(trip_id):
	cur = new_cur()
	cur.execute( """
		SELECT stop_lat, stop_lon
		FROM stop_times st, stops s
		WHERE st.stop_id = s.stop_id
		AND trip_id = %s
		ORDER BY stop_sequence
	""", (trip_id,) )
	return [ [ row['stop_lat'], row['stop_lon'] ] for row in cur.fetchall() ]


def get_trips( year, month, day, hour, minute, second ):
	cur = new_cur()
	start_date = "%s-%s-%s" % (year,month,day)
	departure_time = "%s:%s:%s" % (hour,minute,second)
	cur.execute( """
		SELECT t.trip_id
		FROM stop_times st, trips t, calendar_dates cd
		WHERE cd.date = '%s'
		AND st.departure_time = '%s'
		AND cd.service_id = t.service_id  
		AND st.trip_id = t.trip_id
		group by t.trip_id
	""" % (start_date,departure_time, ) )

	return json.dumps( [ get_polygone( row['trip_id'] ) for row in cur.fetchall() ] )

def get_route_short_name(trip_id):
	cur = new_cur()
	cur.execute(
	"""
		SELECT distinct route_short_name
		FROM trips t, routes r
		where trip_id = %s
		and t.route_id = r.route_id limit 1
	""", (trip_id, ) )
	return cur.fetchone()['route_short_name']

def get_calendar():
	cur = new_cur()
	cur.execute( """
		SELECT distinct DATE_FORMAT(date, "%Y-%m-%d") as value,
		CONCAT( DAY(date),' ',MONTHNAME(date),' ',YEAR(date) ) as text,
		CASE
		    WHEN  DATEDIFF( NOW(), date ) >= 0
			AND DATEDIFF( NOW(), date ) = ( select min(DATEDIFF( NOW(), date )) from calendar_dates where DATEDIFF( NOW(), date ) >= 0 )
		    THEN 1
		    ELSE 0
		END as selected

		FROM calendar_dates c
		ORDER BY date
	""" )
	return cur.fetchall()

def get_flow_passages(min_flow,max_flow):
	cur = new_cur()
	cur.execute("""
	select flux.value, 
	CONCAT( '[[', a1.barycentre_lat ,',', a1.barycentre_lon, '],[', a2.barycentre_lat ,',', a2.barycentre_lon, ']]' )
as chemin

	from arrondissements a1, arrondissements a2, flux_passagers flux
	where flux.from_cp = a1.code_insee
	and flux.to_cp = a2.code_insee
	and a1.code_insee != a2.code_insee
	and flux.value >= %s
	and flux.value <= %s
	""", (min_flow, max_flow,) )

	return cur.fetchall()

def get_flow_bounds():
	cur = new_cur()
	cur.execute("""
	select max(flux.value) as max_value, min(flux.value) as min_value
	from flux_passagers flux
	""")
	row = cur.fetchone()
	return row['min_value'], row['max_value'] 
