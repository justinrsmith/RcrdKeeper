#!/usr/bin/env python
import oauth2 as oauth
import urllib
consumer = oauth.Consumer('zq33ap8e526smhskzx7xkghf', 'rudg3ASW2T')
client = oauth.Client(consumer)
response = client.request('http://api.rdio.com/1/', 'POST', urllib.urlencode({'method': 'get', 'artist': 'arcade fire'}))
print response[1]