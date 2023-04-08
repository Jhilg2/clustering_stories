import gc
from pymongo import MongoClient
import copy

from scraper import get_short_story

TRUE_K = 6

def main(gen_vector, new_model):
	db, collection = connect_to_mongo()
	docs = collection.find({ "refreshed" : { "$exists" : False}}).limit(500)
	# docs = collection.find({ "title" : "a-bad-business"}).limit(1)
	# docs = collection.find({ "has_dup" : { "$exists" : False}}).limit(1500)
	story_list = []
	titles = []
	filter_duplicated_stories(docs, collection)

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
