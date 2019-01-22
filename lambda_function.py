import requests
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import MobileApplicationClient
import json
import datetime
import boto3
import json, os
from random import randint
from pytz import timezone
import time
import plotly.plotly as py
import plotly
import plotly.graph_objs as go

client_id = "22DB4F"
scope = ["sleep"]
client = MobileApplicationClient(client_id)
fitbit = OAuth2Session(client_id, client=client, scope=scope)
authorization_url = "https://www.fitbit.com/oauth2/authorize"
auth_url, state = fitbit.authorization_url(authorization_url)
#print("Visit this page in your browser: {}".cformat(auth_url))
callback_url = "https://127.0.0.1:8080/#access_token=eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyMkRCNEYiLCJzdWIiOiI2UUtLSjQiLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJyc2xlIiwiZXhwIjoxNTc5NjQ5NzgzLCJpYXQiOjE1NDgxMTM3ODN9.BX4sTf0-8TXK8r1hU70F9F2ghXtE-53onQgMCqKxFYY&user_id=6QKKJ4&scope=sleep&state=WDyClkPkZxi2nXAworKvzSYE5mOBMS&token_type=Bearer&expires_in=31536000"
fitbit.token_from_fragment(callback_url)
py.sign_in(username='rampally', api_key='dJT8FJlWVhfYXX9q5v1c')

def build_speechlet_response(title, output, reprompt_text, should_end_session):
	return {
		'outputSpeech':{
			'type':'PlainText',
			'text':output,
			'ssml':'<speak>' + output + '</speak>'
		},
		"directives":[
			{
				"type":"Alexa.Presentation.APL.RenderDocument",
				"token":"30990c41-18b6-46b5-931d-0dafd6a2ec29",
				"document":{
					"type":"APL",
					"version":"1.0",
					"theme":"auto",
					"import":[
						{
							"name":"alexa-layouts",
							"version":"1.0.0"
						}
					],
					"resources":[
						{
							"description":"Stock color for the light theme",
							"colors":{
								"colorTextPrimary":"#151920"
							}
						},
						{
							"description":"Stock color for the dark theme",
							"when":"${viewport.theme == 'dark'}",
							"colors":{
								"colorTextPrimary":"#f0f1ef"
							}
						}
					],
					"styles":{
						"textStyleBase":{
							"description":"Base font description; set color and core font family",
							"values":[
								{
									"color":"@colorTextPrimary",
									"fontFamily":"Amazon Ember Display"
								}
							]
						}
					},
					"layouts":{

					},
					"mainTemplate":{
						"parameters":[
							"payload"
						],
						"items":[
							{
								"type":"Container",
								"direction":"column",
								"width":"100vw",
								"height":"100vh",
								"items":[
									{
										"type":"Text",
										"text":"${payload.myDocumentData.title}"
									},
									{
										"type":"Image",
										 "source": "https://plot.ly/~rampally/0.png",
  								 		 "scale": "fill",
										 "width": 300,
										 "height": 300
									}
								]
							}
						]
					}
				},
				"datasources":{
					"myDocumentData":{
						"title":"This is a very simple sample"
					}
				}
			}
		],
		'card':{
			'type':'Simple',
			'title':"SessionSpeechlet - "        + str(title),
			'content':"SessionSpeechlet - "        + output
		},
		'reprompt':{
			'outputSpeech':{
				'type':'PlainText',
				'text':reprompt_text
			}
		},
		'shouldEndSession':should_end_session
	}

def build_response(session_attributes, speechlet_response):
	return {
		'version': '1.0',
		'sessionAttributes': session_attributes,
		'response': speechlet_response
	}

def get_fitbit_sleep_hours(date):
	r = fitbit.get('https://api.fitbit.com/1.2/user/-/sleep/date/' + date.strftime('%Y-%m-%d') + '.json')
	data = json.loads(r.text)
	hours = 0.0
	sleep_data = {}
	for each in data['sleep']:
		if(each['isMainSleep'] == True):
			td = datetime.timedelta(milliseconds=int(each['duration']))
			hours = round(td.seconds / 3600.0,2)
			for a in each['levels']['summary']:
				td = datetime.timedelta(minutes=int(each['levels']['summary'][a]['minutes']))
				sleep_data[str(a)] = round(td.seconds / 3600.0,2)
	return (hours, sleep_data)


