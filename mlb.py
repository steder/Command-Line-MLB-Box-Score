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

# Replace with your access token
#access_token = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
access_token = "992c5bbd-c0a4-4f56-aaa9-238f5b4deabc"

# Replace with your bot name and email/website to contact if there is a problem
# e.g., "mybot/0.1 (https://erikberg.com/)"
user_agent = "mybot/0.1 (http://sawdust.io/)"

parser = argparse.ArgumentParser(description='Command line MLB box scores')
parser.add_argument('-d','--date', help='Date of game format YYYYMMDD', required=True)
parser.add_argument('-t','--team', help='Team name i.e. Cardinals', required=True)

args = parser.parse_args()
argsdict = vars(args)


def setup_event_id():
    # set the API method, format, and any parameters
    host = "erikberg.com"
    sport = 'mlb'
    method = "events"
    id = None
    format = "json"
    parameters = {
        'date': argsdict['date']
    }

    # Pass method, format, and parameters to build request url
    url = build_event_url(host, sport, method, id, format, parameters)

    req = urllib2.Request(url)
    # Set Authorization header
    req.add_header("Authorization", "Bearer " + access_token)
    # Set user agent
    req.add_header("User-agent", user_agent)
    # Tell server we can handle gzipped content
    req.add_header("Accept-encoding", "gzip")

    try:
        response = urllib2.urlopen(req)
    except urllib2.HTTPError, err:
        print "Error retrieving file: {}".format(err.code)
        sys.exit(1)
    except urllib2.URLError, err:
        print "Error retrieving file: {}".format(err.reason)
        sys.exit(1)
    data = None
    if "gzip" == response.info().get("Content-encoding"):
        buf = StringIO(response.read())
        f = gzip.GzipFile(fileobj=buf)
        data = f.read()
    else:
        data = response.read()
    if data:
        event_id = get_event_id(data)
        if event_id == None:
            print "Drats. Either this game has no box score or you mistyped your team name."
        else:
            return event_id


def get_event_id(data):
    # Parses the JSON content and returns a reference
    # to Events (https://erikberg.com/api/methods/events)
    events = json.loads(data)

    # Loop through each Event (https://erikberg.com/api/objects/event)
    for evt in events['event']:
        # Filter by team name
        if re.search(argsdict['team'], str(evt['home_team'])) or re.search(argsdict['team'], str(evt['away_team'])):
            if evt['event_status'] == 'completed':
                event_id = evt['event_id']
                return event_id
            else:
                return


# See https://erikberg.com/api/methods Request URL Convention for
# an explanation
def build_event_url(host, sport, method, id, format, parameters):
    path = "/".join(filter(None, (sport, method, id)));
    url = "https://" + host + "/" + path + "." + format
    if parameters:
        paramstring = urllib.urlencode(parameters)
        url = url + "?" + paramstring
    return url


def get_box_score():
    event_id = setup_event_id();
    # set the API method, format
    host = "erikberg.com"
    sport = 'mlb'
    method = "boxscore"
    game = event_id;
    format = "json"

    # Pass method, format, and parameters to build request url
    url = build_box_score_url(host, sport, method, game, format)

    req = urllib2.Request(url)
    # Set Authorization header
    req.add_header("Authorization", "Bearer " + access_token)
    # Set user agent
    req.add_header("User-agent", user_agent)
    # Tell server we can handle gzipped content
    req.add_header("Accept-encoding", "gzip")

    try:
        response = urllib2.urlopen(req)
    except urllib2.HTTPError, err:
        print "Error retrieving file: {}".format(err.code)
        sys.exit(1)
    except urllib2.URLError, err:
        print "Error retrieving file: {}".format(err.reason)
        sys.exit(1)
    data = None
    if "gzip" == response.info().get("Content-encoding"):
        buf = StringIO(response.read())
        f = gzip.GzipFile(fileobj=buf)
        data = f.read()
    else:
        data = response.read()
    if data:
        print_result(data)
    else:
        print "Something has gone wrong. No data returned"
    return


def print_result(data):
    # Parses the JSON content and returns a reference
    # to Events (https://erikberg.com/api/methods/events)
    box_score = json.loads(data)
    
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

    if home_team_runs > away_team_runs:
        home_team_win = "[x]"
        away_team_win = "[ ]"
    else:
        home_team_win = "[ ]"
        away_team_win = "[x]"

    print "\n" + stadium + ' ' + format(date.strftime("%A, %B %e, %Y")) + "\n"

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

    return


def build_box_score_url(host, sport, method, game, format):
    path = "/".join(filter(None, (sport, method, game)));
    url = "https://" + host + "/" + path + "." + format
    return url


get_box_score()

