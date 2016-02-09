#-*- coding:utf-8 -*-
import re
import uuid
from slugify import slugify as slug
import StringIO
import json
import csv
import os
import tornado.web
import sql
import pickle as pkl
import random
import import_tools as imp
import pandas as pd
import random

def rand_string(l):
    return str(uuid.uuid4())[:l]
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

def rand_color():
    r = lambda: random.randint(0,255)
    return ('#%02X%02X%02X' % (r(),r(),r()))

def complete_cp(raw_cp):
    regex = r'([0-9]{1,2})(?!.*\d)(eme|e\.|ere|er|e)?[\w ]*?$'
    m = re.match(regex, raw_cp)
    if not m:
        return False
    cp = m.group(1)
    if ( int(cp) > 20 ):
        return False

    l = len(cp)
    if (l==1):
        return '7510'+cp
    elif (l==2):
        return '751'+cp
    else:
        return False


_MIN = 3;
_MAX = 10;
def norm_radius(a,b,x):
    a = float(a)
    b = float(b)
    x = float(x)
    if ( a == b ):
        return _MIN
    
    rapport = ( b-a ) / (_MAX-_MIN)
    return _MIN + (x-a)/rapport


_COLOR_MAX = 255;
def norm_color(a,b,x):
    a = float(a)
    b = float(b)
    x = float(x)
    if ( a == b ): # no data, fill transparent
        return "rgba(255,255,255,1)"
    rapport = ( b-a ) / (_COLOR_MAX);
    c = int( round( _COLOR_MAX - (x-a)/rapport ) );

    return "rgb( 255, %s, %s )" % ( c, c )


class Points(tornado.web.RequestHandler):
    def get(self):
        distro_id = self.get_argument('distro')
        self.write( sql.get_points(distro_id) )


class QueryMap(tornado.web.RequestHandler):
    def post(self):
        global norm_radius
        global norm_color
        distro = self.get_argument('distro')
        routes = self.get_argument('routes', [])
        filters = json.loads( self.get_argument('filters', "[]") )
        paris = self.get_argument('paris')
        date = self.get_argument('date')
        flow_passagers = self.get_argument('flow_passagers')
        min_flow = self.get_argument('min_flow')
        max_flow = self.get_argument('max_flow')


        """
        AFFICHER LES DISTRO
        """
        features = []
        points, properties =  sql.get_points( distro, filters, date )
        min_value = properties["min_value"]
        max_value = properties["max_value"]
        data_label = properties["data_label"]
        avg_value = properties["avg_value"]
        for p in points:
            # stop_id, , , , stop_cp, data_id, data_value
            lon,lat,name,transfers = p['stop_lon'], p['stop_lat'], p['stop_name'], sql.get_transfers(p['stop_name'], date)
            data_value = p["data_value"] if "data_value" in p else "0"
            radius = norm_radius(min_value,max_value, data_value)

            color = norm_color(min_value,max_value, data_value)
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "properties": {
                    "stop_name": name,
                    "stop_transfers": transfers,
                    "data_value": data_value,
                    "radius": radius,
                    "fill_color": color,
                    "stop_cp": p['stop_cp'],
                    "rapport_avg": p["rapport_avg"]
                }
            }
            features.append(feature)

        distro_dic = {
            "type": "FeatureCollection",
            "features": features
        }


        features = []
        if ( paris != "0" ):
            for row in sql.get_paris():
                arr_coord, arr_name, arr_cp = row['arr_geo'], row['arr_name'], row['arr_cp']
                barycentre_lon, barycentre_lat = row['barycentre_lon'], row['barycentre_lat']
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": json.loads( arr_coord )
                    },
                    "properties": {
                        "arr_name": arr_name,
                        "arr_cp": arr_cp
                    }
                }
                features.append(feature)

                # feature = {
                #     "type": "Feature",
                #     "geometry": {
                #         "type": "Point",
                #         "coordinates": [barycentre_lon, barycentre_lat]
                #     },
                #     "properties": {
                #         "stop_name": "BARYCENTRE",
                #         "stop_transfers": '',
                #         "data_value": "VALUE",
                #         "radius": 10,
                #         "fill_color": "#ff9922"
                #     }
                # }
                # features.append(feature)
        paris_dic = {
            "type": "FeatureCollection",
            "features": features
        }


        features = []
        if ( flow_passagers == "1" ):
            chemins = sql.get_flow_passages(min_flow, max_flow)
            bound_min, bound_max = sql.get_flow_bounds()
            for row in chemins:
                feature = {
                    "chemin": json.loads( row['chemin'] ),
                    "value": norm_radius(bound_min,bound_max, row['value']),
                    "color": norm_color(bound_min,bound_max, row['value'])
                }
                features.append(feature)
        flows = features

        features = []
        if ( routes != 0 ):
            for row in sql.get_routes(filters, date):
                route_multilinestring = row['multilinestring']
                color = row['color']
                # print route_linestring
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "MultiLineString",
                        "coordinates": json.loads(route_multilinestring)
                    },
                    "properties": {
                        "color": color
                    }
                }
                features.append(feature)
        routes_dic = {
            "type": "FeatureCollection",
            "features": features
        }
        geo = {
            "distro": distro_dic,
            "properties_distro": {"data_label": data_label, "avg_value": avg_value},
            "paris": paris_dic,
            "routes": routes_dic,
            "flow": flows
        }

        geojsons = json.dumps( geo )

        with open("geojsons.txt", "w") as f:
            f.write(geojsons)

        self.write( geojsons )

