import gc
from pymongo import MongoClient
import copy

from scraper import get_short_story

TRUE_K = 6

def main(gen_vector, new_model):
	db, collection = connect_to_mongo()
	docs = collection.find({ "has_dup" : { "$exists" : False}}).limit(100)
	story_list = []
	titles = []
	filter_duplicated_stories(docs, collection)

def filter_duplicated_stories(docs, collection):
	print("here")
	for doc in docs:
		print("here too?")
		story = filter(None,doc["story"].split("\n"))
		count = 0
		print(doc["title"])
		try:
			if not anydup(copy.deepcopy(story)):
				print(collection.update_one(
						{
							"_id": doc["_id"]
						}, 
						{ 
							"$set": { 
								"has_dup" : False
							}
						}
					).modified_count)
			else:
				while count < 3 :
					count += 1
					title = doc["title"]
					author = doc["author"]
					url = "/author/" + author + "/short-story/" + title
					print(url)
					gotten_story = get_short_story(url, title, author)["story"]
					filtered_story = filter(None, gotten_story)
					if not anydup(copy.deepcopy(filtered_story)):
						count = 5
						print(collection.update_one(
							{
								"_id": doc["_id"]
							}, 
							{ 
								"$set": { 
									"story" : "\n".join(filtered_story),
									"has_dup" : False
								}
							}
						).modified_count)
					elif count == 3:
						collection.update_one(
							{
								"_id": doc["_id"]
							}, 
							{ 
								"$set": { 
									"has_dup" : True
								}
							}
						)
		catch:
			pass
				


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
