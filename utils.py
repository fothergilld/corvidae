import argparse
import httplib2
import smtplib

from apiclient.discovery import build
from oauth2client.tools import run_flow, argparser
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
import pandas as pd

from config import Config

config = Config()

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

def GaDataTidy(data_object):
    rows = data_object.get('rows')
    headers = data_object.get('columnHeaders')
    heads = []
    for i in range(0,len(headers)):
         heads.append(headers[i]['name'])

    #put GA data into dataframe
    df = pd.DataFrame(rows,columns=heads)
    return df
    #convert sessions column to numeric format
    #df['sessions'] = pd.to_numeric(df['ga:sessions'])
    #df['client']  = profile_name
