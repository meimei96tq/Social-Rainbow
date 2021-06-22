#!/usr/bin/env python
# coding: utf-8

# In[1]:


from tweepy import OAuthHandler
from tweepy import API
from tweepy import Cursor
from datetime import datetime, date, time, timedelta
 
import pandas as pd
import csv
import re 
import preprocessor as p
import emoji

consumer_key = '9TvVKS8HRroMN4wQtBdzNA'
consumer_secret = 'BrmSzXi4sGzDiRdj7kbPHMRLQNMkbpHeDqtLhWPhU'
access_key= '1287392767-m7gcpy3wkpNpvMpywC9wwBTzIivWVXvLabhZMlA'
access_secret = 'RHNCzFoLOpUHZhLQu7mDkJGsgtA3xtpKm35596ZfuRY'
 
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
 
auth_api = API(auth, wait_on_rate_limit=True)


# In[2]:


try:
    uchr = unichr  # Python 2
    import sys
    if sys.maxunicode == 0xffff:
        # narrow build, define alternative unichr encoding to surrogate pairs
        # as unichr(sys.maxunicode + 1) fails.
        def uchr(codepoint):
            return (
                unichr(codepoint) if codepoint <= sys.maxunicode else
                unichr(codepoint - 0x010000 >> 10 | 0xD800) +
                unichr(codepoint & 0x3FF | 0xDC00)
            )
except NameError:
    uchr = chr  # Python 3

# Unicode 11.0 Emoji Component map (deemed safe to remove)
_removable_emoji_components = (
    (0x20E3, 0xFE0F),             # combining enclosing keycap, VARIATION SELECTOR-16
    range(0x1F1E6, 0x1F1FF + 1),  # regional indicator symbol letter a..regional indicator symbol letter z
    range(0x1F3FB, 0x1F3FF + 1),  # light skin tone..dark skin tone
    range(0x1F9B0, 0x1F9B3 + 1),  # red-haired..white-haired
    range(0xE0020, 0xE007F + 1),  # tag space..cancel tag
)
emoji_components = re.compile(u'({})'.format(u'|'.join([
    re.escape(uchr(c)) for r in _removable_emoji_components for c in r])),
    flags=re.UNICODE)
def remove_emoji(text, remove_components=False):
    cleaned = emoji.get_emoji_regexp().sub(u'', text)
    if remove_components:
        cleaned = emoji_components.sub(u'', cleaned)
    return cleaned


# In[3]:


def get_tweet(tweet):
    p.set_options(p.OPT.URL,p.OPT.MENTION,p.OPT.RESERVED,p.OPT.SMILEY)
    clean_tweet = p.clean(tweet).replace('\n','.')
    clean_tweet = remove_emoji(clean_tweet)
    return(clean_tweet)


# In[4]:


csvFile = open('transgender.csv', "w", encoding="utf-8", newline='')
csvWriter = csv.writer(csvFile)
 
search_words = 'transgender'      # enter your words
new_search = search_words + " -filter:retweets"
tweet = ''
end_date = datetime.utcnow() - timedelta(days=365)
count = 0
for tweet in Cursor(auth_api.search,q=new_search,tweet_mode='extended').items():
    count +=1
    if 'retweeted_status' in dir(tweet):
#         print(count,tweet.created_at,tweet.retweeted_status.full_text, tweet.lang,tweet.user.screen_name)
        clean_tweet = get_tweet(tweet.retweeted_status.full_text)
        if clean_tweet != '':
            csvWriter.writerow([tweet.created_at, clean_tweet,tweet.user.screen_name, tweet.lang])
    else:
#         print(count,tweet.created_at,tweet.full_text, tweet.lang,tweet.user.screen_name)
        clean_tweet = get_tweet(tweet.full_text)
        if clean_tweet != '':
            csvWriter.writerow([tweet.created_at, clean_tweet,tweet.user.screen_name, tweet.lang])
    if tweet.created_at < end_date:
        break
    if count%1000 == 0:
        print(count,tweet.created_at,tweet.full_text, tweet.lang,tweet.user.screen_name)
csvFile.close()


# In[ ]:




