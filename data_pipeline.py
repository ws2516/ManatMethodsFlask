import update_with_df
from update_with_df import write_to_sheet
import pandas as pd


def go(store_name):
	if store_name == 'MLB':
		final_df = update_with_df.get_from_sheet('MLB')
	'''elif store_name == 'WNBA':
		final_df = update_with_df.get_from_sheet('WNBA')'''
	elif store_name == 'NBA':
		final_df = update_with_df.get_from_sheet('NBA')
	elif store_name == 'NSL':
		final_df = update_with_df.get_from_sheet('NSL')
	elif store_name == 'AAL':
		final_df = update_with_df.get_from_sheet('AAL')
	return final_df
	
def webify(df):
	return df.to_html()
