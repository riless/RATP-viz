from subprocess import Popen, PIPE


db_name = 'pldac'

process = Popen(['mysql','-uroot','-proot', '--local-infile', db_name], stdout=PIPE, stdin=PIPE)


files = {
	'agency': ('agency.txt','(agency_id,agency_name,agency_url,agency_timezone,agency_lang,agency_phone)'),
	'calendar': ('calendar.txt','(service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date)'),
	'calendar_dates': ('calendar_dates.txt','(service_id,date,exception_type)'),
	'routes': ('routes.txt','(route_id,agency_id,route_short_name,route_long_name,route_desc,route_type,route_url,route_color,route_text_color)'),
	'stops': ('stops.txt','(stop_id,stop_code,stop_name,stop_desc,stop_lat,stop_lon,location_type,parent_station)'),
	'stop_times': ('stop_times.txt','(trip_id,arrival_time,departure_time,stop_id,stop_sequence,stop_headsign,shape_dist_traveled)'),
	'transfers': ('transfers.txt','(from_stop_id,to_stop_id,transfer_type,min_transfer_time)'),
	'trips': ('trips.txt','(route_id,service_id,trip_id,trip_headsign,trip_short_name,direction_id,shape_id)' )
}

metro_path = '/home/riless/Desktop/pldac/data/RATP_GTFS_LINES/METRO/RATP_GTFS_METRO_{}/'
metro_stations = [
	'1','2','3','3b','4',
	'5','6','7','7b','8',
	'9','10', '11', '12',
	'13', '14'
]
# metro_stations = ['7']

metro_stations_paths = [metro_path.format(station_num) for station_num in metro_stations]

# metro_stations_paths = ['/home/riless/Desktop/pldac/data/RATP_GTFS_FULL_201405200930/']
query = ''
for metro_stations_path in metro_stations_paths:
	for table_name, (table_file, table_structure) in files.items():
		query += '''LOAD DATA LOCAL INFILE '{}' INTO TABLE {}
			FIELDS TERMINATED BY ','
			ENCLOSED BY '"'
			LINES TERMINATED BY '\\n'
			IGNORE 1 LINES
			{};\n\n
		'''.format(metro_stations_path + table_file, table_name, table_structure)

# print query

output = process.communicate(query)[0]
print output



# LOAD DATA LOCAL INFILE '/var/www/html/pldac/passages.csv' 
# INTO TABLE passages 
# FIELDS TERMINATED BY ',' 
# ENCLOSED BY '"'
# LINES TERMINATED BY '\n'
# IGNORE 1 ROWS;


