# -*- coding: utf-8 -*-
"""
Created on Tue May  7 11:54:23 2019

@author: Pablosky
"""

import praw
import time
import os
import pandas as pd
import datetime
import sys




##This functions keeps track of the submission ids given
def followMe(reddit,ids):
    fileName="hotsInfo.csv"
    posts=[]
    j=0
    hotsInfo = pd.read_csv('hotsInfo.csv', encoding='utf8')
    hotsInfo.columns = ['id','subreddit','score','num_comments','upvote_ratio']
    ids = [item for item in ids if item not in hotsInfo.id.values]
    aux=len(ids)
    for ident in ids:
        print(aux-j)
        print(ident)
        j=j+1
        try:
            submission = reddit.submission(id=ident)
            posts.append([submission.id, submission.subreddit,submission.score, submission.num_comments,submission.upvote_ratio])
        except:
            print("Hubo excepccione")
            continue
        if j % 20 == 0:
            print("Escribiendo")
            posts = pd.DataFrame(posts,columns=['id','subreddit','score','num_comments','upvote_ratio'])
            csvfile = pd.read_csv(fileName, encoding='utf8')
            csvfile.columns = ['id','subreddit','score','num_comments','upvote_ratio']
            df=pd.concat([posts,csvfile])
            os.remove(fileName)
            df.to_csv(fileName, header=True,index=False)
            posts=[]
        
    posts = pd.DataFrame(posts,columns=['id','subreddit','score','num_comments','upvote_ratio'])
    csvfile = pd.read_csv(fileName, encoding='utf8')
    csvfile.columns = ['id','subreddit','score','num_comments','upvote_ratio']
    df=pd.concat([posts,csvfile])
    os.remove(fileName)
    df.to_csv(fileName, header=True,index=False)
 
  
##This function tells the user what ids already saved are hot
    
def ScrapMeUp(reddit,until):
    posts = pd.read_csv('doing.csv', encoding='utf8')
    posts.columns = ['id']
    print(posts.shape[0])
    followMe(reddit,posts.id.values.tolist())
            

subR="a"
if __name__ == "__main__":
    clId = str(sys.argv[1]).strip()
    clS = str(sys.argv[2]).strip()
    passW = str(sys.argv[3]).strip()
    userA = str(sys.argv[4]).strip()
    userN = str(sys.argv[5]).strip()

reddit = praw.Reddit(client_id=clId,
                 client_secret=clS,
                 password=passW,
                 user_agent='dudy',
                 username=userN)

#subR=['funny','askreddit','gaming','pics','science','worldnews','todayilearned','aww','movies','videos','gifs','earthporn','showerthoughts','blog','explainlikeimfive','books','jokes','lifeprotips','diy','television','sports','art','pcgaming','trashy','outoftheloop','backpacking','sex','eatcheapandhealthy','choosingbeggars','nevertellmetheodds','quityourbullshit','cringe','starwars','publicfreakout','horror','japantravel','holdmycosmo','the_donald','math','savedyouaclick']
#ScrapMeUp(['askreddit','science','worldnews','todayilearned','todayilearned','news','earthporn','books','jokes','lifeprotips'],200,(time.time()+40))
ScrapMeUp(reddit,(time.time()+604800))

        

