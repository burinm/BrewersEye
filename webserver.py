#!/usr/bin/env python3
""" tornado.py: Tornado webserver for Brewer's Eye database viewing

"""

from datetime import datetime
# from db import db_get_last_temperature_entries, db_get_last_humidity_entries, \
#                db_add_temperature_entry, db_add_humidity_entry

import threading
import signal

# webserver code
import tornado.ioloop
import tornado.web
import tornado.ioloop

__author__ = "burin"
__copyright__ = "(c)2019"


def getTimestamp():
    # MySQL documentation - TIMESTATMP is 'YYYY-MM-DD hh:mm:ss[.fraction]'
    # https://dev.mysql.com/doc/refman/8.0/en/datetime.html
    # https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    #                                   luckily %f is 6 digits
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")


"""
        if updateDatabase:
            # mySql can only do one query at a time
            sensorThread.databaseLock.acquire()
            db_add_temperature_entry(sensorThread.temperature, timestamp)
            db_add_humidity_entry(sensorThread.humidity, timestamp)
            sensorThread.databaseLock.release()
"""


def ctrl_c(signum, frame):
    """ Exit gracefully """
    print("Stopped by user")
    print("  tornado")
    tornado.ioloop.IOLoop.current().stop()
    # sys.exit()


# All web server code here

# Webserver template code used from tornado documentation
#   https://pypi.org/project/tornado/
#   static files: https://www.tornadoweb.org/en/stable/guide/running.html

settings = {
    "debug": True,
    "static_hash_cache": False  # Doesn't seem to work
}


class MainHandler(tornado.web.RequestHandler):
    """ Server landing page """
    def get(self):
        self.render('client/index.html')


# Needed this so that during development static pages won't cache!
# https://stackoverflow.com/questions/12031007/disable-static-file-caching-in-tornado
class fixStaticFileHandler(tornado.web.StaticFileHandler):
    def set_extra_headers(self, path):
        self.set_header('Cache-Control', 'no-store, no-cache, nust-revalidate, max-age=0')


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/(.*)", fixStaticFileHandler, {'path': "./client"})
     ], **settings)


# Main code starts here
databaseLock = threading.Lock()
signal.signal(signal.SIGINT, ctrl_c)

# Start up web server
app = make_app()
# app.listen(8080, address='172.16.0.1')
app.listen(8080)
tornado.ioloop.IOLoop.current().start()
