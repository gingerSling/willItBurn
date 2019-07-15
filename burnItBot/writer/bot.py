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
from selenium import webdriver
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


def sendMail(id,url):
    fromaddr = "sender@gmail.com"
    toaddr = ["reciever1@fgh.com","reciever2@asd.com"]

    msg = MIMEMultipart()

    msg['From'] = fromaddr
    msg['To'] = ", ".join(toaddr)
    msg['Subject'] = "This post will burn"

    body = url

    msg.attach(MIMEText(body, 'plain'))

    filename = 'screenshots/'+id+'.png'
    attachment = open('screenshots/'+id+'.png', "rb")

    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(fromaddr, "YourPass")
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()

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


def commentMeUp(redSession,email):
    until=time.time() + limit
    while time.time() < until:
        time.sleep(5)
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
        
        #Linux
        subprocess.call (["Rscript", "--vanilla", "predictPost.r"])
        #Windows
        #subprocess.call (["C:/Program Files/R/R-3.5.2/bin/Rscript.exe", "--vanilla", "C:/Users/Pablosky/Desktop/willItBurnBotOld/burnItBot/writer/predictPost.r"])
        itWillBurn = pd.read_csv('files/itWillBurn.csv', encoding='utf8')

        itWillBurn.columns = ['id','url']

        itHasBurnt = pd.read_csv('files/itHasBurnt.csv', encoding='utf8')

        itHasBurnt.columns = ['id','responseTime']

        posts = itWillBurn.merge(itHasBurnt, on=['id'], how='left', indicator=True)
        posts=posts[posts['_merge']=='left_only']
        subRC = pd.read_csv('subRM.csv', encoding='utf8')
        subRC.columns = ['subreddit','meanPost']
        for ident in posts.id.values.tolist():
            url=posts[posts['id']==ident].url.values[0]
            already=pd.read_csv("../reader/server/whosHot.csv", encoding='utf8')
            already.columns = ['id','time']
            submission = reddit.submission(id=ident)
            aux=subRC[subRC['subreddit']==submission.subreddit.title].meanPost.values.tolist()[0]
            nPosts=int(round(aux))
            if nPosts>15:
                nPosts=15

            driver = webdriver.Chrome("/usr/bin/chromedriver")
            driver.get(url)
            driver.save_screenshot('screenshots/' + ident + ".png")
            driver.close()
        if(email==1):
            sendMail(ident,url)
            aux=[]

            aux.append([ident,time.time()])

            aux = pd.DataFrame(aux,columns=['id','responseTime'])

            itHasBurnt=pd.concat([itHasBurnt,aux])
            
        os.remove('files/itHasBurnt.csv')
        itHasBurnt.to_csv('files/itHasBurnt.csv', header=True,index=False)
    


if __name__ == "__main__":
    clId = str(sys.argv[1]).strip()
    clS = str(sys.argv[2]).strip()
    passW = str(sys.argv[3]).strip()
    userA = str(sys.argv[4]).strip()
    userN = str(sys.argv[5]).strip()
    email = int(sys.argv[6])


reddit = praw.Reddit(client_id='CAzwzEHqy2zYtQ',
                 client_secret='d5SBs9S3HFBtLELjM9mAUPP2mcw',
                 password='123qweASDzxc',
                 user_agent='dudy',
                 username='willItBurnBot')

commentMeUp(reddit,email)
