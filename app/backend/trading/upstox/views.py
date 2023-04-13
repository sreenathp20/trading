from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from upstox.upstox import Upstox


# Create your views here.

def index(request):
    return HttpResponse("You're looking at question ")

def nseindexniftybank(request):
    u = Upstox()
    data = u.getTickData('niftybankticks')
    data = u.getEMAData(data)
    return JsonResponse(data, safe=False)