def get_fitbit_sleep_goal():
	r = fitbit.get('https://api.fitbit.com/1/user/-/sleep/goal.json')
	data = json.loads(r.text)
	hours = round(int(data['goal']['minDuration']) / 60.0,2)
	return hours

def get_fitbit_sleep_times(date):
	r = fitbit.get('https://api.fitbit.com/1.2/user/-/sleep/date/' + date.strftime('%Y-%m-%d') + '.json')
	data = json.loads(r.text)
	start = ""
	end = ""
	for each in data['sleep']:
		if(each['isMainSleep'] == True):
			start_date = datetime.datetime.strptime(each['startTime'], "%Y-%m-%dT%H:%M:%S.%f")
			end_date = datetime.datetime.strptime(each['endTime'], "%Y-%m-%dT%H:%M:%S.%f")
			start = start_date.strftime("%I:%M %p")
			end = end_date.strftime("%I:%M %p")
			break
	return (start, end)

def get_fitbit_sleep_range(date_from, date_to):
	r = fitbit.get('https://api.fitbit.com/1.2/user/-/sleep/date/' + date_from.strftime('%Y-%m-%d') + '/' + date_to.strftime('%Y-%m-%d') + '.json')
	data = json.loads(r.text)
	deets = []
	for each in data['sleep']:
		if(each['type'] == "stages"):
			date = datetime.datetime.strptime(each['dateOfSleep'], "%Y-%m-%d")
			sleep_data = {}
			td = datetime.timedelta(milliseconds=int(each['duration']))
			hours = round(td.seconds / 3600.0,2)
			for a in each['levels']['summary']:
				td = datetime.timedelta(minutes=int(each['levels']['summary'][a]['minutes']))
				sleep_data[str(a)] = round(td.seconds / 3600.0,2)
			deets.append((date, (hours, sleep_data)))
	return deets

def lambda_handler(event, context):
	#client = boto3.client('sqs', aws_access_key_id = access_key, aws_secret_access_key = access_secret, region_name = region)
	intent_name = event['request']['intent']['name']
	if (intent_name == "sleepHours"):
		date = datetime.datetime.now(timezone('US/Central'))
		hours_slept = get_fitbit_sleep_hours(date)[0]
		sleep_goal = get_fitbit_sleep_goal()
		minutes = int(round((hours_slept * 60) % 60))
		hours = int(round(hours_slept))
		#make python graphs and send to s3 and multimodal

		values = []
		labels = ['Sleep Slept', 'Hours to Goal']
		colors = ['#E1396C', '#96D38C']
		if (hours_slept < sleep_goal):
			values=[hours_slept, sleep_goal-hours_slept]
		else:
			values=[hours_slept, 0]
		trace = go.Pie(labels=labels, values=values,
				   hoverinfo='label+percent', textinfo='value',
				   textfont=dict(size=20),
				   marker=dict(colors=colors,
							   line=dict(color='#000000', width=2)))
		try:
			py.iplot([trace], filename='styled_pie_chart')
		except:
			pass

		speech_text = 'You slept for '+ str(hours) +' hours and ' + str(minutes) + ' minutes last night'
		speechlet = build_speechlet_response("sample", speech_text, "", "True")
		return build_response({}, speechlet)
	if (intent_name == "sleepTimings"):
		date = datetime.datetime.now(timezone('US/Central'))
		time_slept,time_woke = get_fitbit_sleep_times(date)[0], get_fitbit_sleep_times(date)[1]
		hours_slept = get_fitbit_sleep_hours(date)[0]
		sleepData = get_fitbit_sleep_hours(date)[1]
		print(time_slept, time_woke, hours_slept, sleepData)
		#line graph of depth of sleep
		data = [go.Bar(
            x=['giraffes', 'orangutans', 'monkeys'],
            y=[20, 14, 23]
    	)]
		py.iplot(data, filename='basic-bar')
