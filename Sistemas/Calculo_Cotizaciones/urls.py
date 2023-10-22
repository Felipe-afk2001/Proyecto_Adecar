from django.urls import path, include
from .views import inicio,home


urlpatterns = [
    path('',inicio, name='inicio'),
    path('home/',home, name='home'),
]