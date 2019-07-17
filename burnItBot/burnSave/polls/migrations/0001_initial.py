# Generated by Django 2.2.3 on 2019-07-16 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='rawDat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=2000)),
                ('author', models.DateTimeField(verbose_name='date published')),
                ('edited', models.CharField(max_length=10)),
                ('is_self', models.CharField(max_length=10)),
                ('locked', models.CharField(max_length=10)),
                ('spoiler', models.CharField(max_length=10)),
                ('stickied', models.CharField(max_length=10)),
                ('score', models.IntegerField(default=0)),
                ('upvote_ratio', models.DecimalField(decimal_places=5, max_digits=5)),
                ('idP', models.CharField(max_length=30)),
                ('subreddit', models.CharField(max_length=30)),
                ('url', models.CharField(max_length=2000)),
                ('num_comments', models.IntegerField(default=0)),
                ('body', models.IntegerField(default=0)),
                ('created', models.CharField(max_length=80)),
                ('measured', models.CharField(max_length=80)),
            ],
        ),
    ]
