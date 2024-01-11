import tweepy
import requests
import json
from requests.auth import AuthBase
import time
import base64
import hashlib
import hmac
from datetime import datetime

# Twitter API Credentials
consumer_key = 'YOUR_CONSUMER_KEY'
consumer_secret = 'YOUR_CONSUMER_SECRET'
access_token = 'YOUR_ACCESS_TOKEN'
access_token_secret = 'YOUR_ACCESS_TOKEN_SECRET'

# Coinbase Pro API Credentials
coinbase_api_key = 'YOUR_COINBASE_PRO_API_KEY'
coinbase_secret_key = 'YOUR_COINBASE_PRO_SECRET_KEY'
coinbase_passphrase = 'YOUR_COINBASE_PRO_PASSPHRASE'

# Coinbase Pro API URLs
coinbase_api_url = 'https://api.pro.coinbase.com/'

# Twitter Authentication
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# Coinbase Pro Authentication Class
class CoinbaseAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        message = timestamp + request.method + request.path_url + (request.body or '')
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message.encode(), hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest())

        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        })
        return request

# Instantiate CoinbaseAuth
coinbase_auth = CoinbaseAuth(coinbase_api_key, coinbase_secret_key, coinbase_passphrase)

# Monitor Tweets from Elon Musk
class ElonMuskStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        if status.user.screen_name.lower() == 'elonmusk':
            if '#doge' in status.text.lower() or '#dogecoin' in status.text.lower():
                self.prepare_dogecoin_buy_order()

    def on_error(self, status_code):
        if status_code == 420:
            # Disconnect the stream
            return False

    def prepare_dogecoin_buy_order(self):
        # Implement the logic to prepare a Dogecoin buy order
        order_data = {
            'type': 'market',
            'side': 'buy',
            'product_id': 'DOGE-USD',
            'funds': '100.00'  # Amount in USD to buy Dogecoin with
        }
        response = requests.post(coinbase_api_url + 'orders', auth=coinbase_auth, json=order_data)
        if response.status_code == 200:
            print("Buy order prepared successfully.")
        else:
            print(f"Error preparing buy order: {response.text}")

# Start the stream
myStreamListener = ElonMuskStreamListener()
myStream = tweepy.Stream(auth=api.auth, listener=myStreamListener)

# Filter the stream for tweets by @elonmusk
myStream.filter(follow=['44196397'])  # Twitter ID for @elonmusk
