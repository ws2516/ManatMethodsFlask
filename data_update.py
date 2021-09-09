import update_with_df
from update_with_df import write_to_sheet
import pandas as pd

import models
from models import NBA, MLB, WNBA, NSL, AAL

def update_all():
	try:
		update_with_df.write_to_sheet(NBA.run(),'NBA')
	except:
		continue
	
	try:
		update_with_df.write_to_sheet(MLB.run(),'MLB')
	except:
		continue
	
	try:
		update_with_df.write_to_sheet(WNBA.run(),'WNBA')
	except:
		continue
	
	try:
		update_with_df.write_to_sheet(NSL.run(),'NSL')
	except:
		continue
	
	try:
		update_with_df.write_to_sheet(AAL.run(),'AAL')
	except:
		continue
	
	return 'Done'

print(update_all())
