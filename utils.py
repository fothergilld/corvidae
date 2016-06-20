import argparse
import httplib2
import smtplib

from apiclient.discovery import build
from oauth2client.tools import run_flow, argparser
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc

from config import Config

config = Config()
db_connector = 'mysql://%s:%s@localhost/%s' % (config.DB_USER, config.DB_PSW,config.DB_NAME)
engine = create_engine(db_connector)

# create a configured "Session" class
Session = sessionmaker(bind=engine)
session = Session()

class AuthenticationHandler(object):
    flow = flow_from_clientsecrets(
        config.GA_CLIENT_SECRET,
        scope=config.GA_SCOPE,
        redirect_uri=config.REDIRECT_URI
    )
    storage_file = Storage(config.STORAGE_FILE)
    credentials = storage_file.get()

    if credentials is None or credentials.invalid:
        parser = argparse.ArgumentParser(parents=[argparser])
        flags = parser.parse_args(['--noauth_local_webserver'])
        credentials = run_flow(
            flow=flow,
            storage=storage_file,
            flags=flags
        )

    @classmethod
    def ga_service_build(cls):
        credentials_auth = cls.credentials.authorize(httplib2.Http())
        return build('analytics', 'v3', http=credentials_auth)

    @classmethod
    def gsc_service_build(cls):
        credentials_auth = cls.credentials.authorize(httplib2.Http())
        return build('webmasters', 'v3', http=credentials_auth)

def GaDataTidy(data_object,client_name,ga_profile_id):
    rows = data_object.get('rows')
    headers = data_object.get('columnHeaders')
    heads = []
    for i in range(0,len(headers)):
         heads.append(headers[i]['name'])
    # put GA data into dataframe
    df = pd.DataFrame(rows,columns=heads)
    df['client_name']  = client_name
    df['ga_id']  = ga_profile_id
    # match column names to destination db field names
    df.rename(columns={'ga:yearMonth': 'date','ga:sessions': 'sessions','ga:medium': 'medium',\
            'ga:transactions': 'transactions','ga:transactionRevenue': 'revenue',\
            'ga:goal1Completions': 'goalCompletions1'}, inplace=True)
    df['date'] = pd.to_datetime(df['date'],format="%Y%m")
    df.replace(r'\s+',np.nan,regex=True).replace('',np.nan)
    return df

class DbHelpers(object):

    @staticmethod
    def insert_or_update(model, data):
        for row in data:
            instance = model(**row)
            session.add(instance)
            try:
                session.commit()
            except exc.IntegrityError as e:
                if e.orig.args[0] == 1062:
                    session.rollback()
                    model.update(row)
        session.close()

