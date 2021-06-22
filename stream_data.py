import os
import sys
import tweepy
import argparse
import json
import time
from queue import Queue
from threading import Thread
from tweepy.models import Status
import get_clean_tweet
import nltk
import string
from pymongo import MongoClient

nltk.download('punkt')

MONGO_HOST = "mongodb://localhost:27017/socialrainbow"
myclient = MongoClient("mongodb://localhost:27017/")

mydb = myclient["socialrainbow"]
tweet_col = mydb["data_tweets"]
# Enter Twitter API Keys
consumer_key = 'UrjKcF93o1K8nPpRTVaR46M3b'
consumer_secret = 'zqXwrHxzcQj219W477abf2kTsNXNupZRbg9ZyJvKxZiPzaT90H'
access_token= '1374321478179581954-vwXT8LXDY4RU29lPNRVY56bTZVss5u'
access_token_secret = 'XHRd23nKpI0XUXu1Ki0V9XYS4yObMfMUAG2W8OswIyiqo'

keyword = ['lesbian', 'gay', 'bisexual', 'transgender', 'transsexual', 'queer', 'intersex', 'asexual', 'pansexual',
              'homosexual', 'heterosexual', 'omnisexual', 'genderless', 'sex joke', 'sexually objectify', 'genderqueer',
              'genderless','non-gendered', 'trans youth','lgbt','lgbtq','lgbtq+', 'pride month']


class StreamListener(tweepy.StreamListener):
    def __init__(self, keyword, q=Queue()):
        super(StreamListener, self).__init__()
        num_worker_threads = 8
        self.q = q

        for i in range(num_worker_threads):
            t = Thread(target=self.save_tweets)
            t.daemon = True
            t.start()

        self.keyword = keyword

    def on_data(self, raw_data):
        print("on stream")
        self.q.put(raw_data)

    def save_tweets(self):
        while True:
            raw_data = self.q.get()
            client = MongoClient(MONGO_HOST)
            db = client.socialrainbow
            data = json.loads(raw_data)
            if 'in_reply_to_status_id' in data:
                status = Status.parse(self.api, data)

                is_retweet = False
                retweeted_id = 0
                if hasattr(status, 'retweeted_status'):
                    is_retweet = True
                    retweeted_id = status.retweeted_status.id

                    if hasattr(status.retweeted_status, 'extended_tweet'):
                        text = status.retweeted_status.extended_tweet['full_text']
                    else:
                        text = status.retweeted_status.text

                else:
                    if hasattr(status, 'extended_tweet'):
                        text = status.extended_tweet['full_text']
                    else:
                        text = status.text
                is_quote = hasattr(status, "quoted_status")
                quoted_text = ""
                quoted_id = 0
                if is_quote:
                    quoted_id = status.quoted_status.id

                    if hasattr(status.quoted_status, "extended_tweet"):
                        quoted_text = status.quoted_status.extended_tweet["full_text"]
                    else:
                        quoted_text = status.quoted_status.text
            if status.lang == 'vi' or status.lang == 'en':
                clean_tweet = get_clean_tweet.get_clean_tweet(text).translate(
                    str.maketrans('', '', string.punctuation + "”’?!&...;:“…|"))
                clean_tweet = clean_tweet.lower()
                # tokens = nltk.word_tokenize(clean_tweet)
                tweet = {
                    "tweet id": status.id_str,
                    "create_time": status.created_at,
                    "user_id": status.user.id_str,
                    "user_name": status.user.screen_name,
                    "tweet": text,
                    "clean_tweet": clean_tweet.strip(),
                    "lang": status.lang}

                tweet_col.insert(tweet)

            self.q.task_done()

    def on_limit(self, track):
        print("Rate Limit Exceeded, Sleep for 5 Mins")
        time.sleep(5 * 60)
        return True

    def on_error(self, status_code):
        print('Encountered streaming error (', status_code, ')')
        sys.exit()



auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

if __name__ == "__main__":
    isexcept = True
    while isexcept:
        try:
            streamListener = StreamListener(keyword)
            stream = tweepy.Stream(
                auth=api.auth, listener=streamListener, tweet_mode='extended', language=['en','vi'])
            isexcept = False
        except Exception as e:
            print('First exception:', e)
            isexcept = True

    while True:
        try:
            stream.filter(track=keyword, stall_warnings=True)
        except Exception as e:
            print('Second exception:', e)

    print('Crawling done!!!')
