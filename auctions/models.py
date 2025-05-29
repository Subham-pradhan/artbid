# auctions/models.py
from django.db import models
from django.contrib.auth.models import User

class Artist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    reputation = models.FloatField(default=0.0)

class Painting(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    style = models.CharField(max_length=100)
    starting_price = models.FloatField()
    image = models.ImageField(upload_to='paintings/')
    date_uploaded = models.DateTimeField(auto_now_add=True)

class Bid(models.Model):
    painting = models.ForeignKey(Painting, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

class AuctionData(models.Model):
    painting = models.OneToOneField(Painting, on_delete=models.CASCADE)
    artist_reputation = models.FloatField()
    style = models.CharField(max_length=100)
    starting_price = models.FloatField()
    final_price = models.FloatField()
