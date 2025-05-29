# auctions/utils.py
from django.db.models import Avg, Count, Max
from .models import Artist, Painting, Bid, AuctionData
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta


def calculate_artist_reputation():
    # Calculate maximums globally for normalization (avoid divide by zero)
    max_paintings = Artist.objects.annotate(p_count=Count('painting')).aggregate(Max('p_count'))['p_count__max'] or 1
    max_bids = Artist.objects.annotate(bid_count=Count('painting__bid')).aggregate(Max('bid_count'))['bid_count__max'] or 1
    max_price = AuctionData.objects.values('painting__artist').annotate(avg_price=Avg('final_price')).aggregate(Max('avg_price'))['avg_price__max'] or 1

    for artist in Artist.objects.all():
        painting_count = Painting.objects.filter(artist=artist).count()
        bid_count = Bid.objects.filter(painting__artist=artist).count()
        avg_final_price = AuctionData.objects.filter(painting__artist=artist).aggregate(Avg('final_price'))['final_price__avg'] or 0

        reputation = (
            (painting_count / max_paintings) * 0.2 +
            (bid_count / max_bids) * 0.3 +
            (avg_final_price / max_price) * 0.5
        )

        artist.reputation = round(reputation, 4)
        artist.save()



# def recommend_paintings_for_user(user, limit=5):
#     # Get user's bidding history
#     user_bids = Bid.objects.filter(user=user).select_related('painting__artist')

#     if not user_bids.exists():
#         # No history: recommend popular or latest paintings
#         return Painting.objects.order_by('-id')[:limit]

#     # Count user's favorite styles or artists
#     style_counts = {}
#     artist_counts = {}

#     for bid in user_bids:
#         style = bid.painting.style
#         artist = bid.painting.artist_id
#         style_counts[style] = style_counts.get(style, 0) + 1
#         artist_counts[artist] = artist_counts.get(artist, 0) + 1

#     # Rank paintings by style/artist similarity
#     paintings = Painting.objects.exclude(bid__user=user)

#     # Score paintings by user preferences
#     scored_paintings = []
#     for p in paintings:
#         score = style_counts.get(p.style, 0) + artist_counts.get(p.artist_id, 0)
#         if score > 0:
#             scored_paintings.append((score, p))

#     # Sort and return top recommendations
#     scored_paintings.sort(key=lambda x: x[0], reverse=True)
#     return [p for _, p in scored_paintings[:limit]]




def recommend_paintings_for_user(user, limit=5):
    # Get user's bidding history
    user_bids = Bid.objects.filter(user=user).select_related('painting__artist')

    # Count preferred styles and artists from user's bids
    style_counts = {}
    artist_counts = {}

    for bid in user_bids:
        style = bid.painting.style
        artist = bid.painting.artist_id
        style_counts[style] = style_counts.get(style, 0) + 1
        artist_counts[artist] = artist_counts.get(artist, 0) + 1

    # Recent period for trend detection (e.g., last 30 days)
    recent_period = timezone.now() - timedelta(days=30)

    # Get trending styles based on recent bids
    trending_styles = (
        Bid.objects.filter(timestamp__gte=recent_period)
        .values('painting__style')
        .annotate(style_count=Count('id'))
    )
    trending_dict = {entry['painting__style']: entry['style_count'] for entry in trending_styles}

    # Get paintings not already bid on by the user
    paintings = Painting.objects.exclude(bid__user=user)

    # Score each painting
    scored_paintings = []
    for painting in paintings:
        score = 0
        score += style_counts.get(painting.style, 0) * 2         # user style preference
        score += artist_counts.get(painting.artist_id, 0) * 3    # user artist preference
        score += trending_dict.get(painting.style, 0) * 1        # market trend (recent bid count)

        if score > 0:
            scored_paintings.append((score, painting))

    # Sort and return top recommendations
    scored_paintings.sort(key=lambda x: x[0], reverse=True)
    return [painting for _, painting in scored_paintings[:limit]]
