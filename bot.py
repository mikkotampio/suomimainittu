#!/usr/bin/python3

import tweepy
import json, urllib.request, sys
import xml.etree.ElementTree as ET
from time import sleep

if len(sys.argv) != 2:
    print("Run with 'debug' or 'run'")
    sys.exit()

DEBUG = sys.argv[1].lower() == 'debug'

if DEBUG:
    print('Debug mode enabled')
elif sys.argv[1].lower() != 'run':
    print("Run with 'debug' or 'run'")
    sys.exit()

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

def or_empty(string):
    if string == None:
        return ''
    return string

def read_headlines(source):
    try:
        if DEBUG:
            print('Reading ' + source)
        
        req = urllib.request.Request(source, headers={'User-agent' : 'suomi_mainittu_bot' })
        xml = urllib.request.urlopen(req).read().decode("utf-8")
        tree = tree = ET.fromstring(xml)
        headlines = []
        
        for child in tree.find('channel'):
            if child.tag == 'item':
                headlines.append({
                    'title' : or_empty(child.find('title').text),
                    'link' : or_empty(child.find('link').text),
                    'description' : or_empty(child.find('description').text)
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

def handle_headlines(headlines):
    try:
        with open('cache.json') as f:
            cache = json.load(f)
    except Exception:
        cache = []
    
    for headline in headlines:
        url = headline['link']
        title = headline['title']
        if (not url in cache) and (not title in cache):
            post(url)
    
    with open('cache.json', 'w') as f:
        new_cache = []
        new_cache.extend([hl['link'] for hl in headlines])
        new_cache.extend([hl['title'] for hl in headlines])
        f.write(json.dumps(new_cache, indent=2))

def post(url):
    if not DEBUG:
        api.update_status('torille ' + url)
    print(url)

while True:
    try:
        handle_headlines(find_relevant_headlines())
    except Exception as e:
        print(e)
    sleep(60*15)
