import re
import json
import html
import inflect
from nltk.corpus import stopwords


# Build english stopwords
stopwords = list(stopwords.words('english'))


class Tweet():
    """
    The Tweet class is used to process and parse a tweets
    returned by the Tweeter API (through the tweepy library).
    """

    def __init__(self, data, tracked_patterns, rm_stop_words=False, \
        inflect_nb_to_words=True, tweet_min_len=10, \
        tweet_format='clean_txt', only_retweeted=False):
        self.data = data
        self.tracked_patterns = tracked_patterns
        self.rm_stop_words = rm_stop_words
        self.inflect_nb_to_words = inflect_nb_to_words
        self.tweet_min_len = tweet_min_len
        self.tweet_format = tweet_format
        self.only_retweeted = only_retweeted
        self.inflect_nb = inflect.engine()
        self.JSON = self.get_JSON()
        self.raw_txt = self.get_raw_txt()
        self.clean_txt = self.get_clean_txt()
        self.check_compliance()


    def get_JSON(self):
        """
        Return tweet as a JSON object (dict in Python).
        """
        return json.loads(self.data)


    def get_raw_txt(self):
        """
        Return tweet as raw text.
        """
        raw_txt = self.JSON.get('retweeted_status', {}) \
                           .get('extended_tweet', {}) \
                           .get('full_text', False)
        raw_txt = raw_txt if raw_txt else self.JSON.get('text', '')
        raw_txt = re.sub('\n|\t|\r', ' ', raw_txt) # Extra stip
        raw_txt = ' '.join(raw_txt.split()) # Remove extra spaces
        return raw_txt.strip()


    def get_clean_txt(self):
        """
        Return tweet as clean text.
        """
        clean_txt = self.raw_txt.split(' ')
        clean_txt = [word.lower() for word in clean_txt]

        if self.inflect_nb_to_words:
            clean_txt = [
                    self.inflect_nb.number_to_words(word)
                    if re.search('\d+', word)
                    else word
                    for word in clean_txt]

        if self.rm_stop_words:
            clean_txt = [word \
                        for word in clean_txt \
                        if word not in stopwords]

        clean_txt = ' '.join(clean_txt)

        # remove URLs
        clean_txt = re.sub('http[^\s]+|www[^\s]+', '', clean_txt)
        clean_txt = re.sub('http\S+', '', clean_txt)
        # remove usernames
        clean_txt = re.sub('@[^\s]+', '', clean_txt)
        # remove the #hashtag
        clean_txt = re.sub('#([^\s]+)', '', clean_txt)
        # remove RT markers
        clean_txt = re.sub('^rt\s', '', clean_txt)
        # keep alpha only
        clean_txt = re.sub('[^a-zA-Z ]', '', clean_txt)
        # remove solo char
        clean_txt = ' '.join([word for word in clean_txt.split() \
                     if len(word) > 1 or word in ['i', 'a']])
        # remove extra spaces
        clean_txt = re.sub('\s{2,}', ' ', clean_txt)

        return clean_txt.strip()


    def check_compliance(self):
        """
        Check the tweet compliance regarding
        tracked patterns and min length.
        """
        # Check the right tweet format
        if self.tweet_format == 'clean_txt':
            tweet = self.clean_txt
        elif self.tweet_format in ['raw_txt', 'JSON']:
            tweet = self.raw_txt
        # Check all regex match
        matches = 0
        for regex in self.tracked_patterns:
            if re.search(regex, tweet):
                matches += 1
        self.complies = len(self.tracked_patterns) == matches
        # Check min length
        if self.complies:
            self.complies = len(tweet) >= self.tweet_min_len
        # Check retweet status
        if self.complies and self.only_retweeted:
            # if self.JSON['retweeted'] or 'RT @' in self.raw_txt:
            if self.JSON['in_reply_to_status_id_str'] is not None:
                self.complies = True
            else:
                self.complies = False
