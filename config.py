# -*- coding: utf-8 -*-
import os
import datetime

from dateutil.relativedelta import relativedelta

class Config:
    DEBUG = False
    USE_AWS = False
    USE_RADGE = True

    BASE_DIR = os.environ['SC_DIR']
    GA_CLIENT_SECRET = os.path.join(BASE_DIR, '_data_connectors/ga/client_secret.json')
    STORAGE_FILE = os.path.join(BASE_DIR, '_data_connectors/ga/storage.dat')
    #GSC_SCOPE = 'https://www.googleapis.com/auth/webmasters.readonly'
    GA_SCOPE = 'https://www.googleapis.com/auth/analytics.readonly'
    REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

    GA_PROFILES = [('name','1234567')]

    # dates should be in the format of YYYY-MM-DD
    current_date = datetime.date.today()
    # first day of the previous month
    START_DATE = current_date + relativedelta(day=1, months=-48)
    # last day of the previous month
    END_DATE = current_date + relativedelta(day=1, days=-1)

    DB_NAME = 'corvidae_db'
    DB_GA_TABLE = 'corvidae_ga_medium'
    DB_FORECAST_TABLE = 'corvidae_forecast'  

    if USE_AWS:
        DB_USER = os.environ['CORVIDAE_AWS_USER']
        DB_PSW = os.environ['CORVIDAE_AWS_PSW']
        HOST_URL = 'corvidae-db.ciuleg8pnajz.eu-west-1.rds.amazonaws.com'
    if USE_RADGE:
        DB_USER = os.environ['RADGE_DB_USER']
        DB_PSW = os.environ['RADGE_DB_PSW']
        HOST_URL = os.environ['RADGE_DB_HOST']
        DB_NAME = 'radgedb'
        GA_CLIENT_SECRET = os.path.join(BASE_DIR, 'home/queryclick/apps/radge/ga/client_secrets.json')
        STORAGE_FILE = os.path.join(BASE_DIR, 'home/queryclick/apps/radge/ga/analytics.dat')
    else:
        DB_USER = os.environ['CORVIDAE_DB_USER']
        DB_PSW = os.environ['CORVIDAE_PSW']
        HOST_URL = 'localhost'

    LOG_FILE = 'logs/fcast.log'
