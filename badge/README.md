# FortiusANT Strava Badge

[![Custom badge](https://img.shields.io/endpoint?logo=Strava&logoColor=orange&style=flat-square&url=https%3A%2F%2Fmarcoveeneman-badges.herokuapp.com%2Fstrava)](https://www.strava.com/clubs/804672)

This folder contains all the necessary files to get a working Strava badge showing the number of members of the FortiusANT Strava Club.

## Background

FortiusANT has it's own Strava Club where users of the FortiusANT software can join and share their rides. To promote this Strava Club (and as a nice gadget) the Strava Club badge has been created which shows the number of members of the FortiusANT club.

## Details

The Strava badge is created using the [Shields.io](https://shields.io) service. Using this service one can create a badge for virtually anything using the custom [JSON endpoint](https://shields.io/endpoint).

Strava provides an [API](https://developers.strava.com) with which data can be collected from the platform, including the member count of a Strava Club. However, this API requires authentication in order to be used.

To connect the dots a third service is needed which will fetch data from the Strava API and provide a JSON endpoint which can be fetched by the Shields service. This is implemented as a Flask REST application running on a Heroku server.

## Technical
```
                     Heroku
 --------         ------------         ------------         --------------
| Strava | ----> | Flask REST | ----> | Shields.io | ----> | Strava Badge |
 --------         ------------         ------------         --------------
                       /\
                        \__  This is what we implement here
```

Shields.io requires the endpoint to provide at least the following JSON data on an endpoint:
```json
{
  "schemaVersion": 1,
  "label": "<label>",
  "message": "<value>",
  "color": "<color>"
}
```

The Flask REST application running on [Heroku](https://devcenter.heroku.com) provides this data on the `/strava` endpoint. When a request is made on this endpoint, the application will first query the Strava API to collect the number of members of the Strava Club. Once the Strava API has returned the data it can be used to respond to the request on the `/strava` endpoint. The response from the Strava API will be cached for 5 minutes to prevent hitting the rate limit of the Strava API. All requests to this endpoint within 5 minutes will use the cached data instead of making a new request.

The Strava API requires a token to be used in order to authenticate. This token needs to be renewed every 6 hours. This is taken care of in the application automatically.

To collect data from Strava the [stravalib](https://pypi.org/project/stravalib/) library is used.

The Flask REST application is running on a Heroku server. Heroku is a cloud platform as a service supporting various programming languages, which can run applications for you. Since the application is running on a free instance, it requires to be polled every 30 minutes to prevent the server from going to sleep. This is solved by registering to [Kaffeine](https://kaffeine.herokuapp.com).
