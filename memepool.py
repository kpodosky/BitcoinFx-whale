# -*- coding: utf-8 -*-
import requests
import json
import tweepy
import time
import datetime
from time import sleep
from keys import *

from tweepy import auth

# Make a GET request to the mempool.space API
url = "https://mempool.space/api/block/000000000000000015dc777b3ff2611091336355d3f0ee9766a2cf3be8e4b1ce"
response = requests.get(url)
data = response.text
print(data)
