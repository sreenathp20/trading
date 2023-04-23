from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("nseindexniftybank", views.nseindexniftybank, name="nseindexniftybank"),
    path("nseindexniftybank-history", views.nseindexniftybankhistory, name="nseindexniftybank-history"),
    path("nseindexniftybank-profit", views.nseindexniftybankprofit, name="nseindexniftybank-profit"),
    path("nseindexniftybank-loss", views.nseindexniftybankloss, name="nseindexniftybank-loss"),
    
]