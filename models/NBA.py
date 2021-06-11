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

def parse_data(jsonData):
    results_df = pd.DataFrame()
    for alpha in jsonData['events']:
        gameday = (alpha['tsstart'][:10])
        if (gameday == str(date.today())):
        	print ('Gathering %s data: %s @ %s' %(alpha['sportname'],alpha['participantname_away'],alpha['participantname_home']))
        	alpha_df = json_normalize(alpha).drop('markets',axis=1)
        	for beta in alpha['markets']:
        		beta_df = json_normalize(beta).drop('selections',axis=1)
        		beta_df.columns = [str(col) + '.markets' for col in beta_df.columns]
        		for theta in beta['selections']:
        			theta_df = json_normalize(theta)
        			theta_df.columns = [str(col) + '.selections' for col in theta_df.columns]
        		
        			temp_df = reduce(lambda left,right: pd.merge(left,right, left_index=True, right_index=True), [alpha_df, beta_df, theta_df])
        			results_df = results_df.append(temp_df, sort=True).reset_index(drop=True)
	
    return results_df #time right for <7 on prev day

def fullSet(eventID):
  return requests.get('https://sportsbook.fanduel.com//cache/psevent/UK/1/false/'+ str(eventID) + '.json').json()
  
def getOdds(listing):
  bets = []
  for game in listing:
  	for i in game['eventmarketgroups'][0]['markets']:
  		betName = [game['externaldescription'], i['name']]
  		if i['name'] == 'Moneyline':
  			for i in i['selections']:
  				betName+=[[i['name'], 1+(i['currentpriceup']/i['currentpricedown'])]] #, i['currenthandicap']
  		bets += [betName]
  return bets

def searchingForGame(jsonData):
	results_df = pd.DataFrame()
	alpha = jsonData['events'][0]
	gameday = alpha['tsstart'][:10]
	today = str(date.today())
	return today == gameday

def gameToday():
	jsonData_fanduel_epl = requests.get('https://sportsbook.fanduel.com/cache/psmg/UK/63747.3.json').json()
	boolean = searchingForGame(jsonData_fanduel_epl)
	return boolean

def fetch():
  try:
  	jsonData_fanduel_nba = requests.get('https://sportsbook.fanduel.com/cache/psmg/UK/63747.3.json').json() #gives the game id
  except:
  	print('Not a problem, the XHR has been changed for the NBA, go ahead and fix that then run again')
  epl = parse_data(jsonData_fanduel_nba)
  EPL = pd.DataFrame(epl)[['eventname','tsstart','idfoevent.markets']]
  EPL.columns = ['Teams','Date','EventID']
  listing = []
  for i in np.unique(EPL.EventID.values): 
    listing.append((fullSet(i)))
  df = (pd.DataFrame(getOdds(listing)))
  
  df.columns = ['GameName', 'Type', 'HomeTeamandOdds', 'AwayTeamandOdds']
  df = df[df.Type=='Moneyline']
  probabilities = fetchName()
  name, odds = [], []
  for i in range(len(df)):
  	name += [df.HomeTeamandOdds.values[i][0].split(' ')[-1]]
  	name += [df.AwayTeamandOdds.values[i][0].split(' ')[-1]]
  	odds += [df.HomeTeamandOdds.values[i][1]]
  	odds += [df.AwayTeamandOdds.values[i][1]]
  newest = pd.DataFrame({'ID':name,'Odds':odds})
  result = pd.merge(newest, probabilities, on = 'ID')
  Result = (probabilities.set_index('ID').join(newest.set_index('ID'))).reset_index()
  Result['EV'] = [Result.Probabilities.values[i] * Result.Odds.values[i] for i in range(len(Result))]
  Result['Team'] = Result.ID.values
  Result['Probability'] = Result.Probabilities.values
  Result = Result[['Team','Probability','Odds','EV']]
  Bet = Result[Result.EV >1.00]
  kelly = [Kelly(Bet.Odds.values[i], Bet.Probability.values[i]) for i in range(len(Bet.Probability.values))]
  Betting = pd.DataFrame({'Bet State Chosen':Bet.Team.values, 'Kelly Criterion Suggestion': kelly, 'Payouts (per Dollar)':Bet.Odds.values})
  return Betting
  
def fetchName(): 

  jsonData_fanduel_nba = requests.get('https://sportsbook.fanduel.com/cache/psmg/UK/64165.3.json').json() #gives the game id
  url = 'https://projects.fivethirtyeight.com/2021-nba-predictions/games/?ex_cid=rrpromo'
  page_response = requests.get(url, timeout=10, headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9,fr;q=0.8,ro;q=0.7,ru;q=0.6,la;q=0.5,pt;q=0.4,de;q=0.3',
    'cache-control': 'max-age=0',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'})
  page_content = BeautifulSoup(page_response.content, "html.parser")
  if datetime.today().hour >=3:
  	Today = page_content.findAll('section', class_="day")[0] #not sure what the issue is here
  else: 
  	Today = page_content.findAll('section', class_="day")[1] #not sure what the issue is here
  teams = [i['data-team'] for i in Today.findAll('tr', class_ = "tr team")]
  teamsToday = []
  for j in teams:
  	try:
  		teamsToday += [Today.find('td', class_ = "td text team " + str(j)).text]
  	except:
  		teamsToday += ['None']
  probabilitiesToday = [float(i.text[:-1])/100 for i in Today.findAll('td', class_="td number chance")]
  indexed = []
  for i in range(int(len(teamsToday)/2)):
  	indexed += [i]*2
  nba = pd.DataFrame({'ID':teamsToday, 'Probabilities':probabilitiesToday, 'gameNum':indexed })
  return nba

def oddstoPayout(odds,dollarsIn):
  if odds<0:
    multiplier = 1/(abs(odds/100))
    return dollarsIn + dollarsIn*multiplier
  else:
    multiplier = odds/100
    return dollarsIn + dollarsIn*multiplier

def Kelly(oddsDecimal, probability):
  return (oddsDecimal*probability - (1-probability))/oddsDecimal

def picks():
	result = fetch().round(decimals=2)
	resulting = result[['Bet State Chosen', 'Kelly Criterion Suggestion','Payouts (per Dollar)']]
	resulting['League'] = ['NBA']*len(resulting['Bet State Chosen'])
	resulting['Date'] = [str(date.today())]*len(resulting['Bet State Chosen'])
	return resulting

def run():
	if gameToday():
		try:
			return picks()
		except:
			return pd.DataFrame({})
	else:
		return pd.DataFrame({})