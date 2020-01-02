import tweepy #pip install tweepy, documentation: http://docs.tweepy.org/en/latest/index.html
import requests
import json
from datetime import date

"""Leon Xu analyze tweets sentiment using Repustate Api

"""




class TwitterAPI():
    """Twitter API Class to retriving tweets data

    """
    api = None
    auth = None

    def __init__(self, consumer_key, consumer_secret, access_token, access_secret):
        """Initialize twitter API with keys
        
        Arguments:
            consumer_key {[str]} -- consumer keys for the API
            consumer_secret {[str]} -- consumer secret keys for the API
            access_token {[str]} -- access token for the API
            access_secret {[str]} -- access secret token for the API
        """
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_secret = access_secret
        self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        self.auth.set_access_token(access_token, access_secret)
        self.api = tweepy.API(self.auth)
    

    def on_status(self, status):
        """return full text of tweets
        
        Arguments:
            status {[tweetStatus]} -- [Object that contains all the information of a tweet]
        
        Returns:
            [str] -- [text decription of the tweet]
        """
        if hasattr(status, "retweeted_status"):  # Check if Retweet
            try:
                return ((status.retweeted_status.full_text).encode('utf8'))              
            except AttributeError:
                return ((status.retweeted_status.text).encode('utf8'))
        else:
            try:
                return((status.full_text).encode('utf8'))
            except AttributeError:
                return((status.text).encode('utf8'))
    
    def getTweetsText(self, q, count, until=date.today(), result_type='mixed'):
        """return tweets text from API status call
        
        Arguments:
            q {[str]} -- query string

            count {[int]} -- number of tweets search for

            until {[str]} -- the search tweets until the date provided, default is today's day

            result_type {[str]} -- the results type of search tweets, default is mixed
        
        Returns:
            [list] -- [list of tweets text]
        """
        tweets = []
        status = self.api.search(q=q, count=count, until=until, result_type=result_type, tweet_mode='extended')
        for s in status:
            tweets.append(self.on_status(s)) 
        return tweets


class RepustateAPI():
    """Use Repustate API to analyze tweets
    """
    repustateAPI = None
    entitiesAPI = None

    def __init__(self, apiKey):
        """initilize Repustate API  
        
        Arguments:
            apiKey {[str]} -- [customer API Key]
        """
        self.apiKey = apiKey
        self.repustateAPI = 'https://api.repustate.com/v4/{}/score.json'.format(apiKey)
        self.entitiesAPI = 'https://api.repustate.com/v4/{}/entities.json'.format(apiKey)

    def getSentiment(self, data):
        """get sentiment json
        
        Arguments:
            data {[str]} -- [text decription of the tweets]
        
        Returns:
            [json] -- [json format of sentiment score]
        """
        score = requests.post(self.repustateAPI, 'text='+data)
        return score.json()


    def getEntities(self, data):
        """get entities json
        
        Arguments:
            data {[str]} -- [text decription of the tweets]
        
        Returns:
            [json] -- [json format of entities data]
        """
        entities = requests.post(self.entitiesAPI, 'text='+data)
        return entities.json()


def displayTool(score, entities):
    """a display function to output necessary infomation
    
    Arguments:
        score {[type]} -- [description]
        entities {[type]} -- [description]
    """
    positive = 0
    negative = 0
    titles = {}
    

    for data in score:
        if data.get('score') > 0:
            positive+=1
        elif data.get('score') < 0:
            negative+=1
    for data in entities:
        t = data.get('title').encode('utf8')
        if t not in titles:
            titles[t] = 1
        else:
            titles[t] = titles.get(t) + 1

    with open('record.txt', 'w') as f:
        for k,v in titles.iteritems():
            f.writelines('{}: {}\n'.format(k, v))
    f.close()
    
    print 'total tweets:', len(score)
    print 'total positive: ' , positive
    print 'total negative: ', negative
    print 'total unique entities: ', len(titles)
    mx = max(titles.values())
    print 'most frequent entity: ', [k for k, v in titles.iteritems() if v == mx]

    


if __name__ == '__main__':
    # twitter api keys
    consumer_key = 
    consumer_secret = 
    access_token = 
    access_secret = 

    # repustate api keys
    myRepustateKey = 

    # initilize twitter API
    twitterAPI = TwitterAPI(consumer_key, consumer_secret, access_token, access_secret)
    # initilize repustate API
    repustateAPI = RepustateAPI(myRepustateKey)

    # ask for user input
    query = raw_input('what keywords you want to search for: ')
    while not query:
        query = raw_input('(PLEASE ENTER YOUR KEYWORDS) what keywords you want to search for: ')
    count = raw_input('how many tweets you want to search for (<100): ' )
    while not count.isdigit() or int(count) >= 100:
        count = raw_input('(PLEASE ENTER A NUMBER) how many tweets you want to search for  (<100): ' )
    until = raw_input('tweets created before the given date. Date should be formatted as YYYY-MM-DD. Keep in mind that the search index has a 7-day limit, press enter for default value:today\'s date: ')
    result_type = raw_input('Specifies what type of search results you would prefer to receive. Valid input: mixed, recent, popular. Press Enter for default value:mixed: ')
    text = twitterAPI.getTweetsText(q=query, count=int(count), until=until, result_type=result_type)

    

    # display the results
    score = []
    titles = [] 
    if len(text) == 0:
        print 'There is no tweet match your search query'
    else:
        # write tweets to file
        with open("tweets.txt", "w") as f:
            for t in text:
                f.write('{} \n'.format(t))
        f.close()

        failCount = 0
        with open('ErrorLog.txt', "w") as f:
            for i in text:
                sentiment = repustateAPI.getSentiment(i)
                entities = repustateAPI.getEntities(i)
                if  sentiment.get('status') == 'Fail':
                    failCount+=1
                    f.write('{} \n'.format(i))
                    f.write('Sentiment request error: {} \n'.format(sentiment.get('description')))
                elif entities.get('status') == 'Fail':
                    f.write('{} \n'.format(i))
                    f.write('Entities request error: {} \n'.format(entities.get('description')))
                else:
                    score.append(sentiment)
                    for j in entities.get('entities'):
                        titles.append(j)
        f.close()

        if failCount < int(count):
            displayTool(score, titles)
        else:
            print 'Error, check error log'

        