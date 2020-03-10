import os



class DB_Manager():
    """
    This class is used to store tweets following specifics parameters.
    """

    def __init__(self, file_path, tweet_format='clean_txt', \
        from_scratch=True):
        self.file_path = file_path
        self.tweet_format = tweet_format
        self.from_scratch = from_scratch
        self.__open_data_files()


    def __open_data_files(self, saving=False):
        """
        Create and open the files used to store
        tweet data by the Listener class (or other).
        """
        if saving:
            mode = 'a'
        else:
            mode = 'w' if self.from_scratch else 'a'
        self.DB_file = open(self.file_path, mode, encoding='utf-8')


    def add_tweet(self, tweet):
        """
        Add tweet to the DB file following the wanted format.
        """
        if self.tweet_format == 'clean_txt':
            self.DB_file.write(tweet.clean_txt.strip() + '\n')
        
        elif self.tweet_format == 'raw_txt':
            self.DB_file.write(tweet.raw_txt.strip() + '\n')

        elif self.tweet_format == 'JSON':
            self.DB_file.write(tweet.data.strip() + '\n')


    def save(self):
        """
        Save the DB, usually on checkpoints.
        """
        self.DB_file.close()
        self.__open_data_files(saving=True)


    def close_DB(self):
        """
        Close DB files.
        """
        self.DB_file.close()

