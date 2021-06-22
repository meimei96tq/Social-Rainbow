from flask import Flask, render_template, request, json, jsonify
import tweepy
from stream_tweets import StreamListener
import pymongo
import random
import pandas as pd
from flask_socketio import SocketIO
from flask_socketio import send, emit
from flask_socketio import join_room, leave_room
import json
from event_detection import detect_event, tweets_distribute
import datetime

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["socialrainbow"]
keywords_col = mydb["keywords"]
tweets_col = mydb["tweets"]

consumer_key1 = 'nxyEVskSZSJi4jW5B8HNYxexC'
consumer_secret1 = 'aY06gJf3uDGRHt5wyRX7W4Jrson2zhxKnsJrva33Eg8b0knPFC'
access_key1 = '1293517000711368708-sKPm1JtQBqx29ZNFYYnkJK04hr91St'
access_secret1 = '9ga09pSu5JxxX8zcx88EeZSnc1dcUa6AYK2cDUB4LMaVG'

consumer_key2 = '9TvVKS8HRroMN4wQtBdzNA'
consumer_secret2 = 'BrmSzXi4sGzDiRdj7kbPHMRLQNMkbpHeDqtLhWPhU'
access_key2 = '1287392767-m7gcpy3wkpNpvMpywC9wwBTzIivWVXvLabhZMlA'
access_secret2 = 'RHNCzFoLOpUHZhLQu7mDkJGsgtA3xtpKm35596ZfuRY'

consumer_key3 = 'UrjKcF93o1K8nPpRTVaR46M3b'
consumer_secret3 = 'zqXwrHxzcQj219W477abf2kTsNXNupZRbg9ZyJvKxZiPzaT90H'
access_key3 = '1374321478179581954-vwXT8LXDY4RU29lPNRVY56bTZVss5u'
access_secret3 = 'XHRd23nKpI0XUXu1Ki0V9XYS4yObMfMUAG2W8OswIyiqo'

consumer_keys = [consumer_key1, consumer_key2, consumer_key3]
consumer_secrets = [consumer_secret1, consumer_secret2, consumer_secret3]
access_keys = [access_key1, access_key2, access_key3]
access_secrets = [access_secret1, access_secret2, access_secret3]

# def create_app(test_config=None):
app = Flask(__name__, instance_relative_config=True)

auth = tweepy.OAuthHandler(consumer_keys[0], consumer_secrets[0])
auth.set_access_token(access_keys[0], access_secrets[0])
api = tweepy.API(auth, wait_on_rate_limit=True,
                 wait_on_rate_limit_notify=True)


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/keywords', methods=['POST'])
def action():
    if request.form['flag'] == 'stop':
        keyword = request.form['kw']
        keywords_col.update_one({"keyword": keyword}, {"$set": {"status": 0}})
        keywords_col.update_one({"keyword": keyword}, {"$set": {"flag": 1}})
        return render_template("keywords.html", keywords=keywords_col.find())
    elif request.form['flag'] == 'del':
        keyword = request.form['kw']
        keywords_col.delete_one({"keyword": keyword})
        return render_template("keywords.html", keywords=keywords_col.find())
    return render_template("keywords.html", keywords=keywords_col.find())


@app.route('/stream_data', methods=['POST'])
def stream_data():
    keyword = request.form['kw']
    keywords_col.update_one({"keyword": keyword}, {"$set": {"flag": 0}})
    keywords_col.update_one({"keyword": keyword}, {"$set": {"status": 1}})
    auth = tweepy.OAuthHandler(consumer_keys[0], consumer_secrets[0])
    auth.set_access_token(access_keys[0], access_secrets[0])
    # Set up the listener. The 'wait_on_rate_limit=True' is needed to help with Twitter API rate limiting.
    listener = StreamListener(keyword)
    streamer = tweepy.Stream(auth=api.auth, listener=listener, tweet_mode='extended', )
    print("Tracking: " + str(keyword))
    streamer.filter(track=keyword, languages=['en'])
    return render_template("keywords.html", keywords=keywords_col.find())


# @app.route('/view_tweets', methods=['POST'])
# def view_tweets():
#     keyword = request.form['kw']
#     tweet_col = mydb[keyword]
#     return render_template("view_tweets.html", tweet_col=tweet_col.find(), keyword=keyword)

@app.route('/keywords', methods=['GET'])
def keywords():
    return render_template("keywords.html", keywords=keywords_col.find())


@app.route('/extract_topic', methods=['POST'])
def extract_topic():
    keyword = request.form['kw']
    topic = int(request.form['topic'])
    col = mydb[keyword]

    year = col.find()[0]['create_time'].year
    month = col.find()[0]['create_time'].month
    day = col.find()[0]['create_time'].day

    events = detect_event(col,topic,year,month,day)
    tweets_distribute = events[0]
    event_time = events[1]
    all_tweets = []
    for time in event_time:
        start = datetime.datetime(year, month, day, time, 0, 0)
        tweets = col.find({
            "create_time": {"$gte": start}
        })
        all_tweets.append(tweets)
    print(all_tweets)
    return render_template("event_detection.html", keyword=keyword, tweets=all_tweets[0], tweets_distribute=tweets_distribute,
                           flag=1, year=year, month=month, day=day)


@app.route('/event_detection', methods=['POST'])
def event_detection():
    keyword = request.form['kw']
    return render_template("event_detection.html", keyword=keyword)


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/contact')
def contact():
    return render_template("contact.html")


if __name__ == '__main__':
    app.run(debug=True)
