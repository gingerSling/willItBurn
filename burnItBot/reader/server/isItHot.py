import pandas as pd
import praw
import sys
import os
import datetime
import time
from shutil import copyfile


#indeeed = pd.read_csv('files/indeedItBurnt.csv', encoding='utf8')

def getMeanPost(reddit,subreddit):
    from operator import itemgetter
    trn=time.time()
    subsm=[]
    for i in (subreddit.new(limit=1000)):
        subsm.append(abs(86400-trn+i.created_utc))
    mP=(min(enumerate(subsm), key=itemgetter(1))[0]+1)
    d = {
    'subreddit':[subreddit.title],
    'meanPost':[mP]
    }
    df1 = pd.DataFrame(d,columns=['subreddit','meanPost'])
    csvfile = pd.read_csv('subRM.csv', encoding='utf8')
    csvfile.columns = ['subreddit','meanPost']
    df=pd.concat([csvfile,df1])
    os.remove('subRM.csv')
    df.to_csv('subRM.csv', header=True,index=False)
    

def whosHot(reddit,limit):
    until=time.time() + limit
    subR=['wtf','technology','futurology','funny','pics','showerthoughts','the_donald','unpopularopinion','aww','gaming','videos','jokes','worldnews','art','sex','todayilearned','explainlikeimfive','starwars','movies','earthporn','trashy','horror','television','gifs','science','pcgaming','news','publicfreakout','choosingbeggars','lifeprotips','backpacking','math','japantravel','cringe','nevertellmetheodds','quityourbullshit','books','diy','outoftheloop','eatcheapandhealthy','datascience','sports','music']
    subRC = pd.read_csv('subRM.csv', encoding='utf8')
    subRC.columns = ['subreddit','meanPost']
    while time.time() < until:
        print("Lets see whats burning!")
        posts=[]
        hots = pd.read_csv('whosHot.csv', encoding='utf8')
        whosHot.columns = ['id','time']
        for subs in subR:
            sub=reddit.subreddit(subs)
            try:
                aux=subRC[subRC['subreddit']==sub.title]
            except:
                print('there was an error on the subreddit ' + subs)
                continue
            nPosts=int(round(aux['meanPost']*0.1))
            if nPosts>15:
                nPosts=15   
            for j in sub.hot(limit=nPosts):
                id = j.id
                if(id not in hots.id.values):
                    posts.append([id,time.time()])
        posts = pd.DataFrame(posts,columns=['id','time'])
        df=pd.concat([hots,posts])
        os.remove('whosHot.csv')
        df.to_csv('whosHot.csv', header=True,index=False)

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


whosHot(reddit,limite)
    
    
