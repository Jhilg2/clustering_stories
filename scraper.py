import requests
from pymongo import MongoClient
from bs4 import BeautifulSoup
import time
import pickle
import re

def main():
	urls = ["/author/ambrose-bierce/short-story/a-baby-tramp"]
	# for i in range(1):
	# 	print(19)
	# 	url = "https://americanliterature.com/short-story-library/?page=" + str(19)
	# 	page = requests.get(url)
	# 	soup = BeautifulSoup(page.content, "html.parser")
	# 	link_list = soup.find("div", class_="row")
	# 	for link in link_list.findAll('a'):
	# 		urls.append(link.get('href'))
	# 	time.sleep(2)
	failed = []
	# db, collection = connect_to_mongo()
	for url in urls:
		try:
			s = url.split("/")
			print(s)
			title = s[4]
			author = s[2]
			with open("text.txt", "w") as f:
				f.writelines(get_short_story(url, title, author)["story"])
			# x = collection.count_documents({"title": title})
			# if x == 0:
			# 	collection.insert_one(get_short_story(url, title, author))
			# else:
			# 	print("skipped:", title)
		except Exception as e:
			print(e)
			print(url)
			failed.append(url)
	print(failed)


def get_short_story(url, title, author):
	headers = {'User-Agent': 'test_user'}
	full_url = "https://americanliterature.com" + url
	page = requests.get(full_url, headers=headers)
	# pickle.dump(page, open("second.html.pickle", "wb"))
	# page = pickle.load(open("test.html.pickle", "rb"))
	# with open("second_time.html", "w") as f:
	# 	f.write(str(page.content))
	soup = BeautifulSoup(page.content, "html.parser")
	x = soup.find('div', {"itemtype":"https://schema.org/ShortStory"})
	unparsed_story = x.findAll('p')
	parsed = []
	# print(unparsed_story)
	count = 0
	# print(unparsed_story)
	for line in unparsed_story:
		if count < 1:
			s = cleanhtml(str(line))
			s = list(filter(None, s.split("\n")))
			parsed = s
			print(parsed)
		count +=1
	# print(parsed)
	# print("LENGTH:", len(parsed))
	return {
		"title": title,
		"author": author,
		"story": parsed
	}


CLEANR = re.compile('<.*?>') 
def cleanhtml(raw_html):
	cleantext = re.sub(CLEANR, '', raw_html)
	return cleantext

def connect_to_mongo():
	client = MongoClient()
	db = client.get_database("reddit_archive")
	collection = db.get_collection("short_stories")
	return db, collection

if __name__ == "__main__":
	main()
