from django.urls import path, include
from .views import inicio, home, registrar, login_view
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('',inicio, name='inicio'),
    path('home/',home, name='home'),
    path('registrar/', registrar, name='registrar'),
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]