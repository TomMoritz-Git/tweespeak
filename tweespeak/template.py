from Listener import Listener
from Tweet2vec import Tweet2vec

# listener = Listener(
# 	tracked_keywords=['for', 'a', 'and', 'the', 'an'],
# 	tracked_patterns=['^why|^Why'],
# 	languages=['en'],
# 	locations=[-124.86, 24.65, -74.95, 49.01],
# 	follow=False,
# 	file_path='./template_data.txt',
# 	inflect_nb_to_words=False,
# 	tweet_limit=100,
# 	tweet_min_len=25,
# 	tweet_format='clean_txt',
# 	from_scratch=True,
#     rm_stop_words=False,
#     checkpoint_rate=0.2,
#     only_retweeted=False,
#     match_reply=True)

# listener.start_listening()

txt2vec = Tweet2vec(
	from_path='template_data.txt',
	pairwise=True,
	min_df=1)

input_tweet = 'why my computer is so slow'
reply = txt2vec.find_most_similar(tweet=input_tweet)

print(reply)
