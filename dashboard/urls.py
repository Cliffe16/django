from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api_sugar_price_data/', views.sugar_price_data, name='sugar-price-data'),
    path('submit-ticket/', views.submit_support_ticket, name='submit_support_ticket'),
    # Admin URLs 
    path('admin-panel/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/user-management/', views.user_management, name='user_management'),
    path('admin-panel/data-management/', views.data_management, name='data_management'),
    path('admin-panel/logs/', views.logs, name='logs'),
]