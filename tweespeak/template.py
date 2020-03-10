from Listener import Listener
from Matcher import Matcher

listener = Listener(
	tracked_keywords=['politic', 'politics', 'election', 'president'],
	tracked_patterns=['politic'],
	languages=['en'],
	locations=[-124.86, 24.65, -74.95, 49.01],
	file_path='./template_data.txt',
	inflect_nb_to_words=False,
	tweet_limit=10,
	tweet_min_len=3,
	tweet_format='JSON',
	from_scratch=True,
    rm_stop_words=False,
    checkpoint_rate=False,
    only_retweeted=True)

listener.start_listening()

matcher = Matcher()
matcher.match_all('template_data.txt', 'matched_data.txt')
