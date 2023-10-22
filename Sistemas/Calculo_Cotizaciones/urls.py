from django.urls import path, include
from .views import home2

urlpatterns = [
    path('',home2, name='home2')
]