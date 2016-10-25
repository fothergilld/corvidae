import sys
import os
import argparse
from dateutil.relativedelta import relativedelta
import logging
import csv

import numpy as np
import pandas as pd
import readline
import rpy2.robjects as robjects
from rpy2.robjects import pandas2ri

from models import ForecastData
from utils import DbHelpers
import r_forecast
from config import Config

config = Config()

def main(args):
    """
    Loads data from local DB and creates forecast using Holt Winters method.  The HW
       method is implemented in R.

    Args:
      client_name: The name as it exists in the store of Google Analytics data
      medium: The medium for which to forecast 
      metric: The metric for which to forecast
      client_name: The client to produce a forecast for
      date_from: The starting date to forecast from.  Used as a reference to identify the forecast points

    Returns:
      forecast_data: A pandas dataframe containing forecast data for 24 future periods, with the following columns:
      - sessions (integer)
      - revenue (float)
      - transactions (integer)
      - completions (integer)
    """

    logging.basicConfig(filename=config.LOG_FILE, level=logging.DEBUG,
                        format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    db_connection = 'mysql://%s:%s@%s/%s' % (config.DB_USER, config.DB_PSW, config.HOST_URL, config.DB_NAME)
    sql_query = 'SELECT * FROM %s WHERE client_name = "%s" \
                 AND date <"%s" AND medium = "%s" \
                 ORDER BY date asc' % (config.DB_GA_TABLE,
                                       args.client_name,
                                       args.date_from,
                                       args.medium)
    df = pd.read_sql(sql_query, db_connection)

    if len(df) < 12:
        logging.warning('Not enough data in DB to run forecast for parameters {},{},{}'
                        .format(args.client_name,
                                args.metric,
                                args.medium))
        return
    else:
        start_date = df.date.min().strftime('%Y-%m-%d')
        historic_metric_data = df[args.metric].tolist()

        results = r_forecast.main(historic_metric_data, start_date)
        mean = pandas2ri.ri2py(results[0][1])
        lower_bounds = pandas2ri.ri2py(results[0][5])
        upper_bounds = pandas2ri.ri2py(results[0][4])

    data_frame = pd.concat([pd.DataFrame(upper_bounds, columns=['upper_85', 'upper_95']),
                            pd.DataFrame(lower_bounds, columns=['lower_85', 'lower_95'])], axis=1)

    first_fcast_date = df.date.max() + relativedelta(months=1)
    date_range = pd.date_range(first_fcast_date, periods=24, freq='MS')
    data_frame['fcast_start_date'] = args.date_from
    data_frame['date'] = date_range
    data_frame['medium'] = args.medium
    data_frame['metric'] = args.metric
    data_frame['mean'] = mean
    data_frame['ga_id'] = df['ga_id'][0]
    data_frame['client_name'] = args.client_name
    df_as_dicts = data_frame.T.to_dict().values()
    DbHelpers.insert_or_update(ForecastData, df_as_dicts)

    logging.info('Created {} period forecast using {} historic data points for parameters {},{},{}'
                 .format(len(data_frame),
                         len(historic_metric_data),
                         args.client_name,
                         args.metric,
                         args.medium))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("client_name")
    parser.add_argument("medium", choices=['organic', 'cpc'],
                        help='medium as per the google analytics naming convention')
    parser.add_argument("metric", choices=['sessions', 'revenue', 'transactions', 'goalCompletions1'],
                        help='metric as per the google analytics naming convention')
    parser.add_argument("date_from", help='date from which to forecast from (format YYYY-MM-DD)')
    args = parser.parse_args()
    main(args)
