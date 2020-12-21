from flask import Flask
from flask_restful import Api
from shields import StravaShield

app = Flask(__name__)
api = Api(app)
api.add_resource(StravaShield, "/strava")

if __name__ == "__main__":
  app.run()
