import gensim
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import *
import numpy as np
np.random.seed(400)
import pandas as pd
stemmer = SnowballStemmer("english")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from nltk.probability import FreqDist
from gensim.corpora import Dictionary
from gensim.models.ldamodel import LdaModel
from gensim.models import CoherenceModel
import spacy
from spacy import displacy
nlp = spacy.load("en_core_web_sm") #efficiency
# nlp = spacy.load("en_core_web_trf") #accuracy
from tqdm import tqdm

import pymongo
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["socialrainbow"]

def lemmatize_stemming(text):
    return stemmer.stem(WordNetLemmatizer().lemmatize(text, pos='v'))


# Tokenize and lemmatize
def preprocess(text):
    result = []
    for token in gensim.utils.simple_preprocess(text):
        if len(token) > 3:
            result.append(lemmatize_stemming(token))

    return result

def format_topics_sentences(ldamodel, corpus, texts):
    # Init output
    sent_topics_df = pd.DataFrame()

    # Get main topic in each document
    for i, row_list in enumerate(ldamodel[corpus]):
        row = row_list[0] if ldamodel.per_word_topics else row_list
        # print(row)
        row = sorted(row, key=lambda x: (x[1]), reverse=True)
        # Get the Dominant topic, Perc Contribution and Keywords for each document
        for j, (topic_num, prop_topic) in enumerate(row):
            if j == 0:  # => dominant topic
                wp = ldamodel.show_topic(topic_num)
                topic_keywords = ", ".join([word for word, prop in wp])
                sent_topics_df = sent_topics_df.append(pd.Series([int(topic_num), round(prop_topic,4), topic_keywords]), ignore_index=True)
            else:
                break
    sent_topics_df.columns = ['Dominant_Topic', 'Perc_Contribution', 'Topic_Keywords']

    # Add original text to the end of the output
    contents = pd.Series(texts)
    sent_topics_df = pd.concat([sent_topics_df, contents], axis=1)
    return(sent_topics_df)


def classify_topics(col,num_topics):
    df = pd.DataFrame(list(col.find({'lang': 'en'})))
    print("number of tweets: ", len(df.index))
    df.drop_duplicates(subset=['tweet'], keep='first', inplace=True)
    df['clean_tweet'] = df['clean_tweet'].apply(preprocess)
    df.dropna(subset=["clean_tweet"], inplace=True)
    print("number of tweets after remove 1: ",len(df.index))
    name_entities = []
    lable = ["PERSON", "NORP", "FACILITY", "ORGANIZATION", "GPE", "LOCATION", "PRODUCT", "EVENT",
             "WORK_OF_ART", "LAW","DATE", "TIME"]
    print("check 1")
    for row in tqdm(df['tweet']):
        doc = nlp(row)
        for ent in doc.ents:
            if ent.label_ in lable:
                if ent not in name_entities:
                    name_entities.append(ent)
    index = []
    print("check 2")
    for i in tqdm(range(len(df.index))):
        #     df = df.reset_index(drop=True)
        for ent in name_entities:
            flag = 0
            if str(ent['ner']) in df['clean_tweet'][i]:
                flag = 1
                break
        if flag == 0:
            index.append(df.index[i])
    for i in index:
        df.drop(df.index[i])
    df = df.reset_index(drop=True)
    print("number of tweets after remove 2: ", len(df.index))
    text_dict = Dictionary(df.clean_tweet)
    text_dict.filter_extremes(no_below=5, no_above=.90)
    # txt_out = text_dict.token2id
    tweets_bow = [text_dict.doc2bow(tweet) for tweet in df['clean_tweet']]
    tweets_lda = LdaModel(tweets_bow,
                          num_topics=num_topics,
                          id2word=text_dict,
                          random_state=1,
                          passes=10)
    return tweets_lda



# def extract_ngrams(tweets):
#     tokens = []
#     for row in tweets:
#         text = row['clean_tweet']
#         tokens.extend(nltk.word_tokenize(text))
#     one_gram_counter = collections.Counter(ngrams(tokens, 1))
#     one_gram_counter = one_gram_counter.most_common(5)
#
#     two_gram_counter = collections.Counter(ngrams(tokens,2))
#     two_gram_counter = two_gram_counter.most_common(5)
#
#     thr_gram_counter = collections.Counter(ngrams(tokens,3))
#     thr_gram_counter = thr_gram_counter.most_common(5)
#
#     return one_gram_counter, two_gram_counter, thr_gram_counter


# def topic_detection(data):
#     df = get_clean_df(data)
#     print(df)
#     tfidf_vect = TfidfVectorizer(max_df=0.8, min_df=2, stop_words='english')
#     doc_term_matrix = tfidf_vect.fit_transform(df['clean_tweet'])
#
#     # Transform the TF-IDF: nmf_features
#     nmf = NMF(n_components=15, random_state=42)
#     nmf.fit(doc_term_matrix)
#     topic_values = nmf.transform(doc_term_matrix)
#     df['topic'] = topic_values.argmax(axis=1)
#     return(df)
