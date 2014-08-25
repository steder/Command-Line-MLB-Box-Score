#!/usr/bin/python

import re
import sys
from StringIO import StringIO
import urllib
import urllib2
import gzip
import json
import argparse
import dateutil.parser

import requests

# Replace with your access token
access_token = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# Replace with your bot name and email/website to contact if there is a problem
# e.g., "mybot/0.1 (https://erikberg.com/)"
user_agent = "mybot/0.1 (https://erikberg.com/)"

parser = argparse.ArgumentParser(description='Command line MLB box scores')
parser.add_argument('-d','--date', help='Date of game format YYYYMMDD', required=True)
parser.add_argument('-t','--team', help='Team name i.e. Cardinals', required=True)

args = parser.parse_args()
argsdict = vars(args)


# See https://erikberg.com/api/methods Request URL Convention for
# an explanation
def build_event_url(host, sport, method, id, format, parameters):
    path = "/".join(filter(None, (sport, method, id)));
    url = "https://" + host + "/" + path + "." + format
    if parameters:
        paramstring = urllib.urlencode(parameters)
        url = url + "?" + paramstring
    return url

HOST = "erikberg.com"
SPORT = 'mlb'


def make_api_request(resource, resource_id=None, parameters=None):
    """
    return an erikberg.com JSON document
    """
    format = "json"

    # with requests:
    headers = {"Authorization": "Bearer " + access_token,
               "User-Agent": user_agent,
               "Accept-encoding": "gzip",}
    r = requests.get(build_event_url(HOST, SPORT, resource, resource_id, format, parameters), headers=headers)
    return r.json()


def setup_event_id():
    data = make_api_request("events", parameters={'date': argsdict['date']})
    #print "data:", data
    event_id = get_event_id(data)
    if event_id == None:
        print "Drats. Either this game has no box score or you mistyped your team name."
    else:
        return event_id


def get_event_id(events):
    # Loop through each Event (https://erikberg.com/api/objects/event)
    for evt in events['event']:
        # Filter by team name
        if re.search(argsdict['team'], str(evt['home_team'])) or re.search(argsdict['team'], str(evt['away_team'])):
            if evt['event_status'] == 'completed':
                event_id = evt['event_id']
                return event_id


def get_box_score():
    event_id = setup_event_id()
    data = make_api_request("boxscore", resource_id=event_id)
    #print "box score data:", data
    print_result(data)


def print_result(box_score):
    # Parses the JSON content and returns a reference
    # to MLB Box Score (https://erikberg.com/api/methods/mlb-box-score)


    # Date of game
    date = dateutil.parser.parse(box_score["event_information"]["start_date_time"])

    #Game info
    #temperature = box_score["event_information"]["temperature"]
    stadium = box_score["event_information"]["site"]["name"]
    #attendance = box_score["event_information"]["attendance"]
    #duration = box_score["event_information"]["duration"]

    # Team names
    home_team = box_score["home_team"]["last_name"]
    away_team = box_score["away_team"]["last_name"]

    # Runs
    home_team_runs = box_score["home_batter_totals"]["runs"]
    away_team_runs = box_score["away_batter_totals"]["runs"]

    # Hits
    home_team_hits = box_score["home_batter_totals"]["hits"]
    away_team_hits = box_score["away_batter_totals"]["hits"]

    # Errors
    home_team_errors = 1
    away_team_errors = 0

    # Team win
    home_team_win = None
    away_team_win = None

    baseball_character = u"\u26BE"

    if home_team_runs > away_team_runs:
        home_team_win = "[x]"
        away_team_win = "[ ]"
    else:
        home_team_win = "[ ]"
        away_team_win = "[x]"

    print "\n" + baseball_character + ' ' + stadium + ' ' + format(date.strftime("%A, %B %e, %Y")) + "\n"

    print "{: <5} {: <12} {: <5} {: <5} {: <5}".format(
            home_team_win,
            home_team,
            home_team_runs,
            home_team_hits,
            home_team_errors)

    print "{: <5} {: <12} {: <5} {: <5} {: <5}\n".format(
            away_team_win,
            away_team,
            away_team_runs,
            away_team_hits,
            away_team_errors)


get_box_score()
