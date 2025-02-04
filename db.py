#!/usr/bin/env python3
""" db.py: Access to MySQL database

Useful resource:
    https://pythonspot.com/mysql-with-python/
    $ sudo apt-get install python-mysqldb

The database stores historyical temperature and humidity data
in the raw format it was retrieved from the sensors. This way
it can be converted/formatted later without precision loss.

The database consists of two tables temperature and humidity
which are both also store a timestamp in DATETIME format. An
auto incrementing id was used for the primary key. This way
all the entries are in order they were aquired, and we can just
ask for the last 'n' entries based on the highest key id

i.e. - SELECT * FROM temperature ORDER BY id DESC LIMIT 10) ORDER BY id ASC
        Get the last 10 entries ordered by the id in ascending order

10/5/2019 - Modified to return JSON strings
"""

import MySQLdb
from datetime import datetime

__author__ = "burin"
__copyright__ = "(c)2019"


# TODO - add back milliseconds?
def to_mysql_date(seconds: float):
    # MySQL documentation - TIMESTATMP is 'YYYY-MM-DD hh:mm:ss[.fraction]'
    # https://dev.mysql.com/doc/refman/8.0/en/datetime.html
    # https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    #
    # Converting:
    # https://www.programiz.com/python-programming/datetime/timestamp-datetime
    dt = datetime.fromtimestamp(int(seconds))
    return dt.strftime("%Y-%m-%d %H:%M:%S.%f")


def db_singleton():
    """ Only open the database once """
    try:
        if db_singleton.db is None:
            db_singleton.db = MySQLdb.connect(
                host="localhost",
                user="sensors",
                passwd="password",
                db="node88")  # TODO - Database depends on Node

        if db_singleton.cursor is None:
            db_singleton.cursor = db_singleton.db.cursor()

    except MySQLdb.OperationalError as e:
        print("Couldn't open database: " + str(e))
        return (None, None)

    return (db_singleton.db, db_singleton.cursor)


db_singleton.db = None
db_singleton.cursor = None


def db_destroy():
    if db_singleton.cursor is not None:
        db_singleton.cursor.close()
        db_singleton.db.close()


def db_add_sensor1_entry(temperature: float, timestamp: str):
    # https://pynative.com/python-mysql-execute-parameterized-query-using-prepared-statement/
    query = "INSERT INTO sensor1 (value, timestamp) VALUES(%s, %s)"
    data = (temperature, timestamp)
    db, cursor = db_singleton()
    cursor.execute(query, data)
    db.commit()


def db_add_sensor2_entry(temperature: float, timestamp: str):
    # https://pynative.com/python-mysql-execute-parameterized-query-using-prepared-statement/
    query = "INSERT INTO sensor2 (value, timestamp) VALUES(%s, %s)"
    data = (temperature, timestamp)
    db, cursor = db_singleton()
    cursor.execute(query, data)
    db.commit()


def db_add_bubbles_entry(bubbles: int, timestamp: str):
    # https://pynative.com/python-mysql-execute-parameterized-query-using-prepared-statement/
    query = "INSERT INTO bubbles (value, timestamp) VALUES(%s, %s)"
    data = (bubbles, timestamp)
    db, cursor = db_singleton()
    cursor.execute(query, data)
    db.commit()


def db_get_sensor1_entries_by_date(start: str, end: str, mod: int = 1):
    """ Get sensor1 entries for the specified date range """
    query = "SELECT * FROM sensor1 where timestamp >= %s and timestamp <= %s and sensor1.id mod %s = 0;"
    data = (start, end, mod)
    db, cursor = db_singleton()
    cursor.execute(query, data)

    # https://stackoverflow.com/questions/858746/how-do-you-select-every-n-th-row-from-mysql
    # mod trick! only select every other n'th row!

    result = cursor.fetchall()
    # https://stackoverflow.com/questions/15410119/use-list-comprehension-to-build-a-tuple
    # https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions
    # return {'temperatures': [(int(i[0]), float(i[1]), str(i[2])) for i in result]}
    return {'sensor1': [{'index': int(i[0]), 'temperature': float(i[1]), 'timestamp': str(i[2])} for i in result]}


