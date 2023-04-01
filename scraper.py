import requests
from pymongo import MongoClient
from bs4 import BeautifulSoup
import time

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
	full_url = "https://americanliterature.com" + url
	page = requests.get(full_url)
	soup = BeautifulSoup(page.content, "html.parser")
	with open("text.html", "w") as f:
		f.write(str(page.content))
	unparsed_story = soup.find('div', {"itemtype":"https://schema.org/ShortStory"}).findAll('p')
	parsed = []
	# print(unparsed_story)
	for line in unparsed_story:
		parsed.append(str(line.text))
	# print("LENGTH:", len(parsed))
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
