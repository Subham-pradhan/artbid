# auctions/admin.py
from django.contrib import admin
from .models import Artist, Painting, Bid, AuctionData

admin.site.register(Artist)
admin.site.register(Painting)
admin.site.register(Bid)
admin.site.register(AuctionData)
