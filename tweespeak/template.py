from Listener import Listener

listener = Listener(
	tracked_keywords=['coronavirus', 'covid-19', 'COVID-19'],
	tracked_patterns=['coronavirus'],
	languages=['en'],
	locations=[-124.86, 24.65, -74.95, 49.01],
	follow=False,
	file_path='./template_data.txt',
	inflect_nb_to_words=False,
	tweet_limit=10,
	tweet_min_len=10,
	tweet_format='clean_txt',
	from_scratch=True,
    rm_stop_words=False,
    checkpoint_rate=0.2,
    only_retweeted=False,
    match_reply=True)

listener.start_listening()

from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

target = "for the trumpworld coronavirus is fake news just another democratic lie"
corpus = [line for idx, line in enumerate(open('template_data.txt', 'r', encoding='utf-8')) if idx % 2 == 0]
corpus += [target]

vect = TfidfVectorizer(min_df=1, stop_words="english")                                                                                                                                                                                                   
tfidf = vect.fit_transform(corpus)                                                                                                                                                                                                                       
pairwise_similarity = tfidf * tfidf.T

arr = pairwise_similarity.A 
np.fill_diagonal(arr, np.nan)
argmax = np.nanargmax(arr[corpus.index(target)])
corpus = [line for idx, line in enumerate(open('template_data.txt', 'r', encoding='utf-8')) if idx % 2 != 0]
match = corpus[argmax]
print(match)
