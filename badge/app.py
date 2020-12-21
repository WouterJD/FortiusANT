from flask import Flask
from flask_restful import Api
from shields import StravaShield
from strava import Strava
import os

env = os.environ

CLIENT_ID = env['CLIENT_ID']
CLIENT_SECRET = env['CLIENT_SECRET']
REFRESH_TOKEN = env['REFRESH_TOKEN']
STRAVA_CLUB_ID = env['STRAVA_CLUB_ID']

app = Flask(__name__)
api = Api(app)
strava = Strava(CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, STRAVA_CLUB_ID)
api.add_resource(StravaShield, "/strava", resource_class_kwargs={'strava': strava})

if __name__ == "__main__":
  app.run()
