from django.db import models

# Create your models here.
class rawDat(models.Model):
    title = models.CharField(max_length=2000)
    author = models.CharField(max_length=200)
    edited = models.CharField(max_length=10)
    is_self = models.CharField(max_length=10)
    locked = models.CharField(max_length=10)
    spoiler = models.CharField(max_length=10)
    stickied = models.CharField(max_length=10)
    score = models.IntegerField(default=0) 
    upvote_ratio = models.CharField(max_length=10)
    idP = models.CharField(max_length=30)
    subreddit = models.CharField(max_length=30)
    url = models.CharField(max_length=2000)
    num_comments = models.IntegerField(default=0) 
    body = models.IntegerField(default=0)
    created = models.CharField(max_length=80)
    measured = models.CharField(max_length=80)
    id  = models.CharField(max_length=110,primary_key=True)