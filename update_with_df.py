import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
from datetime import datetime
import pandas as pd
import os

def write_to_sheet(dataframe, sheet_name):
	creds = ServiceAccountCredentials.from_json_keyfile_name('./creds.json')
	client = gspread.authorize(creds)
	sheet = client.open("ManatScrapeData").worksheet(sheet_name)
	sheet.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())
	return 'Done'

def get_from_sheet(sheet_name):
	creds = ServiceAccountCredentials.from_json_keyfile_name('./creds.json')
	client = gspread.authorize(creds)
	sheet = client.open("ManatScrapeData").worksheet(sheet_name)
	table = sheet.get_all_values()
	try:
		headers = table.pop(0)
		return pd.DataFrame(table, columns=headers)
	except:
		return pd.DataFrame({})

