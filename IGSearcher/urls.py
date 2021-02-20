"""IndieGameSearcher URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from gamesearcher import views

urlpatterns = [
    #USER ACTIONS
    path('', views.welcome),
    path('register', views.register),
    path('login', views.login),
    path('logout', views.logout),
    url(r'^games/search/$', views.search),
    url(r'^games/(?P<gameId>\d+)$', views.gameDetails),
    url(r'^start/platforms/$', views.choosePlatforms),
    url(r'^start/mainstreams/$', views.likeDislikeMainstream),
    url(r'^games/recommend/$', views.recommend),
    url(r'^games/recommendations/$', views.recommendations),
    
    #ADMIN ACTIONS
    url(r'^reloadDB/$', views.reloadDB),
    url(r'^extendDB/$', views.extendDB),
    url(r'^loadWH/$', views.loadWH),
    url(r'^loadRS/$', views.loadRS),

    path('admin/', admin.site.urls),
]
