import pandas as pd
from pymongo import MongoClient
from get_clean_tweet import get_clean_tweet


def read_mongo(collection, query={}, host='localhost', port=27017, username=None, password=None, no_id=True):
    """ Read from Mongo and Store into DataFrame """

    # Connect to MongoDB
    myclient = MongoClient("mongodb://localhost:27017/")
    db = myclient["socialrainbow"]

    # Make a query to the specific DB and Collection
    cursor = db[collection].find(query)

    # Expand the cursor an construct the DataFrame
    df = pd.DataFrame(list(cursor))

    # Delete the _id
    if no_id and '_id' in df:
        del df['_id']

    return df
def get_clean_df(data):
    df = read_mongo(data, {'lang': 'en'})
    df.to_csv(data+'.csv', index=False)
    df = pd.read_csv(data+'.csv', index_col=[0])
    df.drop_duplicates(subset=['tweet'], keep='first',inplace=True)
    return(df)
