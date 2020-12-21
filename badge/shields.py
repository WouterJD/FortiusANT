from flask_restful import Resource

endpoint = {
  "schemaVersion": 1,
  "label": "Strava",
  "message": "1234",
  "color": "orange"
}

class StravaShield(Resource):
  def get(self):
    return endpoint, 200
