from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api_sugar_price_data/', views.sugar_price_data, name='sugar-price-data'),
]
