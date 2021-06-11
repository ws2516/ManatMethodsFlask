import flask
import gunicorn
import gspread
import tabulate
import os
import data_pipeline

from flask import Flask, request, render_template, session, redirect
from flask import send_from_directory

app = flask.Flask(__name__, template_folder='templates', static_folder = 'assets')


@app.route('/', methods=['GET', 'POST'])
def main():
    if flask.request.method == 'GET':

        return(flask.render_template('index.html'))
        
    if flask.request.method == 'POST':
    	
    	league_name = flask.request.form['store_name']

    	choices = data_pipeline.go(league_name)
    	
    	if len(choices) == 0:
    		
    		messaged = "All bets are below even EV right now! Come back another time, scripts run every 30 minutes!"
    	
    	else:
    	
    		messaged = data_pipeline.webify(choices)
    	
    	return render_template('index.html', table = messaged, league = league_name)


@app.route('/FutureProjects')
def further_suggestions():
	return flask.render_template('FutureProjects.html')


@app.route('/SignUp', methods=['GET', 'POST'])
def sign_up_sheet():

    return(flask.render_template('SignUp.html'))
    
@app.errorhandler(500)
def pageNotFound(error):
    return flask.render_template('505.html')

if __name__ == '__main__':
    app.run()

    
