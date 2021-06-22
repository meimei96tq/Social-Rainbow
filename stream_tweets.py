import tweepy
import json
from pymongo import MongoClient
from queue import Queue
from threading import Thread
from tweepy.models import Status
import time
import get_clean_tweet
import nltk
import string


nltk.download('punkt')

MONGO_HOST = "mongodb://localhost:27017/socialrainbow"
myclient = MongoClient("mongodb://localhost:27017/")
mydb = myclient["socialrainbow"]
keywords_col = mydb["keywords"]

class StreamListener(tweepy.StreamListener):
    # This is a class provided by tweepy to access the Twitter Streaming API.
    def __init__(self, keyword, q=Queue()):
        super(StreamListener, self).__init__()
        self.keyword = keyword
        num_worker_threads = 8
        self.q = q

        for i in range(num_worker_threads):
            t = Thread(target=self.save_tweets)
            t.daemon = True
            t.start()
        self.is_continue = True
    def on_data(self, raw_data):
        self.q.put(raw_data)
        print('on data',self.keyword)
        if int(time.time()) % 15 == 0:
            self.is_continue = self.stop_streaming()
        return self.is_continue

    def on_error(self, status_code):
        # On error - if an error occurs, display the error / status code
        print('An Error has occured: ' + repr(status_code))
        return False

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
            clean_tweet = get_clean_tweet.get_clean_tweet(text).translate(str.maketrans('', '', string.punctuation + "”’?!&...,;:“…|"))
            clean_tweet = clean_tweet.lower()
            # tokens = nltk.word_tokenize(clean_tweet)
            tweets = db[self.keyword]
            tweet = {
                "tweet id": status.id_str,
                "create_time": status.created_at,
                "user_id": status.user.id_str,
                "user_name": status.user.screen_name,
                "tweet": text,
                "clean_tweet": clean_tweet,
                "lang": status.lang}

            tweets.insert(tweet)

            self.q.task_done()
    def on_error(self, status_code):
        print('Encountered streaming error (', status_code, ')')

    def stop_streaming(self):
        flag = keywords_col.count_documents({"keyword": self.keyword, "flag": 1})
        if flag != 0:
            print("stop", self.keyword)
            return False
        else:
            print("not stop", self.keyword)
            return True