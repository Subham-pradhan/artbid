# auctions/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_painting, name='upload_painting'),
    path('', views.painting_list, name='painting_list'),
    path('bid/<int:painting_id>/', views.place_bid, name='place_bid'),
    path('results/', views.auction_results, name='auction_results'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('predict/<int:painting_id>/', views.predict_price, name='predict_price'),
]
