import requests
import datetime
import pandas as pd
import numpy as np
import tabulate
import time
import datetime
import bs4

from datetime import datetime, timedelta, date

from pandas import json_normalize
from functools import reduce

from bs4 import BeautifulSoup
  
def fetchName(): 
  url = 'https://projects.fivethirtyeight.com/soccer-predictions/matches/'
  page_response = requests.get(url, timeout=10, headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9,fr;q=0.8,ro;q=0.7,ru;q=0.6,la;q=0.5,pt;q=0.4,de;q=0.3',
    'cache-control': 'max-age=0',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'})
  page_content = BeautifulSoup(page_response.content, "html.parser")
  game_time = page_content.findAll('td', class_="datetime")
  league_name_array = page_content.findAll('div', class_="league-link")
  match_array = page_content.findAll('td', class_="match")

  #boolean check vars
  today = game_time[0].findAll('div', class_="date-league")[-1].text

  #init arrays
  game_today, league_names, home, away, home_win, away_win, tie = [], [], [], [], [], [],[]
  for i in range(len(game_time)):
      dated = game_time[i].findAll('div', class_="date-league")[-1].text
      if (dated == today):
        game_today.append(dated + ' at ' + str(game_time[i].findAll('div')[-1].text) + " EST")
        league_names.append(league_name_array[i].text)
        print(len(match_array), i)
        specific_match = match_array[i]
        

        home_str = specific_match.findAll('div', class_='name')[0].text
        home_prob = specific_match.findAll('td', class_='prob')[0].text

        away_str = specific_match.findAll('div', class_='name')[0].text
        away_prob = specific_match.findAll('td', class_='prob')[2].text

        tied = specific_match.findAll('td', class_='prob')[1].text

        home.append(home_str)
        home_win.append(home_prob)

        away.append(away_str)
        away_win.append(away_prob)

        tie.append(tied)

  
  output = pd.DataFrame({'Date':game_today, 'League':league_names, 'Home': home, 'Home Win':home_win, 'Away':away, "Away Win": away_win, 'Tie': tie})
  return output


print(searching("fanduel Benevento Lecce Serie B"))
