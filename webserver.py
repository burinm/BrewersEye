#!/usr/bin/env python3
""" tornado.py: Tornado webserver for Brewer's Eye database viewing
        burin (c) 2019

    APIS:
      /sensor1 -  Returns sensor1 temperature list in JSON string
            <start> = beginning date in [YY-MM-DD HH-MM-SS.mmmmmm] format
            <end> =   ending date in    [YY-MM-DD HH-MM-SS.mmmmmm] format
            <mod> =   skip every nth entry

      /sensor2 -  Returns sensor2 temperature list in JSON string
            <start> = beginning date in [YY-MM-DD HH-MM-SS.mmmmmm] format
            <end> =   ending date in    [YY-MM-DD HH-MM-SS.mmmmmm] format
            <mod> =   skip every nth entry

      /bubbles -  Returns bubbles list in JSON string
            <start> = beginning date in [YY-MM-DD HH-MM-SS.mmmmmm] format
            <end> =   ending date in    [YY-MM-DD HH-MM-SS.mmmmmm] format
            <mod> =   skip every nth entry

      /latest - Returns sensor1, sensor2 latest temperature, and 10 last bubble averages
            in JSON string

            (no arguments)

      /email  - Sends email
            <destination> = "To:" email address
            <subject> =  "Subject:" in plain text
            <message> =  message body in html

"""

from datetime import datetime, timedelta
# from db import db_get_last_temperature_entries, db_get_last_humidity_entries, \
#                db_add_temperature_entry, db_add_humidity_entry
from db import db_get_sensor1_entries_by_date, db_get_sensor2_entries_by_date, db_get_bubbles_entries_by_date, \
                db_get_last_sensor1_entries, db_get_last_sensor2_entries, db_get_last_bubble_entries

from sendmail import sendMessage

import threading
import signal

# webserver code
import tornado.ioloop
import tornado.web
import tornado.ioloop

import json

__author__ = "burin"
__copyright__ = "(c)2019"


def getTimestamp():
    # MySQL documentation - TIMESTATMP is 'YYYY-MM-DD hh:mm:ss[.fraction]'
    # https://dev.mysql.com/doc/refman/8.0/en/datetime.html
    # https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    #                                   luckily %f is 6 digits
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")


class Sensor1Handler(tornado.web.RequestHandler):
    """ Returns sensor1 temperature list in JSON string
            <start> = beginning date in [YY-MM-DD HH-MM-SS.mmmmmm] format
            <end> =   ending date in    [YY-MM-DD HH-MM-SS.mmmmmm] format
            <mod> =   skip every nth entry
    """
    def get(self):

        # Number of entries to request (default = 24 hours)
        #               43200 = number of seconds in 12 hours
        start_date = self.get_query_argument("start", datetime.now() - timedelta(0, 43200))
        end_date = self.get_query_argument("end", datetime.now() + timedelta(0, 43200))
        mod = self.get_query_argument("mod", 1)

        # TODO - validete input (use try/except, strptime)

        # mySql can only do one query at a time
        databaseLock.acquire()
        data = db_get_sensor1_entries_by_date(start_date, end_date, mod)
        databaseLock.release()

        # Write raw JSON string intstead of HTML source
        self.write(json.dumps(data))


class Sensor2Handler(tornado.web.RequestHandler):
    """ Returns sensor1 temperature list in JSON string
            <start> = beginning date in [YY-MM-DD HH-MM-SS.mmmmmm] format
            <end> =   ending date in    [YY-MM-DD HH-MM-SS.mmmmmm] format
            <mod> =   skip every nth entry
    """
    def get(self):

        # Number of entries to request (default = 24 hours)
        #               43200 = number of seconds in 12 hours
        start_date = self.get_query_argument("start", datetime.now() - timedelta(0, 43200))
        end_date = self.get_query_argument("end", datetime.now() + timedelta(0, 43200))
        mod = self.get_query_argument("mod", 1)

        # TODO - validete input (use try/except, strptime)

        # mySql can only do one query at a time
        databaseLock.acquire()
        data = db_get_sensor2_entries_by_date(start_date, end_date, mod)
        databaseLock.release()

        # Write raw JSON string intstead of HTML source
        self.write(json.dumps(data))


class BubbleHandler(tornado.web.RequestHandler):
    """ Returns bubbles list in JSON string
            <start> = beginning date in [YY-MM-DD HH-MM-SS.mmmmmm] format
            <end> =   ending date in    [YY-MM-DD HH-MM-SS.mmmmmm] format
            <mod> =   skip every nth entry
    """
    def get(self):

        # Number of entries to request (default = 24 hours)
        #               43200 = number of seconds in 12 hours
        start_date = self.get_query_argument("start", datetime.now() - timedelta(0, 43200))
        end_date = self.get_query_argument("end", datetime.now() + timedelta(0, 43200))
        mod = self.get_query_argument("mod", 1)

        # TODO - validete input (use try/except, strptime)

        # mySql can only do one query at a time
        databaseLock.acquire()
        data = db_get_bubbles_entries_by_date(start_date, end_date, mod)
        databaseLock.release()

        # Write raw JSON string intstead of HTML source
        self.write(json.dumps(data))


class LatestHandler(tornado.web.RequestHandler):
    """ Returns sensor1, sensor2 latest temperature, and 10 last bubble averages
            in JSON string
    """
    def get(self):

        results = {}

        # mySql can only do one query at a time
        databaseLock.acquire()
        data = db_get_last_sensor1_entries(1)
        databaseLock.release()

        results['sensor1'] = data

        databaseLock.acquire()
        data = db_get_last_sensor2_entries(1)
        databaseLock.release()

        results['sensor2'] = data

        databaseLock.acquire()
        data = db_get_last_bubble_entries(10)
        databaseLock.release()

        results['bubbles'] = data

        # Write raw JSON string intstead of HTML source
        self.write(json.dumps(results))


class EmailHandler(tornado.web.RequestHandler):
    """ Send an html email
            <destination> = "To:" email address
            <subject> =  "Subject:" in plain text
            <message> =  message body in plain text
    """
    def get(self):

        destination = self.get_query_argument("destination", None)
        subject = self.get_query_argument("subject", None)
        message = self.get_query_argument("message", None)

        if destination is None or subject is None or message is None:
            self.write(json.dumps({'error': 400}))
            return

        # Send message
        tornado.ioloop.IOLoop.current().spawn_callback(sendMessage, destination, subject, message)
        self.write(json.dumps({'error': 200}))


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
        (r"/sensor1", Sensor1Handler),
        (r"/sensor2", Sensor2Handler),
        (r"/bubbles", BubbleHandler),
        (r"/latest", LatestHandler),
        (r"/email", EmailHandler),
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
