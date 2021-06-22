import collections
import string
import re
import nltk
from nltk.util import ngrams
# nltk.download('punkt')
from nltk.corpus import stopwords
import pymongo
myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["socialrainbow"]
import get_clean_tweet

def extract_ngrams(tweets):
    sw = stopwords.words('english')
    tokens = []
    for row in tweets:
        text = row['clean_tweet']
        text = " ".join([word for word in text.split() if not word.lower() in sw])
        tokens.extend(nltk.word_tokenize(text))
    one_gram_counter = collections.Counter(ngrams(tokens,1))
    one_gram_counter = one_gram_counter.most_common(5)

    two_gram_counter = collections.Counter(ngrams(tokens,2))
    two_gram_counter = two_gram_counter.most_common(5)

    thr_gram_counter = collections.Counter(ngrams(tokens,3))
    thr_gram_counter = thr_gram_counter.most_common(5)

    return one_gram_counter, two_gram_counter, thr_gram_counter

# print(extract_ngrams(mydb["lesbian"].find()))
