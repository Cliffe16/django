from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
import pandas as pd
from .models import SugarPrice, User, UploadHistory, SupportTicket, Log
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
import datetime as dt
import json

def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

@login_required
def home(request):
    if request.user.role == 'admin':
        return redirect('admin_dashboard')

    prices = SugarPrice.objects.all().order_by('date')
    
    # --- THIS IS THE FIX ---
    # The `price.amount` is a Decimal. We must convert it to a float.
    chart_data = [
        [int(dt.datetime.combine(price.date, dt.time.min).timestamp()) * 1000, float(price.amount)] 
        for price in prices
    ]

    df = pd.DataFrame(list(prices.values('date', 'amount', 'rate')))
    df['date'] = pd.to_datetime(df['date'])

    today_price = df['amount'].iloc[-1]
    yesterday_price = df['amount'].iloc[-2]
    percentage_change = ((today_price - yesterday_price) / yesterday_price) * 100 if yesterday_price else 0
    fx_rate = df['rate'].iloc[-1]
    
    twelve_month_ago = df['date'].iloc[-1] - pd.DateOffset(years=1)
    twelve_month_data = df[df['date'] >= twelve_month_ago]
    annual_range_low = twelve_month_data['amount'].min()
    annual_range_high = twelve_month_data['amount'].max()

    context = {
        'today_price': f"KES {today_price:,.2f}",
        'yesterday_price': f"KES {yesterday_price:,.2f}",
        'percentage_change': f"{percentage_change:+.2f}%",
        'arrow': 'fa-caret-up' if percentage_change > 0 else 'fa-caret-down' if percentage_change < 0 else 'orange',
        'arrow_color': 'green' if percentage_change > 0 else 'red' if percentage_change < 0 else 'orange',
        'fx_rate': f"KES {fx_rate:,.2f}",
        'annual_range_low': f"KES {annual_range_low:,.2f}",
        'annual_range_high': f"KES {annual_range_high:,.2f}",
        'chart_data_json': json.dumps(chart_data)
    }
    return render(request, 'dashboard/home.html', context)

def sugar_price_data(request):
    prices = SugarPrice.objects.all().order_by('date')
    data = [
        [int(dt.datetime.combine(price.date, dt.time.min).timestamp()) * 1000, float(price.amount)] 
        for price in prices
    ]
    return JsonResponse(data, safe=False)

@login_required
def submit_support_ticket(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        description = request.POST.get('description')
        ticket = SupportTicket.objects.create(
            username=request.user.username,
            email=request.user.email,
            subject=subject,
            description=description
        )
        send_mail(
            f'Support Ticket #{ticket.id}: {subject}',
            f'Thank you for your support request. We have received it and will get back to you shortly.\n\nYour ticket number is: {ticket.id}',
            settings.DEFAULT_FROM_EMAIL,
            [request.user.email],
            fail_silently=False,
        )
        messages.success(request, f'Support Ticket #{ticket.id} has been submitted.')
    return redirect('home')

@user_passes_test(is_admin)
def admin_dashboard(request):
    total_users = User.objects.count()
    new_users = User.objects.filter(date_joined__gte=datetime.now() - timedelta(days=7)).count()
    active_sessions = Log.objects.filter(type='login', timestamp__gte=datetime.now() - timedelta(days=1)).count()

    context = {
        'total_users': total_users,
        'new_users': new_users,
        'active_sessions': active_sessions,
    }
    return render(request, 'admin/dashboard.html', context)

@user_passes_test(is_admin)
def user_management(request):
    users = User.objects.exclude(username=request.user.username)
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        user_to_manage = User.objects.get(id=user_id)

        if action == 'activate':
            user_to_manage.status = 'active'
        elif action == 'suspend':
            user_to_manage.status = 'suspended'
        elif action == 'delete':
            user_to_manage.delete()
            messages.success(request, f'User {user_to_manage.username} has been deleted.')
            return redirect('user_management')
        elif 'role' in request.POST:
            user_to_manage.role = request.POST.get('role')
        
        user_to_manage.save()
        messages.success(request, f'User {user_to_manage.username} has been updated.')
        return redirect('user_management')
        
    return render(request, 'admin/user_management.html', {'users': users})

@user_passes_test(is_admin)
def data_management(request):
    if request.method == 'POST' and request.FILES.get('data_upload'):
        csv_file = request.FILES['data_upload']
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a valid .csv file.')
            return redirect('data_management')

        try:
            df = pd.read_csv(csv_file)
            df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
            
            existing_dates = list(SugarPrice.objects.values_list('date', flat=True))
            new_data = df[~df['Date'].dt.date.isin(existing_dates)]

            if new_data.empty:
                messages.warning(request, 'No new data to upload. All dates already exist.')
                return redirect('data_management')
                
            for index, row in new_data.iterrows():
                SugarPrice.objects.create(
                    date=row['Date'].date(),
                    amount=row['Amount'],
                    rate=row['Rate']
                )

            UploadHistory.objects.create(
                admin_username=request.user.username,
                filename=csv_file.name,
                rows_added=len(new_data)
            )
            messages.success(request, f'{len(new_data)} new rows have been uploaded successfully.')

        except Exception as e:
            messages.error(request, f'An error occurred: {e}')
        
        return redirect('data_management')

    upload_history = UploadHistory.objects.all().order_by('-timestamp')
    return render(request, 'admin/data_management.html', {'upload_history': upload_history})

@user_passes_test(is_admin)
def logs(request):
    event_logs = Log.objects.all().order_by('-timestamp')
    return render(request, 'admin/logs.html', {'logs': event_logs})