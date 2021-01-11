import requests
from stravalib.client import Client
import urllib3
import time

urllib3.disable_warnings()

class Strava(object):
  def __init__(self, client_id, client_secret, refresh_token, club_id):
    # First store the client id, secret and refresh token
    self.client_id = client_id
    self.client_secret = client_secret
    self.refresh_token = refresh_token
    
    # And store some other fields
    self.club_id = club_id
    self.club = None
    self.club_expires_at = 0

    # Then we get a new access token using the client id, secret and refresh token
    self.token = self.get_access_token()

    # Now we have the access token we can create an instance of the stravalib Client
    self.client = Client(access_token=self.token['access_token'])

  def get_access_token(self):
    # Get a new access token to fetch data from the Strava API
    auth_url ="https://www.strava.com/oauth/token"
    payload = {
      'client_id' : self.client_id,
      'client_secret' : self.client_secret,
      'refresh_token' : self.refresh_token,
      'grant_type' : "refresh_token",
      'f':'json'
    }
    res = requests.post(auth_url, data=payload, verify=False)
    return res.json()

  def update_access_token(self):
    # Update the existing access token

    refresh_response = self.client.refresh_access_token(client_id=self.client_id,
      client_secret=self.client_secret,
      refresh_token=self.refresh_token)

    # refresh_response contains the following fields:
    # - refresh_token
    # - expires_at

    # We save the new token
    self.token = refresh_response
    # And save the new refresh token which should be used next time
    self.refresh_token = refresh_response['refresh_token']

  def update_club(self):
    # Get new data of the strava club

    if self.token_expired:
      # If the access token has been expired, we need to update it beofre we can fetch data from strava
      print('access_token has expired, updating access_token')
      self.update_access_token()

    # Get the strava club data
    self.club = self.client.get_club(self.club_id)
    # And set the data to expire in 5 minutes
    self.club_expires_at = time.time() + 300

  def get_member_count(self):
    # Get the member count of the strava club

    if self.club_expired:
      # Only fetch data from strava if the club data has been expired
      print('club has expired, updating club')
      self.update_club()

    return self.club.member_count

  @property
  def token_expired(self):
    # Check if the straca access token has been expired
    return time.time() > self.token['expires_at']

  @property
  def club_expired(self):
    # Check if the cached club data has been expired
    return time.time() > self.club_expires_at
