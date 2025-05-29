from django.shortcuts import render, redirect, get_object_or_404
from .models import Painting, Bid, Artist, AuctionData
from .forms import PaintingForm, BidForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.views.decorators.csrf import csrf_exempt
import joblib
from django.http import JsonResponse
from .ml.train_model import train_price_predictor
from .utils import calculate_artist_reputation,recommend_paintings_for_user


@login_required
def upload_painting(request):
    if request.method == 'POST':
        form = PaintingForm(request.POST, request.FILES)
        if form.is_valid():
            painting = form.save(commit=False)
            painting.artist = request.user.artist
            painting.save()
            return redirect('painting_list')
    else:
        form = PaintingForm()
    return render(request, 'upload.html', {'form': form})

def painting_list(request):
    paintings = Painting.objects.all()
    return render(request, 'painting_list.html', {'paintings': paintings})

@csrf_exempt
def predict_price(request, painting_id):
    painting = get_object_or_404(Painting, id=painting_id)
    try:
        model = joblib.load('auctions/ml/models/price_model.pkl')
        encoder = joblib.load('auctions/ml/models/style_encoder.pkl')
    except FileNotFoundError:
        return JsonResponse({'error': 'Model not trained yet.'}, status=500)

    style_encoded = encoder.transform([painting.style])[0]
    features = [[painting.artist.reputation, style_encoded, painting.starting_price]]
    predicted_price = model.predict(features)[0]
    return JsonResponse({'predicted_price': round(predicted_price, 2)})


@login_required
def place_bid(request, painting_id):
    painting = get_object_or_404(Painting, id=painting_id)
    if request.method == 'POST':
        form = BidForm(request.POST)
        if form.is_valid():
            bid = form.save(commit=False)
            bid.user = request.user
            bid.painting = painting
            bid.save()

            # Recalculate reputation
            calculate_artist_reputation()

            # Update AuctionData
            top_bid = Bid.objects.filter(painting=painting).order_by('-amount').first()
            if top_bid:
                AuctionData.objects.update_or_create(
                    painting=painting,
                    defaults={
                        'artist_reputation': painting.artist.reputation,
                        'style': painting.style,
                        'starting_price': painting.starting_price,
                        'final_price': top_bid.amount,
                    }
                )

            train_price_predictor()  # retrain after each bid
            return redirect('painting_list')
    else:
        form = BidForm()
    return render(request, 'bid.html', {'form': form, 'painting': painting})


def auction_results(request):
    results = []
    for painting in Painting.objects.all():
        highest_bid = Bid.objects.filter(painting=painting).order_by('-amount').first()
        if highest_bid:
            results.append({
                'painting': painting,
                'final_price': highest_bid.amount,
                'winner': highest_bid.user.username
            })
    return render(request, 'results.html', {'results': results})

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Artist.objects.create(user=user)
            login(request, user)
            return redirect('painting_list')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('painting_list')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    recommendations = recommend_paintings_for_user(request.user)
    return render(request, 'dashboard.html', {'recommended_paintings': recommendations})
