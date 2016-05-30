import sys

from utils import AuthenticationHandler,GaDataTidy #, DbHelpers
from config import Config
from sqlalchemy import create_engine

config = Config()

def main():
	disk_engine = create_engine('sqlite:///ga_daily_channel.db')
	service = AuthenticationHandler.ga_service_build()
	accounts = get_profile_ids(service)

	#import ipdb; ipdb.set_trace()
	for profile in config.GA_PROFILES:
	 	ga_profile = 'ga:' + profile[1]
	 	historic_data = ga_daily_channel_data(service,ga_profile,config.START_DATE.strftime('%Y-%m-%d')\
	 	,config.END_DATE.strftime('%Y-%m-%d')).execute()

	tidy = GaDataTidy(historic_data)
	import ipdb; ipdb.set_trace()
	tidy.to_sql('data', disk_engine, if_exists='append')

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
		account_detail = (account_name,account_id)
		accounts.append(account_detail)
	return accounts

def ga_daily_channel_data(service, profile, start_date, end_date,segment=None):
  """Returns a query object to retrieve data from the Core Reporting API.

  Args:
    service: The service object built by the Google API Python client library.
    table_id: str The table ID form which to retrieve data.
  """
  return service.data().ga().get(
      ids=profile,
      start_date=start_date,
      end_date=end_date,
      metrics='ga:sessions,ga:transactions,ga:transactionRevenue',
      dimensions='ga:date,ga:medium',
      #sort='ga:visits',
      filters='ga:medium==organic',
      segment=segment,
      start_index='1',
      samplingLevel='HIGHER_PRECISION',
      max_results='10000')

if __name__ == '__main__':
  main()