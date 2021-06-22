from pymongo import MongoClient

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
import numpy as np

myclient = MongoClient("mongodb://localhost:27017/")
mydb = myclient["socialrainbow"]
tweets_col = mydb["new_tweets"]
documents = []
for row in tweets_col.find():
    documents.append(row['clean_tweet'])
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(documents)

true_k = 15
model = KMeans(n_clusters=true_k, init='k-means++', max_iter=100, n_init=1)
model.fit(X)
y_kmeans = model.predict(X)
def get_tweets_topic(topic,y_kmeans):
    tweets = []
    index = np.where(y_kmeans == topic)
    for i in index[0]:
        tweets.append(documents[i])
    return tweets
print(get_tweets_topic(1,y_kmeans))
