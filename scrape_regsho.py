import io
import os
import pandas as pd
import requests
from datetime import datetime, timedelta
from pytz import timezone
from xone import calendar


BASE_URLS = [
	'http://regsho.finra.org/FNYXshvol{}.txt',
	'http://regsho.finra.org/FNQCshvol{}.txt',
	'http://regsho.finra.org/FNSQshvol{}.txt',
]
FILENAME = 'regsho_data.csv'
DELIMITER = '|'
FIELDNAMES = [
	'Date',
	'Symbol',
	'ShortVolume',
	'ShortExemptVolume',
	'TotalVolume',
	'Market',
]

def get_last_date():
	"""Get latest time from CSV.
	"""
	last_line = ''
	with open(FILENAME, 'r') as f:
		f.seek(0, 2)
		fsize = f.tell()
		f.seek(max (fsize-4096, 0), 0)
		lines = f.read().splitlines()
		last_line = lines[-1]
	last_date = last_line.split(DELIMITER)[0]
	last_date = datetime.strptime(last_date, '%Y%m%d')
	return last_date

def trading_dates(start_date, end_date):
	"""Get all trading dates.
	"""
	ust_calendar = calendar.USTradingCalendar()
	dates = pd.bdate_range(start=start_date, end=end_date)
	holidays = ust_calendar.holidays(start=start_date, end=end_date)
	trading_dates = dates.drop(holidays)
	return trading_dates.strftime('%Y%m%d')

def save_data(data, write_header=False):
	"""Append data to csv.
	"""
	with open(FILENAME, 'a') as f:
		data.to_csv(f, header=write_header, index=False, float_format='%.0f', sep=DELIMITER)

def get_data(date):
	# Request
	data = []
	for base_url in BASE_URLS:
		url = base_url.format(date)
		result = requests.get(url)
		content = result.content.decode('utf-8')
		datum = pd.read_csv(io.StringIO(content), sep='|')
		datum = datum.dropna()
		data.append(datum)
	data = pd.concat(data)
	data = data[FIELDNAMES]

	# Append data to csv
	save_data(data, write_header=(date == '20110301'))

	return data

if __name__ == '__main__':
	# Earliest data
	start_date = '3/1/2011'
	# Start date from last row in CSV
	start_date = datetime.strptime(start_date, '%m/%d/%Y')
	if os.path.isfile(FILENAME):
		start_date = get_last_date() + timedelta(days=1)
	start_date = start_date.strftime('%m/%d/%Y')

	# End date from EST date
	end_date = datetime.now(timezone('US/Eastern'))
	# Published after 8PM
	if end_date.hour < 20:
		end_date = end_date - timedelta(days=1)
	end_date = end_date.strftime('%m/%d/%Y')

	# Get all trading dates
	dates = trading_dates(start_date, end_date)

	for date in dates:
		# Get data
		get_data(date)

		print('Fetched {}'.format(date))
