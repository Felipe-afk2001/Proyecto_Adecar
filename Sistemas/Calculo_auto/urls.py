from django.urls import path, include
from .views import home1

urlpatterns = [
    path('', home1, name='home1')
]