from pymongo import MongoClient
from get_clean_tweet import get_clean_tweet
import datetime
import matplotlib.pyplot as plt
import pandas as pd
import string
# from topic_detection import extract_ngrams
# from burst_detection import burst_detection, enumerate_bursts, burst_weights
from topic_detection import classify_topics
import burst_detection as bd
import seaborn as sns
from matplotlib import rcParams
from sklearn.feature_extraction.text import CountVectorizer

myclient = MongoClient("mongodb://localhost:27017/")
mydb = myclient["socialrainbow"]
tweets_col = mydb["new_tweets"]
year = 2021
month = 6
day = 14
start = datetime.datetime(year, month, day, 0, 0, 0, 0)
end = datetime.datetime(year, month, day, 23, 59, 59, 59)
# ngram = extract_ngrams(tweets_col.find())


# Tweets distritution
def get_no_tweets(col, year, month, day):
    number_tweet = [0 for t in range(24)]
    for row in col:
        if row["_id"]["year"] == year and row["_id"]["month"] == month and row["_id"]["day"] == day:
            tmp = row["_id"]['hour']
            # tmp = row["_id"]['hour'] * 60 + row["_id"]['minute']
            number_tweet[tmp] = row['count']
    return number_tweet


def tweets_distribute(col):
    count = col.aggregate([
        {"$group": {
            "_id": {
                "year": {"$year": "$create_time"},
                "month": {"$month": "$create_time"},
                "day": {"$dayOfMonth": "$create_time"},
                # "hour": {"$hour": "$create_time"},
                # "minute": {"$minute": "$create_time"},

            },
            "count": {"$sum": 1}
        }
        },
        {"$sort": {"_id": 1}}
    ]);
    return count


def topic_tweets_distribute(col, topic, ngram):
    onegram_tweets = ngram[0]
    twogram_tweets = ngram[1]
    thrgram_tweets = ngram[2]
    # print(onegram_tweets)
    # print(twogram_tweets)
    # print(thrgram_tweets)
    text_topic = ''
    if topic <= 5:
        text_topic = onegram_tweets[topic - 1][0][0]
        count = col.aggregate([
            # {"$sort": {"create_time": 1}},
            {"$group": {
                "_id": {
                    "year": {"$year": "$create_time"},
                    "month": {"$month": "$create_time"},
                    "day": {"$dayOfMonth": "$create_time"},
                    # "hour": {"$hour": "$create_time"},
                    # "minute": {"$minute": "$create_time"},

                },
                "count": {
                    "$sum": {
                        "$cond": {
                            "if": {
                                "$regexMatch": {
                                    "input": "$clean_tweet",
                                    "regex": onegram_tweets[topic - 1][0][0],
                                }
                            },
                            "then": 1,
                            "else": 0
                        }
                    }
                }
            }
            },
            {"$sort": {"_id": 1}}
        ]);
    elif topic <= 10:
        text_topic = ' '.join(twogram_tweets[topic - 6][0])
        count = col.aggregate([
            # {"$sort": {"create_time": 1}},
            {"$group": {
                "_id": {
                    "year": {"$year": "$create_time"},
                    "month": {"$month": "$create_time"},
                    "day": {"$dayOfMonth": "$create_time"},
                    # "hour": {"$hour": "$create_time"},
                    # "minute": {"$minute": "$create_time"},

                },
                "count": {
                    "$sum": {
                        "$cond": {
                            "if": {
                                "$regexMatch": {
                                    "input": "$clean_tweet",
                                    "regex": ' '.join(twogram_tweets[topic - 6][0]),
                                }
                            },
                            "then": 1,
                            "else": 0
                        }
                    }
                }
            }
            },
            {"$sort": {"_id": 1}}
        ]);
    else:
        text_topic = ' '.join(thrgram_tweets[topic - 11][0])
        count = col.aggregate([
            # {"$sort": {"create_time": 1}},
            {"$group": {
                "_id": {
                    "year": {"$year": "$create_time"},
                    "month": {"$month": "$create_time"},
                    "day": {"$dayOfMonth": "$create_time"},
                    # "hour": {"$hour": "$create_time"},
                    # "minute": {"$minute": "$create_time"},

                },
                "count": {
                    "$sum": {
                        "$cond": {
                            "if": {
                                "$regexMatch": {
                                    "input": "$clean_tweet",
                                    "regex": ' '.join(thrgram_tweets[topic - 11][0]),
                                }
                            },
                            "then": 1,
                            "else": 0
                        }
                    }
                }
            }
            },
            {"$sort": {"_id": 1}}
        ]);
    return count, text_topic


