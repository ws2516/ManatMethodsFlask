import update_with_df
from update_with_df import write_to_sheet
import pandas as pd

import models
from models import NBA, MLB, WNBA, NSL, AAL

def update_all():
	update_with_df.write_to_sheet(NBA.run(),'NBA')
	update_with_df.write_to_sheet(MLB.run(),'MLB')
	update_with_df.write_to_sheet(WNBA.run(),'WNBA')
	update_with_df.write_to_sheet(NSL.run(),'NSL')
	update_with_df.write_to_sheet(AAL.run(),'AAL')
	return 'Done'

print(update_all())
