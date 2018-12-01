from django.urls import path
from . import views
app_name = 'user'

urlpatterns = [
    path('login/', views.Login_View.as_view(),name='login'),
    path('signup/', views.Signup_View.as_view(),name='signup'),
    path('logout/', views.auth_logout,name='logout')
]