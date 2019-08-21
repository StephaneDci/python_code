# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------
# Auteur : Stéphane Di Cioccio
# Prérequis  pip install influxdb
# Object : diagnostic et aide sur InfluxDb derriere un reverseProxy
# Permet la suppression massive de shards
# --------------------------------------------------------------------------

import urllib3
import influxdb
import pandas as pd
import numpy as np
import seaborn as sns

# https://influxdb-python.readthedocs.io/en/latest/api-documentation.html
from influxdb import InfluxDBClient, DataFrameClient

from datetime import datetime, timezone
from dateutil.parser import parse
from pprint import pprint as pp

# Suppression des warning certificats https
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Options pandas
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', 50)
pd.set_option('display.width', 1000)

# ---------------------------------------------------------
#  Configuration des Connections Url / proxy / password
# ---------------------------------------------------------

proxy_squid = {'http': '127.0.0.1:3128', 'https': '127.0.0.1:3128'}
proxy_none  = {"http": None, "https": None}

connection_influx = {'uri': 'influx/',
                     'headers': {"Authorization": "put here basic auth"},
                     'host': 'your host',
                     'proxies': proxy_squid}

# ---------------------------------------------------------
#  Fonctions
# ---------------------------------------------------------


def query_to_df(q):
    df = pd.DataFrame(client.query(q, chunked=True, chunk_size=10000).get_points())
    return df


def get_values_from_json(respjson):
    """
    Construit une liste à partir de la réponse raw
    https://stackoverflow.com/questions/952914/how-to-make-a-flat-list-out-of-list-of-lists
    :param respjson: reponse raw JSON de influxDb
    :return: liste
    """
    dictvalue = dict()
    tmpdict = dict()
    if len(respjson) > 1:
        for n, series in enumerate(respjson.get('series')):
            if series is not None:
                name = series.get('name')
                value = series.get('values')
                if value is not None:
                    tmpdict['name'] = name
                    tmpdict['values'] = value
                    dictvalue[n] = tmpdict.copy()
    return dictvalue


def show_diags():
    result = client.query('show DIAGNOSTICS;')
    for info in list(result.get_points()):
        for k, v in info.items():
            print("{} {}".format(k, v))


def show_series(measurement):
    q = 'SHOW SERIES FROM ' + str(measurement) + ';'
    result = client.query(q)
    return list(result.get_points())


def show_fields_key():
    q = 'SHOW FIELD KEYS'
    print("\n" + q)
    res = get_values_from_json(client.query(q, chunked=False).raw)
    for k, v in res.items():
        print("{} => {}".format(v.get('name'), len(v.get('values'))))


def show_tags_key():
    q = 'SHOW TAG KEYS'
    print("\n" + q)
    res = get_values_from_json(client.query(q, chunked=False).raw)
    for k, v in res.items():
        print("{} => {}".format(v.get('name'), len(v.get('values'))))


def get_measurements():
    result = client.query('show measurements;')
    return list(result.get_points())


def get_series_from_measurements(measurements):
    print("\nAffichage des Series sur les measurements: \n")

    for msrmt in measurements:
        try:
            listser = show_series(msrmt.get('name'))
            print("{} => {} series".format(msrmt.get('name'), len(listser)))

        except influxdb.exceptions.InfluxDBClientError as influxerr:
            print("\t !! Incorrect Measurement => {}".format(msrmt))
            # client.drop_measurement(msrmt.get('name'))


def count_data_from_measurements(lst_measurements, time="10m"):
    print("\nAffichage des Datas sur les measurements: \n")
    for msrmt in lst_measurements:
        q = 'select * from "' + str(msrmt.get('name')) + '" where time > (now() - ' + time + ')'
        res = client.query(q)
        result = list(res.get_points())
        print("{} => {} datas in {} ".format(msrmt.get('name'), len(result), time))


def show_shards():
    result = client.query('show shards;')
    return list(result.get_points())


def suppress_shards(list_shards, limit=1000):
    print("Suppression de la liste des Shards par lot de {}".format(limit))
    pp(list_shards)
    rep = input("Etes-vous sur (taper: 'JECONFIRME'): ")
    if rep == 'JECONFIRME':
        for key in list(sorted(list_shards))[0:limit]:
            print()
            print("%s: %s" % (key, list_shards[key]))
            drop_shard(key)
    else:
        print("Abandon")


def drop_shard(no_shard):
    q = 'DROP shard '+str(no_shard)+';'
    print(q)
    result = client.query(q, method="POST")
    print(result.raw)


def get_incorrect_shards(nbdays=360, dbtodelete="logs"):
    """
    Trouve les shards alloués dans le futur apres nbdays
    :param nbdays: parametre en jour à partir de la date courante
    :param dbtodelete: database contenant les shards que nous voulons supprimer
    :return: dictionnaire contenant les informations des shards incorrects
    """

    allshards = show_shards()
    dtnow = datetime.now(timezone.utc)
    shards_to_suppress = dict()
    tmpdict = dict()

    for shardinfo in allshards:
        start_time = shardinfo.get('start_time')
        db_shard = shardinfo.get('database')
        dtdelta = parse(start_time) - dtnow
        if (dtdelta.days >= nbdays) & (dbtodelete == db_shard):
            tmpdict['db'] = db_shard
            tmpdict['start_time'] = start_time
            tmpdict['expire_time'] = shardinfo.get('expiry_time')
            tmpdict['delta_days'] = dtdelta.days
            shards_to_suppress[shardinfo.get('id')] = tmpdict.copy()
    print("Il y a {} shards {} jours apres le {} sur la base {}".format(len(shards_to_suppress), nbdays, dtnow, dbtodelete))
    return shards_to_suppress


# --------------------------------------------------
# Main
# --------------------------------------------------

# Configuration Connection instance Influx
connection = connection_influx
db = 'logs'              # Database

# Connection sur Influx
# https://influxdb-python.readthedocs.io/en/latest/api-documentation.html
# https://github.com/influxdata/influxdb-python/pull/453
client = InfluxDBClient(host=connection['host'],
                        uri=connection['uri'],
                        port=443,
                        database=db,
                        proxies=connection['proxies'],
                        ssl=True,
                        headers=connection['headers'],
                        verify_ssl=False)

print("Connection sur : {} \n Database: {}".format(connection['uri'], db))


## ATTENTION SVP !
# suppress_shards(get_incorrect_shards(nbdays=3, dbtodelete="telegraf"), limit=40)

input("\nShow TAGS : Press Key to continue")
show_tags_key()

input("\nShow FIELDS : Press Key to continue")
show_fields_key()

# Get Measurements on DB
msrmts = get_measurements()

input("\nShow SERIES : Press Key to continue")
get_series_from_measurements(msrmts)

input("\nShow DATA : Press Key to continue")
count_data_from_measurements(msrmts, time="5m")
