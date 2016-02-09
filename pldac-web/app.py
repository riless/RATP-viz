#-*- coding:utf-8 -*-

import tornado.ioloop
import tornado.web

import handlers
import os


settings = dict({
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "template_path": os.path.join(os.path.dirname(__file__),"templates"),
    "cookie_secret": os.urandom(12),
    "login_url": "/login",
    "xsrf_cookies": False,
    "debug":True
})

urls = [
    (r"/", handlers.MainHandler),
    (r"/points/.*", handlers.Points),
    (r"/users", handlers.Users),
    (r"/stations", handlers.Stations),
    (r"/upload", handlers.Upload),
    (r"/distro-list", handlers.DistroList),
    (r"/route-list", handlers.RouteList),
    (r"/del-disto/.*", handlers.DelDistro),
    (r"/query/.*", handlers.QueryMap),
    (r"/trains", handlers.Trains),
    (r"/calendars", handlers.Calendars),
    (r"/flow_bounds", handlers.FlowBounds),
]

application = tornado.web.Application(urls, **settings)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()