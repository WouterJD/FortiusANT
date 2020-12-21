from flask_restful import Resource

endpoint = {
  "schemaVersion": 1,
  "label": "Strava",
  "message": "1234",
  "color": "orange"
}
class StravaShield(Resource):
  def __init__(self, **kwargs):
    self.strava = kwargs['strava']

  def get(self):
    members = self.strava.get_member_count()
    endpoint['message'] = f"{members}"
    return endpoint, 200
