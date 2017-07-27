# The purpose of this script is to scrape all images from @chrisalbon tweets referencing #machinelearningflashcards.
# __author__: Brandon Fetters
    
from collections import defaultdict
import os

import twitter
import urllib

from config import CONSUMER_KEY,CONSUMER_SECRET,OAUTH_TOKEN,OAUTH_TOKEN_SECRET

# ----------------------------------------------------------------------------------------------------------------------
def authorize():
    """
    Authorizes and creates connection with Twitter API.
    :return: twitter.api.Twitter, twitter api connection object
    """
    api = twitter.Twitter(auth=twitter.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET))
    return api

# ----------------------------------------------------------------------------------------------------------------------
def get_user_timeline(user, api, count=200, iterations=100, max_id=None):
    """
    Get all tweets for the user provided.
    :param user: str, screen_name of user (without '@')
    :param api: tweepy.API object, used for connecting to Twitter API
    :param count: int, max number of tweets to retrieve this call
    :param max_id: int, 
    :return: collection of twitter.api.TwitterListResponses (tweets)
    """
    tweets = api.statuses.user_timeline(screen_name=user,
                                        count=count,
                                        exclude_replies=True,
                                        include_rts=False)

    for x in xrange(iterations):
        max_id = tweets[-1]['id']
        tweets.extend(api.statuses.user_timeline(screen_name=user, 
                                                   count=count,
                                                   exclude_replies=True,
                                                   include_rts=False, 
                                                   max_id=max_id))

    return tweets

# ----------------------------------------------------------------------------------------------------------------------
def generate_flashcards(tweets,hashtag):
    """
    Loop through tweets, filter out any non-flashcard related, and store in dictionary.
    :param tweets: twitter.api.TwitterListResponse, collection of Twitter API reponses
    :param hashtag: str, used to filter out non-relevant tweets
    :return: dictionary with flashcards stored as topic,image_url
    """
    flashcards = defaultdict()
    for i,tweet in enumerate(tweets):
        if hashtag in tweet['text']:
            try:
                image_url = tweet['entities']['media'][0]['media_url_https']
                label = tweet['text'].split(hashtag)[0].strip().lower().replace(' ','_')
            except:
                pass  # If there isn't any media associated with the tweet we can just skip it

            if label > '':
                flashcards[label] = image_url
    return flashcards

# ----------------------------------------------------------------------------------------------------------------------
def download_images(flashcards,destination='./images/'):
    """
    Loops through all flashcards, downloads, and saves to file.
    :param flashcards: dict, dictionary with flashcards stored as topic,image_url
    :param output_path: str, directory path to save images 
    """

    if not os.path.isdir(destination):
        os.mkdir(destination)

    for topic,url in flashcards.iteritems():
        # print(topic,url)
        fname = topic + '.' + url.split('.')[-1]
        urllib.urlretrieve(url,destination + fname)

# ======================================================================================================================
if __name__ == '__main__':
    
    # Define user and hashtag variables for search
    user = 'chrisalbon'
    hashtag = '#machinelearningflashcards'

    print('Connecting to API...')
    api = authorize()

    print('Retrieving tweets...')
    tweets = get_user_timeline(user,api)

    print('Generating flashcards...')
    flashcards = generate_flashcards(tweets,hashtag)

    print('Downloading flashcards...')
    download_images(flashcards)

    print('DONE!')