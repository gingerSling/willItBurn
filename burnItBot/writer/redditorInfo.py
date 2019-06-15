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
##Mail: abotwillbe@gmail.com
##Pass: 123qweASDzxc
##usr: willItBurnBot
##Pass: 123qweASDzxc
##Client_Id: CAzwzEHqy2zYtQ
##Client_Secret: d5SBs9S3HFBtLELjM9mAUPP2mcw
###Recordar que la cuenta a usar ha de tener el mail verificado y algo de karma (15-30)

##Hay que anadir un while para dar limite de tiempo

def getRedditorsInfo(reddit,limit):
    until=time.time() + limit
    change=0
    while time.time() < until:
        if change==os.path.getmtime('files/notFunnyNames.csv'):
            continue
        change=os.path.getmtime('files/notFunnyNames.csv')
        names = pd.read_csv('files/notFunnyNames.csv', encoding='utf8')
        names.columns = ['id']
        namesInfo = pd.read_csv('files/namesInfo.csv', encoding='utf8')
        namesInfo.columns = ['id','commentN','commentK','commentR','postN','postK','postR','trophiesN','has_verified_email','is_gold']
        redditorsInfo=[]
        newRedditors=[]
        newRedditors = [item for item in names.id.values if item not in namesInfo.id.values]
        i=len(newRedditors )
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

getRedditorsInfo(reddit,limite)
###Ejecuta scripts de R###

#subprocess.call (["C:/Program Files/R/R-3.5.2/bin/Rscript.exe", "--vanilla", "C:/Users/Pablosky/Desktop/thisWillBeOurTime/willItBurn-/burnItBot/stupidly.r"])


###Ejecuta scripts de R###



#print("Hey babe!")
#subreddit = reddit.subreddit('AskReddit')
#submission = reddit.submission(id='btiqqf')
#reply_template = 'wanna see me dancing?'
#url_title = quote_plus(submission.title)
#reply_text = reply_template.format(url_title)
#submission.reply(reply_text)    
