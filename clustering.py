import gc
from pymongo import MongoClient
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import pickle
from sklearn.metrics import silhouette_score
from collections import Counter

TRUE_K = 10

def main(gen_vector, new_model):
	db, collection = connect_to_mongo()
	docs = collection.find({"complete": True})
	story_list = []
	titles = []
	for doc in docs:
		story_list.append(doc["story"])
		titles.append(doc["title"])
	print(len(titles))
	x = vectorize(story_list, gen_vector)
	# select_k(x)
	labels=cluster(x, new_model)
	cluster_silhouette_score(x, labels)
	write_labels_to_document(labels, titles)
	# print("Stories in each group",Counter(labels))



def select_k(x):
	# decide on number of clusters
	sum_of_sqrd_dist = []
	clusters = range(2, 15)
	for cluster_count in clusters:
		print("Clusters:", cluster_count)
		km = KMeans(n_clusters=cluster_count, max_iter=200, n_init=10)
		km = km.fit(x)
		sum_of_sqrd_dist.append(km.inertia_)
	plt.plot(clusters, sum_of_sqrd_dist, 'bx-')
	plt.xlabel('k')
	plt.ylabel('Sum_of_squared_distances')
	plt.title('Elbow Method For Optimal k')
	plt.show()


def cluster(x, new_model):
	if new_model:
		# Clustering
		model = KMeans(n_clusters=TRUE_K, init='k-means++', max_iter=200, n_init=10)
		model.fit(x)
		pickle.dump(model, open("clustering_model.pickle", "wb"))
	else:
		model = pickle.load(open("clustering_model.pickle","rb"))
	labels=model.labels_
	print(Counter(labels))
	return labels


def cluster_silhouette_score(x,labels):
	silhouette_avg = silhouette_score(X=x, labels=labels)
	print(
        "The average silhouette_score is :",
        silhouette_avg,
    )


def vectorize(story_list, gen_vector):
	vectorizer = TfidfVectorizer(max_df=.6)
	print("Vectorizing")
	x = {}
	if gen_vector:
		x = vectorizer.fit_transform(story_list)
		print(vectorizer.stop_words_)
		pickle.dump(x, open("vectorizer.pickle", "wb"))
	else:
		x = pickle.load(open("vectorizer.pickle", "rb"))
	print("Vectorized")
	return x


def write_labels_to_document(labels, titles):
	result={'cluster':labels,'title':titles}
	# result={'cluster':labels,'story':story_list}
	result=pd.DataFrame(result)
	for k in range(0,TRUE_K):
		s=result[result.cluster==k]
		with open("labels_per_title.txt", "a") as f:
			f.write(s.to_string(header=True, index=True))
			f.write(str(k))


def connect_to_mongo():
	client = MongoClient()
	db = client.get_database("reddit_archive")
	collection = db.get_collection("short_stories")
	return db, collection

if __name__ == "__main__":
	main(False, False)
