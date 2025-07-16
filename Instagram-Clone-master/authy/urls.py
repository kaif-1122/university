from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Root URL - Welcome Page
    path('', views.welcome, name='welcome'),
    
    # Authentication URLs
    path('sign-in/', views.sign_in, name='sign-in'),
    path('sign-up/', views.register, name='sign-up'),
    path('sign-out/', views.sign_out, name='sign-out'),
    
    # Profile Section
    path('profile/edit/', views.EditProfile, name="editprofile"),
    path('profile/<str:username>/', views.UserProfile, name="profile"),
    path('follow/<str:username>/<int:option>/', views.follow, name="follow"),
     path('chatbot/', views.chatbot_view, name='chatbot'),
    path('get-response/', views.get_university_suggestions, name='get_university_suggestions'),
    # App URLs
    path('index/', views.index, name='index'),
]