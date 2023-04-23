from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from upstox.upstox import Upstox
from datetime import datetime, timedelta

# Create your views here.

def index(request):
    return HttpResponse("You're looking at question ")

def nseindexniftybank(request):
    u = Upstox()
    data = u.getTickData('niftybankticks')
    data = u.getEMAData(data)
    return JsonResponse(data, safe=False)

def nseindexniftybankhistory(request):
    start = datetime(2023, 1, 6)
    end = start + timedelta(days=1)
    u = Upstox()
    data = u.getHistoryData('nseindexniftybank2', start, end)
    data = u.getHistoryEMAData(data)
    return JsonResponse(data, safe=False)

def nseindexniftybankprofit(request):
    u = Upstox()
    data = u.getProfitData('profit')
    #data = u.getHistoryEMAData(data)
    return JsonResponse(data, safe=False)

def nseindexniftybankloss(request):
    u = Upstox()
    data = u.getProfitData('loss')
    #data = u.getHistoryEMAData(data)
    return JsonResponse(data, safe=False)
