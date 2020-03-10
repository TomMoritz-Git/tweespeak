import config
import tweepy
from tweepy import Stream, OAuthHandler, Cursor
from tweepy.streaming import StreamListener
from DB_Manager import DB_Manager
from Tweet import Tweet
import re
import time
import os
import json



class Listener(StreamListener):
    """
    The Listener class gets data from
    Tweeter's API in real time based on given
    search parameters such as keywords and regex.
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


    def __init__(self, tracked_keywords, tracked_patterns, languages, \
        locations, file_path, inflect_nb_to_words=False, tweet_limit=10, \
        tweet_min_len=10, tweet_format='clean_txt', from_scratch=True, \
        rm_stop_words=False, checkpoint_rate=0.25, follow=False,\
        only_retweeted=False, match_reply=False):
        self.tracked_keywords = tracked_keywords
        self.tracked_patterns = tracked_patterns
        self.languages = languages
        self.locations = locations
        self.file_path = file_path
        self.inflect_nb_to_words = inflect_nb_to_words
        self.tweet_limit = tweet_limit
        self.tweet_min_len = tweet_min_len
        self.tweet_format = tweet_format
        self.from_scratch = from_scratch
        self.rm_stop_words = rm_stop_words
        self.only_retweeted = only_retweeted
        self.match_reply = match_reply
        self.follow = follow if follow else []
        self.__get_follow_id()
        self.checkpoint_rate = 1.0 if checkpoint_rate is False \
                                 else checkpoint_rate
        self.checkpoint = int(round(self.checkpoint_rate * tweet_limit))
        self.tweet_count = 0
        self.start_time = time.time()
        self.tweetDB = DB_Manager(
            file_path=file_path,
            tweet_format=tweet_format,
            from_scratch=from_scratch)


    def __get_follow_id(self):
        if self.follow:
            user_objects = self.api.lookup_users(
                screen_names=self.follow)
            self.follow_ids = [user.id_str for user in user_objects]
        else:
            self.follow_ids = []


    def __tweet_listened(self):
        """
        Show listener progression based on the tweet limit
        and takes care of checkpoints.
        """
        self.tweet_count += 1
        percent = self.tweet_count / self.tweet_limit * 100
        tpt = (time.time() - self.start_time) / self.tweet_count
        print('Progression: {:.2f}% - {} tweets | {:.2f}s per tweet ' \
            .format(percent, self.tweet_count, tpt), end='\r')
        
        if self.tweet_count % self.checkpoint == 0:
            self.tweetDB.save()


    def __end_stream(self):
        """
        End the tweepy stream, closing files.
        """
        print('\nEnd of listening.')
        print(f'File(s) saved at: {os.path.abspath(self.file_path)}')
        self.tweetDB.close_DB()
        return False


    def start_listening(self):
        """
        Initiate the stream with the tweepy API.
        """
        # Start listening
        print('Listening...')
        self.twitterStream = Stream(
            self.auth,
            self,
            tweet_mode="extended",
            wait_on_rate_limit=True)

        # Filter tweets based on keywords, languages and locations
        self.twitterStream.filter(
            track=self.tracked_keywords,
            languages=self.languages,
            locations=self.locations,
            follow=self.follow_ids)


    def on_data(self, data):
        """
        Append tweets as json into the "tweets.json" file.
        """
        # Check tweet limit
        enough_tweet = self.tweet_limit <= self.tweet_count
        if not enough_tweet:
            tweet = Tweet(
                data=data,
                rm_stop_words=self.rm_stop_words,
                inflect_nb_to_words=self.inflect_nb_to_words,
                tracked_patterns=self.tracked_patterns,
                tweet_min_len=self.tweet_min_len,
                tweet_format=self.tweet_format,
                only_retweeted=self.only_retweeted,
                match_reply=self.match_reply)

            # Filter tweet the right format based on:
            # tracked patterns and min length
            if tweet.complies:
                if self.match_reply:
                    origin_tweet = self.find_origin_tweet(tweet)
                    if origin_tweet:
                        self.tweetDB.add_tweet(tweet)
                        self.tweetDB.add_tweet(origin_tweet)
                        self.__tweet_listened()
                else:
                    self.tweetDB.add_tweet(tweet)
                    self.__tweet_listened()

        # Quit app when the tweet count is reached
        else:
            self.__end_stream()
            return False


    def on_error(self, status):
        """
        Print error on tweepy error.
        """
        print('Tweepy Error:')
        print(status)


    def on_status(self, status):
        """
        Help to close the stream quicker
        when the tweet limit is reached.
        """
        enough_tweet = self.tweet_limit <= self.tweet_count
        if enough_tweet:
            self.__end_stream()
            return False


    def find_origin_tweet(self, tweet):
        """
        Find the first tweet is the current instance
        is a reply tweet.
        """
        if tweet.is_reply:
            try:
                data = json.dumps(
                    self.api.get_status(
                        id=tweet.is_reply,
                        tweet_mode="extended",
                        wait_on_rate_limit=True)._json)
                return Tweet(
                    data=data,
                    tracked_patterns=[],
                    rm_stop_words=self.rm_stop_words,
                    inflect_nb_to_words=self.inflect_nb_to_words,
                    tweet_min_len=1,
                    match_reply=False,
                    tweet_format=self.tweet_format,
                    only_retweeted=False)
            except Exception as e:
                pass
