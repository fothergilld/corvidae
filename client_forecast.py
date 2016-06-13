import sys
import os
from dateutil.relativedelta import relativedelta

import csv
import numpy as np
import pandas as pd
import readline
import rpy2.robjects as robjects
from rpy2.robjects import pandas2ri

from models import ForecastData
from utils import DbHelpers
import r_holtwinters_forecast
from config import Config

config = Config()

def main(client_name):
	"""
	Loads data from local DB and creates forecast using Holt Winters method.  The HW \
	   method is implemented in R.

	Args:
		client_name: The name as it exists in the store of Google Analytics data

	Returns:
		forecast_data: A pandas dataframe containing forecast data for 24 future periods, with the following columns:
		- sessions (integer)
		- revenue (float)
		- transactions (integer)
		- completions (integer)
	"""

	db_connection = 'mysql://%s:%s@localhost/%s' % (config.DB_USER, config.DB_PSW,config.DB_NAME)
	sql_query = 'select * from %s where client_name = "%s"' % (config.DB_GA_TABLE, client_name)
	df = pd.read_sql(sql_query,db_connection)
	
	start_date = df.date.min().strftime('%Y-%m-%d') #'2015-06-01'
	historic_sessions = df['sessions'].tolist()
	historic_revenue = df['revenue'].astype('float').tolist()

	results = r_holtwinters_forecast.main(historic_sessions,start_date)
	mean = pandas2ri.ri2py(results[0][1])
	lower_bounds = pandas2ri.ri2py(results[0][5])
	upper_bounds = pandas2ri.ri2py(results[0][4])

	data_frame = pd.concat([pd.DataFrame(upper_bounds,columns=['sessions_upper_85','sessions_upper_95'])\
		,pd.DataFrame(lower_bounds,columns=['sessions_lower_85','sessions_lower_95'])],axis=1)

	first_fcast_date = df.date.max() +  relativedelta(months=1)
	date_range = pd.date_range(first_fcast_date, periods=24, freq='M')
	data_frame['date'] = date_range
	data_frame['medium'] = 'organic'
	data_frame['sessions_mean'] = mean
	data_frame['ga_id'] = df['ga_id']
	data_frame['client_name'] = df['client_name']
	df_as_dicts = data_frame.T.to_dict().values()
	DbHelpers.insert_or_update(ForecastData, df_as_dicts)


if __name__ == '__main__':
  main('test')