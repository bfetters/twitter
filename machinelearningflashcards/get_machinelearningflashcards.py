# The purpose of this script is to scrape all images from @chrisalbon tweets referencing #machinelearningflashcards.
# __author__: Brandon Fetters

import argparse
from collections import defaultdict
import os

import twitter
import urllib

from config import CONSUMER_KEY,CONSUMER_SECRET,OAUTH_TOKEN,OAUTH_TOKEN_SECRET

# ----------------------------------------------------------------------------------------------------------------------
DUPLICATE_CARDS = ["heteroscedasticity_(with_a_k,_apparently)", "leave_one_out_cross_validation_(with_thanks_to_@rasbt_and_@ramhiser)",
                   "residual_sum_of_squares_(which_should_be_called_sum_of_squared_residuals,_but_whatevs)", "since_someone_asked,_all_my",
                   "supervised_vs_unsupervised", "what_are_principal_components", "why_don't_you_write_your"]

# ----------------------------------------------------------------------------------------------------------------------
def authorize():
    """
    Authorizes and creates connection with Twitter API.
    :return: twitter.api.Twitter, twitter api connection object
    """
    api = twitter.Twitter(auth=twitter.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET))
    return api

# ----------------------------------------------------------------------------------------------------------------------
def get_user_timeline(user, api, count=200, iterations=100, max_id=None, verbose=False):
    """
    Get all tweets for the user provided.
    :param user: str, screen_name of user (without '@')
    :param api: tweepy.API object, used for connecting to Twitter API
    :param count: int, max number of tweets to retrieve this call
    :param max_id: int, only get tweets older than this id
    :param verbose: boolean, print more detailed status statements
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

    if verbose:
        print('\t=> {} tweets retrieved.'.format(len(tweets)))

    return tweets

# ----------------------------------------------------------------------------------------------------------------------
def generate_flashcards(tweets,hashtag, verbose=False):
    """
    Loop through tweets, filter out any non-flashcard related, and store in dictionary.
    :param tweets: twitter.api.TwitterListResponse, collection of Twitter API reponses
    :param hashtag: str, used to filter out non-relevant tweets
    :return: dictionary with flashcards stored as topic,image_url
    """
    n = 0  # Number of flashcards
    flashcards = defaultdict()
    for i,tweet in enumerate(tweets):
        if hashtag in tweet['text']:
            try:
                image_url = tweet['entities']['media'][0]['media_url_https']
                label = tweet['text'].split(hashtag)[0].strip().lower().replace(' ','_')
            except:
                pass  # If there isn't any media associated with the tweet we can just skip it

            # Don't create flashcard if text is blank or it is a duplicate
            if label > '' and label not in DUPLICATE_CARDS:
                n += 1
                flashcards[label] = image_url

    if verbose:
        print('\t=> {} flashcards generated.'.format(n))

    return flashcards

# ----------------------------------------------------------------------------------------------------------------------
def download_images(flashcards,destination='./images/', verbose=False):
    """
    Loops through all flashcards, downloads, and saves to file.
    :param flashcards: dict, dictionary with flashcards stored as topic,image_url
    :param output_path: str, directory path to save images 
    """
    new_flashcards = []
    if not os.path.exists(destination):
        os.mkdir(destination)

    for topic,url in flashcards.iteritems():
        fname = destination + topic + '.' + url.split('.')[-1]

        # Only save images to file if it doesn't already exist
        if not os.path.exists(fname):
            new_flashcards.append(fname)
            urllib.urlretrieve(url,fname)

    if verbose:
        print('\t=> {} new flashcards downloaded.'.format(len(new_flashcards)))
        for flashcard in new_flashcards:
            print('\t\t + {}'.format(flashcard.split('/')[-1]))

# ======================================================================================================================
if __name__ == '__main__':

    # Process command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', default=False, action='store_true', help='print detailed output to console')
    args = parser.parse_args()

    # Define user and hashtag variables for search
    user = 'chrisalbon'
    hashtag = '#machinelearningflashcards'

    print('Connecting to API...')
    api = authorize()

    print('Retrieving tweets...')
    tweets = get_user_timeline(user, api, verbose=args.verbose)

    print('Generating flashcards...')
    flashcards = generate_flashcards(tweets, hashtag, verbose=args.verbose)

    print('Downloading flashcards...')
    download_images(flashcards, verbose=args.verbose)

    print('DONE!')