def detect_event(r, d):
    n = len(r)
    variables = [[0.5, 0.5],
                 [1.5, 0.5],
                 [2.0, 0.5],
                 [3.0, 0.5],
                 [4.0, 0.5],
                 [1.5, 1.0],
                 [1.5, 1.5],
                 [1.5, 2.0],
                 [1.5, 3.0]]
    burst_list = []
    for v in variables:
        label = 's=' + str(v[0]) + ', g=' + str(v[1])
        print(label)
        [q, _, _, p] = bd.burst_detection(r, d, n, v[0], v[1],smooth_win=2)
        # enumerate the bursts
        bursts = bd.enumerate_bursts(q, label)
        # find weight of each burst
        bursts = bd.burst_weights(bursts, r, d, p)

        burst_list.append(bursts)
    return burst_list, variables

# def classify_topics(col):
#     for row in col:
#
#     return True

# Detect event
col_total = tweets_distribute(tweets_col)
# number_tweets_total = get_no_tweets(col_total, year, month, day)
number_tweets_by_day = []
for row in col_total:
    print(row)
    number_tweets_by_day.append(row['count'])
print(number_tweets_by_day)

#topic classify
#
lda_model = classify_topics(tweets_col,15)
print(lda_model.show_topics())


# d = pd.DataFrame(number_tweets_total)
# for i in range(1, 16):
#     topic_distribute = topic_tweets_distribute(tweets_col, 9, ngram)
#     col = topic_distribute[0]
#     topic = topic_distribute[1]
#     print(topic)
#     number_tweets = get_no_tweets(col, year, month, day)
#     # print(number_tweets)
#
#     r = pd.DataFrame(number_tweets).astype(float)
#     r = r.mask(r == 0).fillna(1)
#     d = d.mask(d == 0).fillna(1)
#     events = detect_event(r, d)
#     print(events)
#     # print("List burst: ", events[0])
#     # print(detect_event_isolationForest(r))
#     break
# Tweets distribution by topic (15 topics)
# for i in range(1,16):
#     print(i)
#     topic_distribute = topic_tweets_distribute(tweets_col, 9, ngram)
#     col = topic_distribute[0]
#     topic = topic_distribute[1]
#
#     number_tweets = get_no_tweets(col, year, month, day)
#     # print(number_tweets)
#
#     r = pd.DataFrame(number_tweets)
#     plt.subplots(figsize=(10, 7))
#     plt.plot(r / d, color='#00bbcc', linewidth=1)
#     plt.yticks(size=14)
#     time = list(range(0, 24))
#     lable = ["0:00","1:00","2:00","3:00","4:00","5:00","6:00","7:00","8:00","9:00"
#              ,"10:00","11:00","12:00","13:00","14:00","15:00","16:00","17:00","18:00","19:00"
#              ,"20:00","21:00","22:00","23:00"]
#     plt.xticks(time,lable,rotation = 80,size=14)
#     plt.title('Proportion Tweets Distribution by topic "'+topic+'"'+ " on "+ str(year) + "/" + str(month) + "/" + str(day), fontsize=14)
#     plt.ylabel('Proportion of tweets', size=14)
#     plt.grid(True)
#     plt.show()
#     break


# #update data
# from tqdm import tqdm
# for row in tqdm(tweets_col.find()):
#     # print(row['_id'])
#     tmp = row['clean_tweet'].translate(
#                     str.maketrans('', '', string.punctuation + "”’?!&...;:“…|"))
#     tweets_col.update({"_id": row['_id']},{"$set": {"clean_tweet": tmp}})
