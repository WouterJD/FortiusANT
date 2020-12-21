import requests
from stravalib.client import Client
import urllib3
import time

urllib3.disable_warnings()

class Strava(object):
  def __init__(self, client_id, client_secret, refresh_token, club_id):
    self.client_id = client_id
    self.client_secret = client_secret
    self.refresh_token = refresh_token

    self.token = self.get_access_token()
    self.client = Client(access_token=self.token['access_token'])

    self.club_id = club_id
    self.club = None
    self.club_expires_at = 0

  def get_access_token(self):
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
    refresh_response = self.client.refresh_access_token(client_id=self.client_id,
      client_secret=self.client_secret,
      refresh_token=self.refresh_token)
    self.token = refresh_response
    self.refresh_token = refresh_response['refresh_token']

  def update_club(self):
    if self.token_expired:
      print('access_token has expired, updating access_token')
      self.update_access_token()

    self.club = self.client.get_club(self.club_id)
    self.club_expires_at = time.time() + 300  # expires in 5 minutes

  def get_member_count(self):
    if self.club_expired:
      print('club has expired, updating club')
      self.update_club()

    return self.club.member_count

  @property
  def token_expired(self):
    return time.time() > self.token['expires_at']

  @property
  def club_expired(self):
    return time.time() > self.club_expires_at
