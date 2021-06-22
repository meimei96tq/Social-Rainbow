from topic_detection import extract_ngrams
import datetime
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt
def tweets_distribute(col,topic,year,month,day,ngram):
    onegram_tweets = ngram[0]
    twogram_tweets = ngram[1]
    thrgram_tweets = ngram[2]
    if topic <= 5:
        # print(onegram_tweets[topic -1][0][0])
        tweets_distribute = []
        for i in range(24):
            start = datetime.datetime(year, month, day, i, 0, 0, 0)
            end = datetime.datetime(year, month, day, i, 59, 59, 0)
            # print(start, end)
            number_tweets = col.find({
                "$and": [
                    {"create_time": {"$gte": start}},
                    {"create_time": {"$lt": end}},
                    {"clean_tweet": {
                            "$regex": onegram_tweets[topic - 1][0][0],
                            "$options": 'i'}
                    }
                ]
            }).count()
            tweets_distribute.append({
                "number_tweets": number_tweets,
                "start": i})
        return tweets_distribute, onegram_tweets[topic - 1][0][0]
    elif topic <= 10:
        # print(' '.join(twogram_tweets[topic - 6][0]))
        tweets_distribute = []
        for i in range(24):
            start = datetime.datetime(year, month, day, i, 0, 0)
            end = datetime.datetime(year, month, day, i, 59, 59)
            # print(start, end)
            number_tweets = col.find({
                "$and": [
                    {"create_time": {"$gte": start}},
                    {"create_time": {"$lt": end}},
                    {"clean_tweet": {
                            "$regex": ' '.join(twogram_tweets[topic - 6][0]),
                            "$options": 'i'}
                    }
                ]
            }).count()
            tweets_distribute.append({
                "number_tweets": number_tweets,
                "start": i})
        return tweets_distribute, ' '.join(twogram_tweets[topic - 6][0])
    else:
        tweets_distribute = []
        # print(' '.join(thrgram_tweets[topic - 11][0]))
        for i in range(24):
            start = datetime.datetime(year, month, day, i, 0, 0)
            end = datetime.datetime(year, month, day, i, 59, 59)
            number_tweets = col.find({
                "$and": [
                    {"create_time": {"$gte": start}},
                    {"create_time": {"$lt": end}},
                    {"clean_tweet": {
                            "$regex": ' '.join(thrgram_tweets[topic - 11][0]),
                            "$options": 'i'}
                    }
                ]
            }).count()
            tweets_distribute.append({
                "number_tweets": number_tweets,
                "start": i})
        return tweets_distribute, ' '.join(thrgram_tweets[topic - 11][0])
def detect_event(col,topic,year,month,day,ngram):
    td = tweets_distribute(col=col,topic=topic,year=year,month=month,day=day,ngram=ngram)
    distribute = td[0]
    df = pd.DataFrame(distribute)
    model = IsolationForest(n_estimators=50, max_samples='auto', contamination=float(0.1), max_features=1.0)
    model.fit(df[['number_tweets']])
    df['scores'] = model.decision_function(df[['number_tweets']])
    df['anomaly'] = model.predict(df[['number_tweets']])
    # print(df)
    anomaly = df.loc[df['anomaly'] == -1]
    anomaly_index = list(anomaly.index)
    return df, td[1]