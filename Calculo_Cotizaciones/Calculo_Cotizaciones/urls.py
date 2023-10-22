
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('main_menu/', views.main_menu, name='main_menu'),
]
