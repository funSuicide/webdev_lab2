from django.urls import path
from app import views

urlpatterns = [path('index/', views.get_schedule_data, name='index')]

