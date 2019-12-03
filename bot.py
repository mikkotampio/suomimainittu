#!/usr/bin/python3

import tweepy
import json, urllib.request
import xml.etree.ElementTree as ET
from time import sleep

with open('config.json') as f:
    config = json.load(f)
    KEYWORDS = config['keywords']
    SOURCES = config['sources']
    consumer_key = config['consumer_key']
    consumer_secret = config['consumer_secret']
    access_token = config['access_token']
    access_secret = config['access_secret']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret);
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)

def read_headlines(source):
    try:
        req = urllib.request.Request(source, headers={'User-agent' : 'suomi_mainittu_bot' })
        xml = urllib.request.urlopen(req).read().decode("utf-8")
        tree = tree = ET.fromstring(xml)
        headlines = []
        
        for child in tree.find('channel'):
            if child.tag == 'item':
                headlines.append({
                    'title' : child.find('title').text,
                    'link' : child.find('link').text,
                    'description' : child.find('description').text
                })
        return headlines
    except Exception as e:
        print(str(e) + " while reading " + source)
        return []

def find_relevant_headlines():
    headlines = []
    
    for source in SOURCES:
        for headline in read_headlines(source):
            if is_relevant(headline):
                headlines.append(headline)
    
    return headlines

def is_relevant(headline):
    for keyword in KEYWORDS:
        if keyword in headline['title'].lower() or keyword in headline['description'].lower():
            return True
    return False

def in_cache(headline, cache):
    link = headline['link']
    for cached in cache:
        if cached['link'] == link:
            return True
    return False

def handle_headlines(headlines):
    try:
        with open('cache.json') as f:
            cache = json.load(f)
    except Exception:
        cache = []
    
    for headline in headlines:
        if not in_cache(headline, cache):
            post(headline)
    
    with open('cache.json', 'w') as f:
        f.write(json.dumps(headlines, indent=2))

def post(headline):
    api.update_status('torille ' + headline['link'])

while True:
    handle_headlines(find_relevant_headlines())
    sleep(60*15)
