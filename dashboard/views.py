from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from highcharts_core.chart import Chart
import pandas as pd
from .models import SugarPrice
from django.http import JsonResponse

@login_required
# Create your views here.
def home(request):
    #Fetch data and store in a dataframe
    prices = SugarPrice.objects.all().order_by('date')
    df = pd.DataFrame(list(prices.values()))
    
    #Convert the date column to a datetime object
    df['date'] = pd.to_datetime(df['date'])
        
    #Prepare data for Highcharts
    data = list(zip(df['date'].apply(lambda x: int(x.timestamp()) * 1000), df['amount']))
    
    chart = Chart.from_dict({
        'chart': {
            'type': 'line',
            'width': 850,
            'height': 600
        },
        'title': {
            'text': 'Sugar Prices'
        },
        'xAxis': {
            'type': 'datetime',
            'title': {
                'text': 'Date'
            }
        },
        'yAxis': {
            'title': {
                'text': 'Price'
            }
        },
        'series': [{
            'name': 'Average Sugar Price',
            'data': data
        }]
    })
    
    #Calculate KPIs
    today_price = df['amount'].iloc[-1]
    yesterday_price = df['amount'].iloc[-2]
    percentage_change = ((today_price - yesterday_price)/yesterday_price) * 100
    
    context = {
        'chart script': chart.to_json(),
        'today price': today_price,
        'yesterday price': yesterday_price,
        'percentage_change': round(percentage_change, 2),
    }
    return render(request, 'dashboard/home.html', context)

@login_required
def sugar_price_data(request):
    """
    This chart serves the data for our chart as a json response
    """
    prices = SugarPrice.objects.all().order_by('date')
    
    #Prepare the data
    data = [[int(price.data.strftime('%s'))*1000, price.amount]
            for price in prices]
    
    return JsonResponse(data, safe = False)

    
    
    
    
    
    
