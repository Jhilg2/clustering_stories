import requests
import webbrowser
from bs4 import BeautifulSoup
from selenium import webdriver
from dateutil import parser

from pymongo import MongoClient
COMMENT_INFO = [("span", "score unvoted"),("div", "md"),("a", "author")]
POST_INFO = [("div", "md"),("a", "author"), ("a", "title")]


def main():
	# URL = "https://old.reddit.com/r/linguistics/comments/srbear/are_there_languages_with_explicit_markers_of_both/"
	#
	#
	# page = requests.get(URL, headers = {'User-agent': 'your bot 0.1'})
	# with open("failtest.html", "wb") as f:
	# 	f.write(page.content)
	with open("6-21-2022.html", "rb") as f:
		soup = BeautifulSoup(f, "html.parser")

		# results = soup.find("title").prettify()
		results = soup.find_all("div",{"class":"entry unvoted"}) #id=lambda x: x and x.startswith('thing_'))# {"class": "score unvoted"})
		# list = [str(str(tag).encode("utf-8")) for tag in soup.find_all()]
		f2 = open("test.txt", "w", encoding="utf-8")
		boo = True
		unparsed_comments = results[1:]
		unparsed_post = results[0]
		unparsed_score = soup.find("div", {"class": "midcol unvoted"})
		score = unparsed_score.find("div", {"class":"score likes"}).text
		f2.write(str(get_post_info(unparsed_post, score)))
		d = get_post_info(unparsed_post, score)
		for x in d:
			print(x + ": " + str(d[x]))
		f2.write("\n")
		for comment in unparsed_comments:
			# if boo:
			r = get_comment_info(comment)
			f2.write(str(r))
			f2.write("\n")
			# f2.write(str(result))
			# f2.write("\n")
			# boo = False
		f2.close()


def write_rows(listicle, file):
	mod_list = [item + "\n" for item in listicle]
	file.writelines(mod_list)


def get_comment_info(soup):
	ret = {}
	for c in COMMENT_INFO:
		div = soup.find(c[0], {"class": c[1]})
		ret[c[1]] = div.text if div else None
	return ret

def get_post_info(soup, score):
	ret = {"score unvoted": score}
	for c in POST_INFO:
		div = soup.find(c[0], {"class": c[1]})
		ret[c[1]] = div.text if div else None
	title = soup.find("a", {"class": "title"})
	if title and title.has_attr("href"):
		ret["href"] = title["href"]
	date = soup.find("time")
	if date and date.has_attr('datetime'):
		ret["timestamp"] = parser.parse(date["datetime"])
	return ret

def test_access_mongo(to_write):
	client = MongoClient('hostname', 27017)
	db = client.local
	collection = db.teset_collection
	print(collection.find_one())


if __name__ == "__main__":
	main()
