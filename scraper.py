import requests
from pymongo import MongoClient
from bs4 import BeautifulSoup
import re
from datetime import datetime
import logging
import pickle

logging.basicConfig(level=logging.INFO, filename="scraper.log")

def main():
	urls = []
	for i in range(1,20):
		url = "https://americanliterature.com/short-story-library/?page=" + str(i)
		page = requests.get(url)
		soup = BeautifulSoup(page.content, "html.parser")
		link_list = soup.find("div", class_="row")
		urls.extend([link.get('href') for link in link_list.findAll('a')])
	logging.debug(f"Urls received: [{', '.join(urls)}] ")


	db, collection = connect_to_mongo()
	for url in urls:
		try:
			s = url.split("/")
			title = s[4]
			author = s[2]
			if collection.count_documents({"title": title}) == 0:
				short_story = get_short_story(url, title, author)
				logging.debug(f"story object: {short_story}")
				collection.insert_one(short_story)
			else:
				print("skipped:", title)
		except Exception as e:
			logging.error(f"Error: {e} for URL {url}")


def get_short_story(url, title, author):
	full_url = "https://americanliterature.com" + url
	page = requests.get(full_url)
	soup = BeautifulSoup(page.content, "html.parser")
	story_html = soup.find('div', {"itemtype":"https://schema.org/ShortStory"})
	unparsed_story = story_html.findAll('p')
	line = unparsed_story[0]
	html_cleaned_story = cleanhtml(str(line))
	parsed = list(filter(None, html_cleaned_story.split("\n")))
	return {
		"title": title,
		"author": author,
		"refreshed": datetime.now(),
		"story": '\n'.join(parsed)
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
