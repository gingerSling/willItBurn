# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 12:46:07 2019

@author: Pablosky
"""
import pandas as pd
import praw
import sys
import os
import datetime
import time
import random

def checkAv(av):
    res=[]
    cont=0
    for i in av:
        res.extend([cont]*i)
        cont=cont+1
    return res
  
def serveMe(reddit,limit,subs):
    until=time.time() + limit
    
    if subs==1: 
        subR=['futurology','music','funny','gaming','worldnews','todayilearned','explainlikeimfive','television','pcgaming','choosingbeggars','lifeprotips','outoftheloop','quityourbullshit','datascience']
    elif subs==2:
        subR=['technology','aww','pics','videos','art','earthporn','publicfreakout','starwars','sports','gifs','math','backpacking','eatcheapandhealthy','science']
    elif subs==3:
        subR=['wtf','showerthoughts','unpopularopinion','jokes','sex','movies','horror','news','trashy','books','diy','japantravel','cringe','nevertellmetheodds']

    fileNames=list(filter(lambda x:'reader' in x, next(os.walk('..'))[1]))
    fileNames = ['../'+item + '/doing.csv'for item in fileNames]
    pathHistoric=''
    if subs==1: 
        fileNames=fileNames[0:6]
        pathHistoric='historic1.csv'
    elif subs==2:
        fileNames=fileNames[6:13]
        pathHistoric='historic2.csv'
    elif subs==3:
        fileNames=fileNames[13:19]
        pathHistoric='historic3.csv'
    print(fileNames)
    time.sleep(10)
    while time.time() < until:
        print('Lets see whats new')
        print(datetime.datetime.now())
        historic = pd.read_csv(pathHistoric, encoding='utf8')
        historic.columns = ['id']
        files=[]
        for i in fileNames:
            aux=pd.read_csv(i, encoding='utf8')
            aux.columns = ['id']
            files.append(aux)
        av=[]
        for i in files:
            av.append(60-i.shape[0])
        news=[]
        for subs in subR:
            sub=reddit.subreddit(subs)
            for j in sub.new(limit=7):
                if (time.time()-j.created_utc)<120:
                    news.append(j.id)
                else:
                    break
        news = [item for item in news if item not in historic.id.values]
        print(news)
        disp=checkAv(av)
        if len(disp) < len(news):
            news=news[0:len(disp)]
        assign=random.sample(disp,len(news))
        for i in range(len(assign)):
            aux = pd.DataFrame([news[i]],columns=['id'])
            files[assign[i]]=pd.concat([files[assign[i]],aux])
        for i in range(len(fileNames)):
            os.remove(fileNames[i])
            files[i].to_csv(fileNames[i], header=True,index=False)
        news = pd.DataFrame(news,columns=['id'])
        historic=pd.concat([historic,news])
        os.remove(pathHistoric)
        historic.to_csv(pathHistoric, header=True,index=False)


if __name__ == "__main__":
    clId = str(sys.argv[1]).strip()
    clS = str(sys.argv[2]).strip()
    passW = str(sys.argv[3]).strip()
    userA = str(sys.argv[4]).strip()
    userN = str(sys.argv[5]).strip()
    limit = int(sys.argv[6])
    subs = int(sys.argv[7])

#subR=[,,,]

reddit = praw.Reddit(client_id=clId,
				 client_secret=clS,
				 password=passW,
                 user_agent='dudy',
				 username=userN)

serveMe(reddit,limit,subs)
