# -*- coding: utf-8 -*-
"""
Created on Mon May 27 09:03:17 2019

@author: Pablosky
"""

import praw
from urllib.parse import quote_plus
import pandas as pd
import sys
import os
import subprocess
import time
import shutil

##Hay que anadir un while para dar limite de tiempo
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:  
            yield
        finally:
            sys.stdout = old_stdout

def getRedditorsInfo(reddit):
    names = pd.read_csv('files/notFunnyNames.csv', encoding='utf8')
    names.columns = ['id']
    namesInfo = pd.read_csv('files/namesInfo.csv', encoding='utf8')
    namesInfo.columns = ['id','commentN','commentK','commentR','postN','postK','postR','trophiesN','has_verified_email','is_gold']
    redditorsInfo=[]
    newRedditors=[]
    newRedditors = [item for item in names.id.values if item not in namesInfo.id.values]
    i=len(newRedditors)
    for redditor in newRedditors:
        if (i % 150) == 0:
            print("Escribiendo")
            redditorsInfo = pd.DataFrame(redditorsInfo,columns=['id','commentN','commentK','commentR','postN','postK','postR','trophiesN','has_verified_email','is_gold'])
            df=pd.concat([namesInfo,redditorsInfo])
            df.to_csv('files/namesInfo.csv', header=True,index=False)
            namesInfo = pd.read_csv('files/namesInfo.csv', encoding='utf8')
            namesInfo.columns = ['id','commentN','commentK','commentR','postN','postK','postR','trophiesN','has_verified_email','is_gold']
            redditorsInfo=[]
        i=i-1
        print(i)
        print(redditor)
        try:
            tor = reddit.redditor(redditor)
            kCom=tor.comment_karma
        except:
            redditorsInfo.append([redditor, 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error', 'error'])
            continue
        nComs=0
        for com in tor.comments.top('all',limit=350):
            nComs=nComs+1 
        nPosts=0
        for post in tor.submissions.top('all',limit=250):
            nPosts=nPosts+1
        nTrophies=0
        for troph in tor.trophies():
            nTrophies=nTrophies+1
        kPosts=tor.link_karma
        if nComs==0:
            rCom=0
        else:
            rCom=kCom/nComs
        if nPosts==0:
            rPosts=0
        else:
            rPosts=kPosts/nPosts
        redditorsInfo.append([redditor, nComs, kCom, rCom, nPosts, kPosts, rPosts, nTrophies, tor.has_verified_email, tor.is_gold])
    print("Escribiendo")
    redditorsInfo = pd.DataFrame(redditorsInfo,columns=['id','commentN','commentK','commentR','postN','postK','postR','trophiesN','has_verified_email','is_gold'])
    df=pd.concat([namesInfo,redditorsInfo])
    df.to_csv('files/namesInfo.csv', header=True,index=False)
    namesInfo = pd.read_csv('files/namesInfo.csv', encoding='utf8')
    namesInfo.columns = ['id','commentN','commentK','commentR','postN','postK','postR','trophiesN','has_verified_email','is_gold']
    

def readPosts(dir):
    fileNames=list(filter(lambda x:'reader' in x, next(os.walk(dir))[1]))
    fileNames = [dir+'/'+item + '/post.csv'for item in fileNames]
    files=[]
    for i in fileNames:
        fileName=i
        files.append(pd.read_csv(fileName, encoding='utf8'))
    dat=files[0]
    for i in range(1,len(files)):
        dat=pd.concat([dat,files[i]])   
    return dat


def commentMeUp(redSession,limit):
    until=time.time() + limit
    while time.time() < until:
        print("Another look to latest submissions")
        src='../reader'
        dat=readPosts(src)
        
        hasBurnt=pd.read_csv("files/itHasBurnt.csv", encoding='utf8')
        hasNotBurnt=pd.read_csv("files/itHasNotBurnt.csv", encoding='utf8')
        checked=hasBurnt['id'].values.tolist()
        notBurnt=hasNotBurnt['id'].values.tolist()
        checked.extend(notBurnt)
        dat=dat[-(dat.id.isin(checked))]
        dat.to_csv('files/dat.csv', header=True,index=False)
        
        #Linux (it needs the absolut path)
        subprocess.call (["/usr/bin/Rscript", "--vanilla", "burnItBot/writer/predictPost.r"])
        #Windows
        #subprocess.call (["C:/Program Files/R/R-3.5.2/bin/Rscript.exe", "--vanilla", "burnItBot/writer/predictPost.r"])
        itWillBurn = pd.read_csv('files/itWillBurn.csv', encoding='utf8')
        itWillBurn.columns = ['id','time']
        itHasBurnt = pd.read_csv('files/itHasBurnt.csv', encoding='utf8')
        itHasBurnt.columns = ['id','time','responseTime']
        posts = [item for item in itWillBurn.id.values if item not in itHasBurnt.id.values]
        
        for ident in posts:
            submission = redSession.submission(id=ident)
            reply_template =submission.title + '     This will burn in ' + str(itWillBurn[(itWillBurn['id'] == ident)].time.values[0])
            print(reply_template)
            url_title = quote_plus(submission.title)
            reply_text = reply_template.format(url_title)
            #submission.reply(reply_text)
            aux=[]
            aux=itWillBurn[(itWillBurn['id'] == ident)].values.tolist()
            aux = [item for sublist in aux for item in sublist]
            aux.append(time.time())
            aux=pd.DataFrame(aux).transpose()
            aux.columns = ['id','time','responseTime']
            itHasBurnt=pd.concat([itHasBurnt,aux])
            
        os.remove('files/itHasBurnt.csv')
        itHasBurnt.to_csv('files/itHasBurnt.csv', header=True,index=False)
    

if __name__ == "__main__":
    clId = str(sys.argv[1]).strip()
    clS = str(sys.argv[2]).strip()
    passW = str(sys.argv[3]).strip()
    userA = str(sys.argv[4]).strip()
    userN = str(sys.argv[5]).strip()
    limite = int(sys.argv[6])

reddit = praw.Reddit(client_id=clId,
				 client_secret=clS,
				 password=passW,
                 user_agent='dudy',
				 username=userN)

commentMeUp(reddit,limite)
