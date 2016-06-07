import sys
import os

import csv
#import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
#import statsmodels.api as sm
import rpy2.robjects as robjects
from rpy2.robjects import pandas2ri

import r_holtwinters_forecast
from config import Config

config = Config()
#pandas2ri.activate()

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
	df = pd.read_sql(config.DB_GA_TABLE,db_connection)
	
	start_date = df.date.min().strftime('%Y-%m-%d') #'2015-06-01'
	historic_sessions = df['sessions'].tolist()
	historic_revenue = df['revenue'].astype('float').tolist()

	results = r_holtwinters_forecast.main(historic_sessions,start_date)
	mean = pandas2ri.ri2py(results[0][1])
	lower_bounds = pandas2ri.ri2py(results[0][5])
	upper_bounds = pandas2ri.ri2py(results[0][4])

	data_frame = pd.concat([pd.DataFrame(upper_bounds,columns=['upper_85','upper_90'])\
		,pd.DataFrame(lower_bounds,columns=['lower_85','lower_90'])],axis=1)
	data_frame['mean'] = mean

if __name__ == '__main__':
  main('TRU')