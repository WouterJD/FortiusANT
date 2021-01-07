from flask import Flask
from flask_restful import Api
from shields import StravaShield
from strava import Strava
import os

env = os.environ

# The Strava API secrets must be provided by setting the following envorinment
# variables:
# - CLIENT_ID
# - CLIENT_SECRET
# - REFRESH_TOKEN
CLIENT_ID = env['CLIENT_ID']
CLIENT_SECRET = env['CLIENT_SECRET']
REFRESH_TOKEN = env['REFRESH_TOKEN']

# The ID of the Strava Club we want to provide the badge for is provided by
# setting the following environment variable:
# - STRAVA_CLUB_ID
STRAVA_CLUB_ID = env['STRAVA_CLUB_ID']

app = Flask(__name__)
api = Api(app)

# Create the Strava instance which will handle fetching the club data from Strava
strava = Strava(CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, STRAVA_CLUB_ID)

# Connect the /strava REST endpoint to the Strava instance
api.add_resource(StravaShield, "/strava", resource_class_kwargs={'strava': strava})

if __name__ == "__main__":
  app.run()
