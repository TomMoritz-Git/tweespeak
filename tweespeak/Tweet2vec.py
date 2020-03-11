from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pickle
from Tweet import Tweet



class Tweet2vec:
    """
    This class is used to vectorize tweets
    or couple of tweeted, already preprocessed.
    It can allow to identify similar tweets.
    """

    def __init__(self, from_path, from_format, \
        pairwise=False, min_df=1):
        self.from_path = from_path
        self.from_format = from_format
        self.pairwise = pairwise
        self.corpus = []
        self.min_df = min_df


    def load_corpus(self):
        """
        Load corpus of texts in from_path.
        """
        if self.from_format != 'pickle':
            with open(self.from_path, 'r', encoding='utf-8') as f:
                    self.corpus = [line for line in f]
        else:
            with open(self.from_path, 'rb') as f:
                self.pickle_corpus = []
                while True:
                    try:
                        data = pickle.load(f)
                        self.pickle_corpus += [data]
                        self.corpus += [data.clean_txt]
                    except EOFError:
                        break


    def add_tweet_to_corpus(self, tweet):
        """
        Append a tweet to the corpus list.
        """
        self.corpus += [tweet]
        if self.from_format == 'pickle':
            self.pickle_corpus += [
                Tweet(
                    tweet,
                    tracked_patterns=[],
                    from_word2vec=True)]


    def vectorize_tweets(self):
        """
        Vectorize tweets, where each line
        of the from_path file is a text.
        """
        self.vect = TfidfVectorizer(
            min_df=self.min_df,
            stop_words="english")

        if self.pairwise:
            self.even_corpus = [
                txt for idx, txt in enumerate(self.corpus) \
                if idx % 2 == 0]
            self.tfidf = self.vect.fit_transform(self.even_corpus)
        else:
            self.tfidf = self.vect.fit_transform(self.corpus)

        self.pairwise_similarity = self.tfidf * self.tfidf.T
        self.arr = self.pairwise_similarity.A 
        np.fill_diagonal(self.arr, np.nan)


    def find_most_similar(self, tweet):
        """
        Find most similar tweet in the corpus.
        """
        self.load_corpus()
        self.add_tweet_to_corpus(tweet)
        self.vectorize_tweets()
        if self.pairwise:
            self.argmax = np.nanargmax(
                self.arr[self.even_corpus.index(tweet)])
            self.argmax = self.argmax * 2
        else:
            self.argmax = np.nanargmax(
                self.arr[self.corpus.index(tweet)])

        if self.from_format == 'pickle':
            if self.pairwise:
                return self.pickle_corpus[self.argmax], \
                       self.pickle_corpus[self.argmax + 1]
            else:
                return self.pickle_corpus[self.argmax]
        else:
            if self.pairwise:
                return self.corpus[self.argmax], \
                       self.corpus[self.argmax + 1]
            else:
                return self.corpus[self.argmax]
