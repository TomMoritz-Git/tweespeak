from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np



class Tweet2vec:
	"""
	This class is used to vectorize tweets
	or couple of tweeted, already preprocessed.
	It can allow to identify similar tweets.
	"""

	def __init__(self, from_path, pairwise=False, min_df=1):
		self.from_path = from_path
		self.pairwise = pairwise
		self.corpus = []
		self.min_df = min_df


	def load_corpus(self):
		"""
		Load corpus of texts in from_path.
		"""
		if self.pairwise:
			with open(self.from_path, 'r', encoding='utf-8') as f:
				self.corpus = [line for idx, line in enumerate(f) if idx % 2 == 0]
		else:
			with open(self.from_path, 'r', encoding='utf-8') as f:
				self.corpus = [line for line in f]


	def vectorize_tweets(self):
		"""
		Vectorize tweets, where each line
		of the from_path file is a text.
		"""
		self.vect = TfidfVectorizer(
			min_df=self.min_df,
			stop_words="english")                                                                                                                                                                                                   
		self.tfidf = self.vect.fit_transform(self.corpus)
		self.pairwise_similarity = self.tfidf * self.tfidf.T
		self.arr = self.pairwise_similarity.A 
		np.fill_diagonal(self.arr, np.nan)


	def find_most_similar(self, tweet):
		"""
		Find most similar tweet in the corpus.
		"""
		self.load_corpus()
		self.corpus += [tweet]
		self.vectorize_tweets()
		argmax = np.nanargmax(self.arr[self.corpus.index(tweet)])
		if self.pairwise:
			with open(self.from_path, 'r', encoding='utf-8') as f:
				self.paired_corpus = [line for idx, line in enumerate(f) if idx % 2 != 0]
				return self.paired_corpus[argmax]
		else:
			return self.corpus[argmax]
