import django
import pandas as pd
import os
import datetime
import numpy as np
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "burnSave.settings") 
django.setup()
from polls.models import rawDat, whosHot, whosTop

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

def readHot(dir):
    fileName= dir + '/whosHot.csv'
    hot=pd.read_csv(fileName, encoding='utf8')
    return hot
    
def readTop(dir):
    fileName= dir + '/whosTop.csv'
    top=pd.read_csv(fileName, encoding='utf8')
    return top
print("Writing on the DB")
print(datetime.datetime.now())
dat=readPosts('../reader')
dat.rename(columns={'id': 'idP'}, inplace=True)
dat['id'] = dat['idP'] + '_' + dat['measured'].astype(str)
dat.drop_duplicates(subset ="id", keep = 'first', inplace = True) 
df = pd.DataFrame(list(rawDat.objects.all().values('measured')))
last=float(np.max(df.measured.values))
dat=dat[dat.measured.values>last]
if(dat.shape[0]!=0):
    print("Data dimensions")
    print(dat.shape)

    for index, row in dat.iterrows():
        model = rawDat()
        model.id = row['id']
        model.title = row['title']
        model.author = row['author']
        model.edited = row['edited']
        model.is_self = row['is_self']
        model.locked = row['locked']
        model.spoiler = row['spoiler']
        model.stickied = row['stickied']
        model.score = row['score']
        model.upvote_ratio = row['upvote_ratio']
        model.idP = row['idP']
        model.subreddit = row['subreddit']
        model.url = row['url']
        model.num_comments = row['num_comments']
        model.body = row['body']
        model.created = row['created']
        model.measured = row['measured']
        model.save()
    

dat=readHot('../reader/server')
dat.drop_duplicates(subset ="id", keep = 'first', inplace = True) 
df = pd.DataFrame(list(whosHot.objects.all().values('time')))
last=float(np.max(df.time.values))
dat=dat[dat.time.values>last]
if(dat.shape[0]!=0 & df.shape[0]!=0):
    print(dat.shape)
if(dat.shape[0]!=0):
    print("Hot dimensions")
    print(dat.shape)
    for index, row in dat.iterrows():
        model = whosHot()
        model.id = row['id']
        model.time = row['time']
        model.save()
    
dat=readTop('../reader/server')
dat.drop_duplicates(subset ="id", keep = 'first', inplace = True) 
df = pd.DataFrame(list(whosTop.objects.all().values('time')))
last=float(np.max(df.time.values))
dat=dat[dat.time.values>last]

if(dat.shape[0]!=0 & df.shape[0]!=0):
    print(dat.shape)
if(dat.shape[0]!=0):
    print("Top dimensions")
    print(dat.shape)
    for index, row in dat.iterrows():
        model = whosTop()
        model.id = row['id']
        model.time = row['time']
        model.save()