def db_get_sensor2_entries_by_date(start: str, end: str, mod: int = 1):
    """ Get sensor1 entries for the specified date range """
    query = "SELECT * FROM sensor2 where timestamp >= %s and timestamp <= %s and sensor2.id mod %s = 0;"
    data = (start, end, mod)
    db, cursor = db_singleton()
    cursor.execute(query, data)

    # https://stackoverflow.com/questions/858746/how-do-you-select-every-n-th-row-from-mysql
    # mod trick! only select every other n'th row!

    result = cursor.fetchall()
    # https://stackoverflow.com/questions/15410119/use-list-comprehension-to-build-a-tuple
    # https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions
    # return {'temperatures': [(int(i[0]), float(i[1]), str(i[2])) for i in result]}
    return {'sensor2': [{'index': int(i[0]), 'temperature': float(i[1]), 'timestamp': str(i[2])} for i in result]}


def db_get_bubbles_entries_by_date(start: str, end: str, mod: int = 1):
    """ Get sensor1 entries for the specified date range """
    query = "SELECT * FROM bubbles where timestamp >= %s and timestamp <= %s and bubbles.id mod %s = 0;"
    data = (start, end, mod)
    db, cursor = db_singleton()
    cursor.execute(query, data)

    # https://stackoverflow.com/questions/858746/how-do-you-select-every-n-th-row-from-mysql
    # mod trick! only select every other n'th row!

    result = cursor.fetchall()
    # https://stackoverflow.com/questions/15410119/use-list-comprehension-to-build-a-tuple
    # https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions
    # return {'temperatures': [(int(i[0]), float(i[1]), str(i[2])) for i in result]}
    return {'bubbles': [{'index': int(i[0]), 'average': float(i[1]), 'timestamp': str(i[2])} for i in result]}


def db_get_last_sensor1_entries(n: int):
    """ Get the last 'n' entries from the sensor1 table """
    # https://dba.stackexchange.com/questions/156911/get-last-x-rows-order-by-asc
    query = "(SELECT * FROM sensor1 ORDER BY id DESC LIMIT %s) ORDER BY id ASC;"
    data = (n, )
    db, cursor = db_singleton()
    cursor.execute(query, data)

    result = cursor.fetchall()
    # https://stackoverflow.com/questions/15410119/use-list-comprehension-to-build-a-tuple
    # https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions
    # return tuple([(float(i[1]), str(i[2])) for i in result])
    return {'entries': [{'index': int(i[0]), 'temperature': float(i[1]), 'timestamp': str(i[2])} for i in result]}


def db_get_last_sensor2_entries(n: int):
    """ Get the last 'n' entries from the sensor2 table """
    # https://dba.stackexchange.com/questions/156911/get-last-x-rows-order-by-asc
    query = "(SELECT * FROM sensor2 ORDER BY id DESC LIMIT %s) ORDER BY id ASC;"
    data = (n, )
    db, cursor = db_singleton()
    cursor.execute(query, data)

    result = cursor.fetchall()
    # https://stackoverflow.com/questions/15410119/use-list-comprehension-to-build-a-tuple
    # https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions
    # return tuple([(float(i[1]), str(i[2])) for i in result])
    return {'entries': [{'index': int(i[0]), 'temperature': float(i[1]), 'timestamp': str(i[2])} for i in result]}


def db_get_last_bubble_entries(n: int):
    """ Get the last 'n' entries from the bubbles table """
    # https://dba.stackexchange.com/questions/156911/get-last-x-rows-order-by-asc
    query = "(SELECT * FROM bubbles ORDER BY id DESC LIMIT %s) ORDER BY id ASC;"
    data = (n, )
    db, cursor = db_singleton()
    cursor.execute(query, data)

    result = cursor.fetchall()
    # https://stackoverflow.com/questions/15410119/use-list-comprehension-to-build-a-tuple
    # https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions
    # return tuple([(float(i[1]), str(i[2])) for i in result])
    return {'entries': [{'index': int(i[0]), 'average': float(i[1]), 'timestamp': str(i[2])} for i in result]}
