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


def f2(seq): 
   # order preserving
   checked = []
   for e in seq:
       if e not in checked:
           checked.append(e)
   return checked


def funcAllNight(x):
    return len(x)


##This function computes the number of post in the subreddit indicated in the
##actual day
    
##This function tells if the given submission is in the 10 percentile of its hot
##This function tells if the given submission is in the 10 percentile of its hot
def amIHot(posts):
    whosHot=pd.read_csv('../server/whosHot.csv', encoding='utf8')
    whosHot.columns = ['id','time']
    done=pd.read_csv('done.csv', encoding='utf8')
    done.columns = ['id']
    hots= [item for item in posts if item in whosHot.id.values]
    hots=pd.DataFrame(hots,columns=['id'])
    done=pd.concat([done,hots])
    os.remove('done.csv')   
    done.to_csv('done.csv', header=True,index=False)       





##This functions keeps track of the submission ids given
def followMe(reddit,ids):
    fileName="post.csv"
    posts=[]
    for ident in ids:
        submission = reddit.submission(id=ident)
        posts.append([submission.title,submission.author,submission.edited,submission.is_self,submission.locked,submission.spoiler,submission.stickied, submission.score, submission.id, submission.subreddit, submission.url, submission.num_comments, submission.selftext, submission.created_utc,time.time()])
    posts = pd.DataFrame(posts,columns=['title','author','edited','is_self','locked','spoiler','stickied', 'score','id', 'subreddit', 'url', 'num_comments','body', 'created','measured'])
    posts["body"] = posts["body"].apply(funcAllNight)
    csvfile = pd.read_csv(fileName, encoding='utf8')
    csvfile.columns = ['title','author','edited','is_self','locked','spoiler','stickied', 'score','id', 'subreddit', 'url', 'num_comments','body', 'created','measured']
    df=pd.concat([posts,csvfile])
    df=df.sort_values(by=['measured'])
    dfNM=df.drop(['measured'], axis=1)
    df=df.loc[dfNM.duplicated()==False,:]
    os.remove(fileName)
    df.to_csv(fileName, header=True,index=False)
 
  
##This function tells the user what ids already saved are hot
    

    


##This function return the posts ids that are younger than 4.16 hours.
def forgotten(ids):
    trn=time.time()
    times=[]
    fileName="post.csv"
    csvfile = pd.read_csv(fileName, encoding='utf8')
    csvfile.columns = ['title','author','edited','is_self','locked','spoiler','stickied', 'score', 'id', 'subreddit', 'url', 'num_comments', 'body', 'created','measured']
    csvfile=csvfile.drop_duplicates('id')
    for ident in ids:
        submission = csvfile[(csvfile['id'] == ident)]
        if len(submission)==0:
            times.append(600)
        else:
            times.append(trn-submission.created.values)
    res=[ j for (i,j) in zip(times,ids) if i >= 1500 ]
    done=pd.read_csv('done.csv', encoding='utf8')
    done.columns = ['id']
    res=pd.DataFrame(res,columns=['id'])
    done=pd.concat([done,res])
    os.remove('done.csv')   
    done.to_csv('done.csv', header=True,index=False) 
    
def update():
    done=pd.read_csv('done.csv', encoding='utf8')
    done.columns = ['id']
    doing = pd.read_csv('doing.csv', encoding='utf8')
    doing.columns = ['id']
    doing=[item for item in doing.id.values.tolist() if item not in done.id.values.tolist()]
    doing=pd.DataFrame(doing,columns=['id'])
    os.remove('doing.csv')   
    doing.to_csv('doing.csv', header=True,index=False)
    
    
def ScrapMeUp(reddit,until):
    while(time.time()<until):
        print(datetime.datetime.now())
        posts = pd.read_csv('doing.csv', encoding='utf8')
        posts.columns = ['id']
        print(posts.shape[0])
        print(posts.id.values.tolist())
        followMe(reddit,posts.id.values.tolist())
        amIHot(posts.id.values.tolist())
        forgotten(posts.id.values.tolist())
        update()
            

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

        

