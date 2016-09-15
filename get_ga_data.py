import argparse
from datetime import datetime
from dateutil.relativedelta import relativedelta

from utils import AuthenticationHandler, GaDataTidy, DbHelpers
from config import Config
from models import GaData

config = Config()


def main(args):
    service = AuthenticationHandler.ga_service_build()

    ga_profile = 'ga:' + args.ga_id

    execution_date = datetime.strptime(args.execution_date, '%Y-%m-%d')
    end_date = execution_date - relativedelta(days=1)
    start_date = end_date - relativedelta(day=1)
    historic_data = ga_monthly_channel_data(service, ga_profile, start_date.strftime('%Y-%m-%d'),
                                            end_date.strftime('%Y-%m-%d')).execute()
    formatted_dataframe = GaDataTidy(historic_data, args.client_name, args.ga_id)
    df_as_dicts = formatted_dataframe.T.to_dict().values()
    DbHelpers.insert_or_update(GaData, df_as_dicts)


def get_profile_ids(service):
    """Uses Management API to get available Profile IDS for the current user

    Args:
        service: The service object built by the Google API Python client library.

    Returns:
        A list of tuples with the profile ID and name.  None if user has access to zero profiles
    """
    account_data = service.management().accounts().list().execute()
    accounts = []
    for single_account in account_data['items']:
        account_name = single_account['name']
        account_id = single_account['id']
        account_detail = (account_name, account_id)
        accounts.append(account_detail)
    return accounts


def ga_monthly_channel_data(service, profile, start_date, end_date, segment=None):
    """Returns a query object to retrieve data from the Core Reporting API.

    Args:
      service: The service object built by the Google API Python client library.
      table_id: str The table ID form which to retrieve data.
    """
    return service.data().ga().get(
        ids=profile,
        start_date=start_date,
        end_date=end_date,
        metrics='ga:sessions,ga:transactions,ga:transactionRevenue,ga:goal1Completions',
        dimensions='ga:yearMonth,ga:medium',
        #sort='ga:visits',
        filters='ga:medium==organic,ga:medium==cpc',
        segment=segment,
        start_index='1',
        samplingLevel='HIGHER_PRECISION',
        max_results='10000')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("client_name")
    parser.add_argument("ga_id")
    parser.add_argument("execution_date", help='Day on which report is being executed (format YYYY-MM-DD)')
    parser.add_argument("report_period", choices=['LAST_MONTH'], help='choose from LAST_MONTH')

    args = parser.parse_args()
    main(args)