class Users(tornado.web.RequestHandler):
    def get(self):
        f = pkl.load( open( "data/u10kSt.pkl", "rb" ) )
        self.write( str( len(f)) )
        self.write( str( f[3] ) )

class Stations(tornado.web.RequestHandler):
    def get(self):
        f = pkl.load( open( "data/niceStation.pkl", "rb" ) )
        self.write( str(len(f)) )
        self.write( str(f[0]) )

class DistroList(tornado.web.RequestHandler):
    def get(self):
        self.write( str(sql.get_distro_list()) )

class RouteList(tornado.web.RequestHandler):
    def get(self):
        self.write( str(sql.get_route_list() ))


class DelDistro(tornado.web.RequestHandler):
    def get(self):
        distro_id = self.get_argument("del")
        self.write( str(sql.del_distro( distro_id )) )

class Trains(tornado.web.RequestHandler):
    def post(self):
        year = self.get_argument("year")
        month = self.get_argument("month")
        day = self.get_argument("day")
        hour = self.get_argument("hour")
        minute = self.get_argument("minute")
        second = self.get_argument("second")

        self.write( sql.get_trips(year, month, day, hour, minute, second) )
        # with open("/home/riless/Desktop/query.txt", "wb") as f:
        #     f.write( sql.get_trips(year, month, day, hour, minute, second) )

class Upload(tornado.web.RequestHandler):
    def post(self):

        upload_cp = self.get_argument('upload_cp')
        upload_value = self.get_argument('upload_values')
        label = self.get_argument('data_label')

        icon = self.request.files['data_icon'][0]
        original_filename = icon['filename']
        data_icon = icon['body']

        slug_label = slug(label)
        ext = os.path.splitext(original_filename)[1]
        data_id = slug_label+'-'+rand_string(6)
        icon_filename = data_id+ext
        file_name = os.path.join('static','icons',icon_filename)
        
        with open( file_name , 'wb') as out:
            out.write(str(data_icon))

        data_file = self.request.files['data_file'][0]['body']
        # self.write(upload_cp +', '+ upload_values)
        if len(data_file) > 0: # si fichier n'est pas vide
            f = StringIO.StringIO(data_file)
            reader = csv.reader( f )
            has_header = csv.Sniffer().has_header(data_file[:1024])
            first_line = reader.next()
            nb_colonnes = len( first_line )
            f.seek(0)
            if has_header:
                headers = reader.next()

            data = []
            for row in reader:
                cp = complete_cp( row[int(upload_cp)] )
                v = row[int(upload_value)]
                if ( cp ):
                    data.append([cp,v])
            if ( len(data) > 0):
                sql.insert_new_data(label, icon_filename, data_id, data)


        else:
            self.write( dict( ["error", "wrong file type" ] ) )
        # original_fname = data_file['filename']
        # extension = os.path.splitext(original_fname)[1]
        # fname = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(6))
        # final_filename= fname+extension
        # output_file = open("uploads/" + final_filename, 'wb')
        # self.finish("file" + final_filename + " is uploaded")
    def get(self):
        self.write("get here")

class Calendars(tornado.web.RequestHandler):
    def get(self):
        self.write( json.dumps( sql.get_calendar() ) )

class FlowBounds(tornado.web.RequestHandler):
    def get(self):
        flux_min, flux_max = sql.get_flow_bounds()
        result = {"flux_min": int(flux_min), "flux_max": int(flux_max)}
        return self.write( json.dumps(result) )