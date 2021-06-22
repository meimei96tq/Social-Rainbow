import pymongo
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
from bson.json_util import dumps

mydb = myclient["socialrainbow"]

keywords_col = mydb["keywords"]

keywords_list = [
  {"keyword": "lesbian","status": 0,"flag": 0},
  {"keyword": "gay","status": 0,"flag": 0},
  {"keyword": "bisexual","status": 0,"flag": 0},
  {"keyword": "transgender","status": 0,"flag": 0},
  {"keyword": "transsexual","status": 0,"flag": 0},
  {"keyword": "queer","status": 0,"flag": 0},
  {"keyword": "intersex","status": 0,"flag": 0},
  {"keyword": "asexual","status": 0,"flag": 0},
  {"keyword": "genderless","status": 0,"flag": 0},
  {"keyword": "pansexual","status": 0,"flag": 0},
  {"keyword": "homosexual","status": 0,"flag": 0},
  {"keyword": "heterosexual","status": 0,"flag": 0},
  {"keyword": "omnisexual","status": 0,"flag": 0},
  {"keyword": "sex joke","status": 0,"flag": 0}
]

#keywords_col.insert_many(keywords_list)
# #
# # print(x.inserted_ids)
# keywords = []
# # keywords_col = mydb["keywords"]
# for row in keywords_col.find():
#   keywords.append(row['keyword'])
# print((keywords))
# keyword = "queer"
# i = keywords_col.count_documents({"keyword": keyword, "flag": 1})
# print(i)
# les_col = mydb['lesbian']
# curson = les_col.find({})
# with open('data.json','w') as file:
#   file.write('[')
#   for doc in curson:
#     file.write(dumps(doc))
#     file.write(',')
#   file.write(']')