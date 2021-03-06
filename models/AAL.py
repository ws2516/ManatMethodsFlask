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
    #print(jsonData)
    for alpha in jsonData['events']:
        gameday = (alpha['tsstart'][:10])
        if (gameday == str(date.today())):
        	print ('Gathering %s data: %s @ %s' %(alpha['sportname'],alpha['participantname_away'],alpha['participantname_home']))
        	alpha_df = json_normalize(alpha).drop('markets',axis=1)
        	for beta in alpha['markets']:
        		#print(beta['selections']) #merge "getOdds" with this parse
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

def searchingForGame(jsonData):
	results_df = pd.DataFrame()
	alpha = jsonData['events'][0]
	gameday = alpha['tsstart'][:10]
	today = str(date.today())
	return today == gameday

def gameToday():
	jsonData_fanduel_epl = requests.get('https://sportsbook.fanduel.com/cache/psmg/UK/56609.3.json').json()
	boolean = searchingForGame(jsonData_fanduel_epl)
	return boolean

def build(oddsDataFrame,dataInput): #NEEDS WORK !!!!!!!
  betting = []
  for i in range(len(oddsDataFrame.iloc[:,0].values)):
    betName = oddsDataFrame.iloc[:,1].values[i]
    game = oddsDataFrame.iloc[:,0].values[i]
    for i in oddsDataFrame.iloc[i,2:].values:
      if i!=None:
        betting += [betFunction(game, betName,i, GoalsLookup)]
  df = pd.DataFrame(betting).dropna()
  df = df.reset_index()
  df.columns = ['Bet Number','Game','Team','Payout','Type']
  return df
  
def getOdds(listing):
  bets = []
  #print(len(listing))
  for game in listing:
  	for i in game['eventmarketgroups'][0]['markets']:
  		#print(i['name'])
  		betName = [game['externaldescription'], i['name']]
  		if i['name'] == 'Moneyline':
  			for i in i['selections']:
  				betName+=[[i['name'], 1+(i['currentpriceup']/i['currentpricedown'])]] #, i['currenthandicap']
  		bets += [betName]
  return bets

