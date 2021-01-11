from flask_restful import Resource

# Data fields required by the Shields.io service
endpoint = {
  "schemaVersion": 1,
  "label": "Strava",
  "message": "1234",
  "color": "orange"
}

class StravaShield(Resource):
  def __init__(self, **kwargs):
    # Store a reference to the strava instance here so it can be used to fetch data
    self.strava = kwargs['strava']

  def get(self):
    # This function is called when a GET request is made on the /strava endpoint. Once
    # the request is made the member count of the strava club will be fetched. This
    # value is then filled in in the endpoint data and returned together with a success
    # status code (200).

    members = self.strava.get_member_count()
    endpoint['message'] = f"{members}"
    return endpoint, 200
