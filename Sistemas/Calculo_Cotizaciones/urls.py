from django.urls import path, include
from .views import inicio,home2


urlpatterns = [
    path('',inicio, name='inicio'),
    path('home2/',home2, name='home2'),
]