from datetime import datetime
from json import dumps
import pandas as pd
import requests as rq
from django.shortcuts import render

import asyncio
import aiohttp


# Create your views here.

def home(request):    
    return render(request,'home.html')

def register(request):
    return render(request,'register.html')

def notRegistered(request):
    return render(request,'notregistered.html')

def login(request):
    return render(request,'login.html')

def profile(request):
    return render(request,'profile.html')


def nsebse(request):
    if request.user.is_authenticated:
        endpoint1 = rq.get('https://stockindex.up.railway.app/api/bse/').json()
        endpoint2 = rq.get('https://stockindex.up.railway.app/api/nse/').json()
        bseData = helperForBSENSE(endpoint1)
        nseData = helperForBSENSE(endpoint2)
        return render(request,'nsebse.html',{'bseData':bseData,'nseData':nseData})
    else:
        return render(request,'notauth.html')

def companies(request):
    if request.user.is_authenticated:
        ashok = rq.get('https://stockindex.up.railway.app/api/ashok/').json()
        cipla = rq.get('https://stockindex.up.railway.app/api/cipla/').json()
        eicher = rq.get('https://stockindex.up.railway.app/api/nse/').json()
        reliance = rq.get('https://stockindex.up.railway.app/api/bse/').json()
        tata = rq.get('https://stockindex.up.railway.app/api/nse/').json()

 
        ashok_oneyr_high_values,ashok_oneyr_dates = helperForCompanies(ashok)
        cipla_oneyr_high_values,cipla_oneyr_dates = helperForCompanies(cipla)
        eicher_oneyr_high_values,eicher_oneyr_dates = helperForCompanies(eicher)
        reliance_oneyr_high_values,reliance_oneyr_dates = helperForCompanies(reliance)
        tata_oneyr_high_values,tata_oneyr_dates = helperForCompanies(tata)


        context = {'ashok_oneyr_high_values':ashok_oneyr_high_values,
                    'ashok_oneyr_dates':ashok_oneyr_dates,
                    'cipla_oneyr_high_values':cipla_oneyr_high_values,
                    'cipla_oneyr_dates':cipla_oneyr_dates,
                    'eicher_oneyr_high_values':eicher_oneyr_high_values,
                    'eicher_oneyr_dates':eicher_oneyr_dates,
                    'reliance_oneyr_high_values':reliance_oneyr_high_values,
                    'reliance_oneyr_dates':reliance_oneyr_dates,
                    'tata_oneyr_high_values':tata_oneyr_high_values,
                    'tata_oneyr_dates':tata_oneyr_dates,
                    }
        return render(request,'companies.html',context)
    else:
        return render(request,'notauth.html')





def helperForCompanies(data):

    df = pd.json_normalize(data)
    df = df.drop(['id'], axis=1)
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year

        
    today, req_day = datetime(2023,1,12), datetime(2022,1,12)
    one_year_df = df[(df['date'] <= today) & (df['date'] > req_day)]

    oneyr_high_values = dumps(list(one_year_df['high']))
    oneyr_dates = dumps(list(df['date'].astype(str)))

    return oneyr_high_values,oneyr_dates



def helperForBSENSE(data):
    df = pd.json_normalize(data)
    df = df.drop(['id'], axis=1)
    df['date']= pd.to_datetime(df['date'])
    today, req_day = datetime(2023,1,12), datetime(2022,1,12)

    one_year_df = df.query('date <= @today and date > @req_day')
    fifty_two_week_high = one_year_df['high'].max()
    fifty_two_week_low = one_year_df['low'].min()

    day_high = df.query('date == @today')['high'].values[0]
    day_low = df.query('date == @today')['low'].values[0]

    previous_day = today - pd.Timedelta(days=1)
    today_close = df.query('date == @today')['close'].values[0]
    prev_close = df.query('date == @previous_day')['close'].values[0]

    today_open = df.query('date == @today')['open'].values[0]
    today_gain_or_loss = today_close - prev_close

    data = {
            'today_open':today_open,
            'today_close':today_close,
            'prev_close': prev_close,
            'today_gain_or_loss' : today_gain_or_loss,
            'day_high':day_high,
            'day_low':day_low,
            'fifty_two_week_high':fifty_two_week_high,
            'fifty_two_week_low':fifty_two_week_low,
            'xAxis':list(df['date']),
            'yAxis':list(df['close']),
            }
    return data