def fetch():
  try:
  	jsonData_fanduel_epl = requests.get('https://sportsbook.fanduel.com/cache/psmg/UK/56609.3.json').json() #gives the game id
  except:
  	print('Not a problem, the XHR has been changed for the EPL, go ahead and fix that then run again')
  epl = parse_data(jsonData_fanduel_epl)
  print(epl)
  EPL = pd.DataFrame(epl)[['eventname','tsstart','idfoevent.markets']]
  EPL.columns = ['Teams','Date','EventID']
  listing = []
  for i in np.unique(EPL.EventID.values): 
    listing.append((fullSet(i)))
  df = (pd.DataFrame(getOdds(listing)))
  df.columns = ['GameName', 'Type', 'HomeTeamandOdds', 'DrawOdds', 'AwayTeamandOdds']
  df = df[df.Type=='Moneyline']
  #df = df[df.GameName != 'Shrewsbury v Lincoln']
  probabilities = fetchName()
  #print(probabilities)
  
  #check if all of them are there
  valued = []
  #print(probabilities.gameNum.values)
  for i in np.unique(probabilities.gameNum.values):
  	newdf = probabilities[probabilities.gameNum == i]
  	valued += [newdf.ID.values[1][:]]
  	#print(valued)
  sorting = np.sort(valued)
  indices, counterArray, soughtGameArray = [], [], []
  counter = 0
  gamed = []
  
  #print((len(df.GameName.values), len(sorting)))
  for i in (df.GameName.values):
  	temp = []
  	for j in np.unique(sorting):
  		temp += [tryMatch(i,j)]
  	#print(temp)
  	sought = (sorting[temp.index(np.max(temp))])
  	soughtgameNum = probabilities[probabilities.ID == sought].gameNum.values[0]
  	counterArray += [counter]
  	soughtGameArray += [soughtgameNum]
  	counter += 1
  	
  fixed = pd.DataFrame({'sought':soughtGameArray, 'linked':counterArray}).sort_values(['sought'])
  #print(fixed)
  linker = []
  
  for i in fixed.linked.values:
  	linker += [i]
  	linker += [i]
  	linker += [i]
  #print(len(probabilities['gameNum']), len(linker))
  probabilities['gameNum'] = linker
  #print(probabilities)
  
  array ,counter = [], 0
  for i in probabilities.gameNum.values:
  	#print(counter)
  	if counter%3 == 0:
  		indexed = probabilities.gameNum.values[counter]
  		#print(df.HomeTeamandOdds.values[indexed][-1])
  		valued = df.HomeTeamandOdds.values[i][-1]
  		array+= [valued]
  		counter = counter+1
  	elif counter%3 == 1:
  		indexed = probabilities.gameNum.values[counter]
  		print(df.HomeTeamandOdds.values[indexed][-1])
  		valued = df.DrawOdds.values[i][-1]
  		array+= [valued]
  		counter = counter+1
  	else:
  		indexed = probabilities.gameNum.values[counter]
  		valued = df.AwayTeamandOdds.values[i][-1]
  		array += [valued]
  		counter = counter+1
  EV = []
  for i in range(len(array)):
  	EV += [probabilities.Probabilities.values[i]*array[i]]
  #print(array, probabilities.ID.values,probabilities )
  Result = pd.DataFrame({'Team':probabilities.ID.values, 'Probability': probabilities.Probabilities.values, 'Odds':array, 'EV':EV})
  #print(Result)
  Bet = Result[Result.EV >1.07]
  kelly = [Kelly(Bet.Odds.values[i], Bet.Probability.values[i]) for i in range(len(Bet.Probability.values))]
  #print(len(Bet.Team.values), len(kelly),  len(Bet.Odds.values))
  Betting = pd.DataFrame({'Bet State Chosen':Bet.Team.values, 'Kelly Criterion Suggestion': kelly, 'Payouts (per Dollar)':Bet.Odds.values})
  #Betting.columns = ['Bet State Chosen', 'Kelly Criterion Suggestion', 'Probability Spread','Payouts (per Dollar)']
  return Betting
  
def fetchName(): 
  url = 'https://projects.fivethirtyeight.com/soccer-predictions/a-league/'
  #print('hello')
  page_response = requests.get(url, timeout=10, headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9,fr;q=0.8,ro;q=0.7,ru;q=0.6,la;q=0.5,pt;q=0.4,de;q=0.3',
    'cache-control': 'max-age=0',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'})
  page_content = BeautifulSoup(page_response.content, "html.parser")
  navigate = page_content.findAll('div', class_="games-container upcoming")[0]
  Today = navigate.findAll('tbody')
  teams, prob = [], []
  for i in Today:
  	#print(i.find('div').text)
  	if (i.find('div').text == str(date.today().strftime("%-m/%-d"))): #this is to be changed
  	  #(date.today()).strftime("%m/%d"))
  	  home = i.findAll('td', class_ = "team")[0]['data-str']
  	  away = i.findAll('td', class_ = "team")[1]['data-str']
  	  teams += [home, 'Draw ' + str(home)+ ' v ' +str(away),away]
  	  prob +=[float(j.text[:-1])/100 for j in i.findAll('td', class_="prob")]
  #print(teams)
  indexed = []
  for i in range(int(len(teams)/3)):
  	indexed += [i]*3
  epl = pd.DataFrame({'ID':teams, 'Probabilities':prob, 'gameNum':indexed })
  #print(epl)
  return epl

def oddstoPayout(odds,dollarsIn):
  if odds<0:
    multiplier = 1/(abs(odds/100))
    return dollarsIn + dollarsIn*multiplier
  else:
    multiplier = odds/100
    return dollarsIn + dollarsIn*multiplier

def Kelly(oddsDecimal, probability):
  return (oddsDecimal*probability - (1-probability))/oddsDecimal
	
def picks(): #this needs some work/checking
	result = fetch().round(decimals=2)
	print(result.to_markdown())
	resulting = result[['Bet State Chosen', 'Kelly Criterion Suggestion','Payouts (per Dollar)']]
	resulting['League'] = ['ELO']*len(resulting['Bet State Chosen'])
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
	
