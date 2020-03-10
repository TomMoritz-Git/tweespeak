import config
import tweepy
from tweepy import Stream, OAuthHandler
from Tweet import Tweet
import json



class Matcher:
    """
    This class is usefull to match tweets with their retweets.
    """

    # Load config
    cfg = config.conf
    user = 'TM'

    # Get tweeter API credidentials
    consumer_key = cfg[user]['API-KEY']
    consumer_secret = cfg[user]['API-KEY-SECRET']
    access_token = cfg[user]['ACCESS-TOKEN']
    access_token_secret = cfg[user]['ACCESS-TOKEN-SECRET']

    # Setup tweeter API auth
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)


    def __init__(self, inflect_nb_to_words=False, rm_stop_words=False, \
        tweet_min_len=10):
        self.inflect_nb_to_words = inflect_nb_to_words
        self.rm_stop_words = rm_stop_words
        self.tweet_min_len = tweet_min_len


    def match_all(self, from_path, to_path):
        """
        Match each tweet with one retweet.
        """
        with open(from_path, 'r', encoding='utf-8') as read_f:
            with open(to_path, 'w', encoding='utf-8') as write_f:
                for line in read_f:
                    tweet = Tweet(
                        data=line,
                        rm_stop_words=self.rm_stop_words,
                        inflect_nb_to_words=self.inflect_nb_to_words,
                        tracked_patterns=[],
                        tweet_min_len=self.tweet_min_len,
                        tweet_format='clean_txt')
                    tweet_id = tweet.JSON['in_reply_to_status_id_str']
                    if tweet_id:
                        try:
                            data = json.dumps(
                                self.api.get_status(tweet_id)._json)
                            origin_tweet = Tweet(
                                data=data,
                                rm_stop_words=self.rm_stop_words,
                                inflect_nb_to_words=self.inflect_nb_to_words,
                                tracked_patterns=[],
                                tweet_min_len=self.tweet_min_len,
                                tweet_format='clean_txt')
                            if origin_tweet.clean_txt.strip():
                                write_f.write(origin_tweet.clean_txt + '\n')
                                write_f.write(tweet.clean_txt + '\n')
                                write_f.write('\n')
                        except:
                            pass


matcher = Matcher()
matcher.match_all('template_data.txt', 'matched_data.txt')
