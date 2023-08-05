from tweepy import Cursor
from tweepy import API
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import random


class Error(Exception):
    pass
class HTTP404Error(Error):
    pass
class AuthenthicationError(Error):
    pass

class _Login():
    def __init__(self,ac_tok = None, ac_tok_sec = None,con_tok = None,con_tok_sec = None):
        self.actok = ac_tok
        self.actoksec = ac_tok_sec
        self.contok = con_tok
        self.contoksec = con_tok_sec

    def authenticate_twitter_app(self):
        auth = OAuthHandler(self.contok,self.contoksec)
        auth.set_access_token(self.actok,self.actoksec)
        self.twitter_client = API(auth)
        return self.twitter_client

class accesstwitpy():
    def __init__(self,__access_token,__access_token_secret,__consumer_key,__consumer_key_secret):
        self.__api = _Login(__access_token, __access_token_secret,__consumer_key,__consumer_key_secret).authenticate_twitter_app()

    def pickuserfrom_retweet(self,id):
            try:
                res = self.__api.retweeters(id)
                choose = random.choice(res)
                res2 = self.__api.get_user(choose)
                self.username = res2.screen_name
                self.name = res2.name
                self.userid = res2.id
                self.followers = res2.followers_count
                self.following = res2.friends_count
                return self
            except Exception as e:
                raise HTTP404Error(f"An Error Occured: {e}")

    def get_tweetsfromuser(self,name,count):
        try:
            if count < 11:
                tweets = self.__api.user_timeline(screen_name=name,count= count, tweet_mode = 'extended')
                return tweets
            else:
                raise Error("You cannot fetch more than 10 tweets from a user.")
        except Exception as e:
            raise HTTP404Error(f"An Error Occured: {e}")
            
    def find_user(self,name):
        try:
            api = self.__api
            result = api.get_user(name)
            self.username = result.screen_name
            self.name = result.name
            self.userid = result.id
            self.created_at = result.created_at
            self.description = result.description
            self.followers = result.followers_count
            self.following = result.friends_count
            self.location = result.location
            self.tweets_count = result.statuses_count
            self.isVerified = result.verified
            self.avatar_url = result.profile_image_url
            return self
        except Exception as e:
            raise HTTP404Error(f"An Error Occured: {e}")
        
    def retweet_tweet(self,id):
        try:
            api = self.__api
            api.retweet(id)
        except Exception as e:
            raise HTTP404Error(f"An Error Occured: {e}")

    def follow_user(self,name):
        try:
            api = self.__api
            res = api.get_user(name)
            res.follow()
        except Exception as e:
              raise HTTP404Error(f"An Error Occured: {e}")
    
    def send_dm(self,name,text):
        try:
            api  = self.__api
            res = api.get_user(name)
            ID = res.id 
            api.send_direct_message(ID,text)
        except Exception as e:
            raise HTTP404Error(f"An Error Occured: {e}")
    
    def like_tweet(self,statusid):
        try:
            api = self.__api
            api.create_favorite(statusid)
        except Exception as e:
            raise HTTP404Error(f"An Error Occured: {e}")
    
    def unlike_tweet(self,statusid):
        try:
            api = self.__api
            api.destroy_favorite(statusid)
        except Exception as e:
            raise HTTP404Error(f"An error occured: {e}")


    

