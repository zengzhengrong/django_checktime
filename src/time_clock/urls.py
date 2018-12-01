from django.urls import path
from . import views

app_name = 'time_clock'

urlpatterns = [
    path('', views.UserActivity_View.as_view(),name='index'),
    path('history/', views.UserActivity_ListView.as_view(),name='history'),
    path('history/<datetype>/', views.UserActivity_ListView.as_view(),name='history-type')
]