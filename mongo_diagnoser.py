import gc
from pymongo import MongoClient
import copy
import pickle
from scraper import get_short_story

TRUE_K = 6

def main(gen_vector, new_model):
	db, collection = connect_to_mongo()
	# docs = collection.find({ "refreshed" : 1 }).limit(500)
	docs = collection.find()
	# docs = collection.find({ "title" : "youth"})
	story_list = []
	titles = []
	incorrect, incorrect_docs = find_incorrect_stories(docs)
	pickle.dump(incorrect, open("incorrect_stories.pickle", "wb"))
	with open("incorrect_stories.txt", 'w', encoding="utf-8") as f:
		f.writelines("\n".join(incorrect))
	print(len(incorrect_docs))
	# for doc in incorrect_docs:
	# 	collection.update_one(
	# 		{
	# 			"_id": doc["_id"]
	# 		}, 
	# 		{ 
	# 			"$set": { 
	# 				"complete" : False
	# 			}
	# 		}
	# 	)
	# filter_duplicated_stories(incorrect_docs, collection)

def find_incorrect_stories(docs):
	incorrect = []
	incorrect_docs = []
	for doc in docs:
		l = doc["story"].split("\n")
		# print(l[len(l)-2].startswith(" Add"))
		if not check_correct(l[len(l)-2]):
			incorrect.append(str((doc["title"], len(l), l[len(l)-2])))
			incorrect_docs.append(doc)
	return incorrect, incorrect_docs

def check_correct(s):
	return s == ", or . . . Read the next short story; " or s.startswith(" Add")

def filter_duplicated_stories(docs, collection):
	for doc in docs:
		print(doc["title"])
		try:
			title = doc["title"]
			author = doc["author"]
			url = "/author/" + author + "/short-story/" + title
			print(url)
			gotten = get_short_story(url, title, author)
			print("Refreshed:", gotten["refreshed"])
			print("Modified Count:",collection.update_one(
				{
					"_id": doc["_id"]
				}, 
				{ 
					"$set": { 
						"story" : gotten["story"],
						"refreshed" : gotten["refreshed"]
					}
				}
			).modified_count)
		except Exception as e:
			with open("failed_to_remove_duplicates.txt", "a") as f:
				f.write(e)
				f.write("\n")
				f.write(doc["title"])
				


def anydup(thelist):
	seen = set()
	for x in thelist:
		if x in seen:
			return True
		seen.add(x)
	return False

def connect_to_mongo():
	client = MongoClient()
	db = client.get_database("reddit_archive")
	collection = db.get_collection("short_stories")
	return db, collection

if __name__ == "__main__":
	main(True, True)
