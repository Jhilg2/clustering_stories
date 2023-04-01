import requests
from pymongo import MongoClient
from bs4 import BeautifulSoup
import time

def main():
	urls = []
	for i in range(1):
		print(19)
		url = "https://americanliterature.com/short-story-library/?page=" + str(19)
		page = requests.get(url)
		soup = BeautifulSoup(page.content, "html.parser")
		link_list = soup.find("div", class_="row")
		for link in link_list.findAll('a'):
			urls.append(link.get('href'))
		time.sleep(2)
	failed = []
	db, collection = connect_to_mongo()
	for url in urls:
		try:
			s = url.split("/")
			print(s)
			title = s[4]
			author = s[2]
			x = collection.count_documents({"title": title})
			if x == 0:
				collection.insert_one(get_short_story(url, title, author))
			else:
				print("skipped:", title)
		except Exception as e:
			print(e)
			print(url)
			failed.append(url)
	print(failed)


def get_short_story(url, title, author):
	full_url = "https://americanliterature.com" + url
	page = requests.get(full_url)
	soup = BeautifulSoup(page.content, "html.parser")
	unparsed_story = soup.findAll('p')
	parsed = []
	for line in unparsed_story:
		parsed.append(str(line.text))
	return {
		"title": title,
		"author": author,
		"story": parsed
	}

def connect_to_mongo():
	client = MongoClient()
	db = client.get_database("reddit_archive")
	collection = db.get_collection("short_stories")
	return db, collection

if __name__ == "__main__":
	main()
