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

def find_relevant_headline_urls():
    headlines = []
    
    for source in SOURCES:
        for headline in read_headlines(source):
            if is_relevant(headline):
                headlines.append(headline['link'])
    
    return set(headlines)

def is_relevant(headline):
    for keyword in KEYWORDS:
        if keyword in headline['title'].lower() or keyword in headline['description'].lower():
            return True
    return False

def handle_urls(urls):
    try:
        with open('cache.json') as f:
            cache = json.load(f)
    except Exception:
        cache = []
    
    for url in urls:
        if not url in cache:
            post(url)
    
    with open('cache.json', 'w') as f:
        f.write(json.dumps(list(urls), indent=2))

def post(url):
    #api.update_status('torille ' + url)
    print(url)

while True:
    try:
        handle_urls(find_relevant_headline_urls())
    except Exception as e:
        print(e)
    sleep(60*15)
