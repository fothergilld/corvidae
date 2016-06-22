# -*- coding: utf-8 -*-
import os
import datetime

from dateutil.relativedelta import relativedelta

class Config:
    DEBUG = False
    TESTING = False

    BASE_DIR = os.environ['SC_DIR']
    GA_CLIENT_SECRET = os.path.join(BASE_DIR, '_data_connectors/ga/client_secret.json')
    STORAGE_FILE = os.path.join(BASE_DIR, '_data_connectors/ga/storage.dat')
    #GSC_SCOPE = 'https://www.googleapis.com/auth/webmasters.readonly'
    GA_SCOPE = 'https://www.googleapis.com/auth/analytics.readonly'
    REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

    GA_PROFILES = [('TRU','13292137')]

    # dates should be in the format of YYYY-MM-DD
    current_date = datetime.date.today()
    # first day of the previous month
    START_DATE = current_date + relativedelta(day=1, months=-48)
    # last day of the previous month
    END_DATE = current_date + relativedelta(day=1, days=-1)

    DB_NAME = 'corvidae_db'
    DB_GA_TABLE = 'ga_data'
    DB_FORECAST_TABLE = 'forecast_data'  
    DB_USER = os.environ['CORVIDAE_DB_USER']
    DB_PSW = os.environ['CORVIDAE_PSW']

    LOG_FILE = 'logs/fcast.log'
