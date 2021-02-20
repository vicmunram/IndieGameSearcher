#encoding:utf-8
from whoosh.index import open_dir
from whoosh.qparser import MultifieldParser
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth import login as do_login
from django.contrib.auth import logout as do_logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .forms import LoadDjangoDBForm, FilterForm, SearchForm, LikeMainstreanmsForm, LikeDislikeForm
from .models import Author, Genre, Platform, MainstreamGame, IndieGame, IGSUser, Tag
from .populate import loadDjangoDB, loadWhooshDB, deleteDjangoDB
from .recommendations import loadSimilarities, recommendGames
from datetime import date

#USER ACTIONS
def getLastGamesAdded():
    games = list(IndieGame.objects.all())
    games.sort(key=lambda x: x.id)       
    games = games[-3:]
    return games


def welcome(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            authorsNumber = Author.objects.all().count()
            genresNumber = Genre.objects.all().count()
            platformsNumber = Platform.objects.all().count()
            tagsNumber = Tag.objects.all().count()
            igames = IndieGame.objects.all().count()
            mgames = MainstreamGame.objects.all().count()
            igsUsers = IGSUser.objects.all().count()
            
            return render(request, "users/welcome.html", {"authorsNumber":authorsNumber,"genresNumber":genresNumber, "platformsNumber":platformsNumber,
                                                          "tagsNumber":tagsNumber, "igames":igames, "mgames":mgames, "igsUsers":igsUsers})
        else:
            igsUser = IGSUser.objects.get(user=request.user)
            notStarted = igsUser.platforms.count() == 0
            return render(request, "users/welcome.html", {"games":getLastGamesAdded(),"notStarted":notStarted})
    else:
        return render(request, "users/welcome.html", {"games":getLastGamesAdded()})
        
            
def register(request):
    if request.user.is_anonymous:
        form = UserCreationForm()
        if request.method == "POST":
            form = UserCreationForm(data=request.POST)
            if form.is_valid():
                user = form.save()
                if user is not None:
                    igsuser = IGSUser()
                    igsuser.user = user
                    igsuser.save()
                    
                    do_login(request, user)
                    return redirect('/')
    
        return render(request, "users/register.html", {'form': form})
    else:
        return redirect('/')

def login(request):
    if request.user.is_anonymous:
        form = AuthenticationForm()
        if request.method == "POST":
            form = AuthenticationForm(data=request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
    
                user = authenticate(username=username, password=password)
    
                if user is not None:
                    do_login(request, user)
                    return redirect('/')
    
        return render(request, "users/login.html", {'form': form})
    else:
        return redirect('/')

def logout(request):
    do_logout(request)
    return redirect('/')

#SEARCH

def filterPlatforms(targetPlatforms,games):
    for platform in targetPlatforms:
        games = games.filter(platforms=platform)
    
    return games

def filterGenres(targetGenres,games):
    for genre in targetGenres:
        games = games.filter(genres=genre)
    
    return games

def filterDates(firstDate,lastDate,games):
    if not firstDate: firstDate = '1949-12-12'
    if not lastDate: lastDate = date.today()
    games = games.filter(lastVersionDate__range=[firstDate, lastDate])

    return games

def filterText(query,games,title,description,tags,author):
    ix = open_dir("igs_index")
    
    params = []
    if title: params.append("title")
    if description: params.append("description")
    if tags: params.append("tags")
    if author: params.append("authors")

    with ix.searcher() as searcher:
        query = MultifieldParser(params, ix.schema).parse(query)
        results = searcher.search(query)
        idList = []
        for r in results:
            idList.append(int(r['idIndieGame']))
        
    games = games.filter(id__in=idList)
    
    return games


def search(request):
    if request.method == "GET":
        searchForm = SearchForm()
        filterForm = FilterForm()
        return render(request, "users/search.html", {"filterForm":filterForm, "searchForm":searchForm})
    
    if request.method == "POST":
        searchForm = SearchForm(data=request.POST)
        filterForm = FilterForm(data=request.POST)
        if searchForm.is_valid() and filterForm.is_valid():
            games = IndieGame.objects.all()
            
            targetPlatforms = filterForm.cleaned_data['platforms']
            games = filterPlatforms(targetPlatforms, games)
            
            targetGenres = filterForm.cleaned_data['genres']
            games = filterGenres(targetGenres, games)
            
            targetStatus = filterForm.cleaned_data['status']
            if targetStatus: games = games.filter(status=targetStatus)
            
            firstDate = filterForm.cleaned_data['firstDate']
            lastDate = filterForm.cleaned_data['lastDate']
            if firstDate or lastDate: games = filterDates(firstDate,lastDate,games)
            
            targetText = searchForm.cleaned_data['text']
            targetTitle = searchForm.cleaned_data['title']
            targetDescription = searchForm.cleaned_data['description']
            targetTags = searchForm.cleaned_data['tags']
            targetAuthor = searchForm.cleaned_data['author']
            if targetText: games = filterText(targetText,games,targetTitle,targetDescription,targetTags,targetAuthor)
            
            return render(request, "users/list.html", {"games": games})
            
        return render(request, "users/search.html", {"filterForm":filterForm, "searchForm":searchForm})
    
def gameDetails(request,gameId):
    if request.method == "GET":
        game = get_object_or_404(IndieGame, pk=gameId)
        likeDislikeForm = None
        
        if request.user.is_authenticated and not request.user.is_staff:
            igsUser = IGSUser.objects.get(user=request.user)
            isRecommended = igsUser.recommendedGames.all().filter(id=gameId)
            if isRecommended: 
                likeDislikeForm = LikeDislikeForm()
        
        return render(request,'users/gameDetails.html',{'game': game, 'likeDislikeForm': likeDislikeForm})
    
    elif request.method == "POST":
        game = get_object_or_404(IndieGame, pk=gameId)
        likeDislikeForm = LikeDislikeForm(data=request.POST)
        if likeDislikeForm.is_valid():
            igsUser = IGSUser.objects.get(user=request.user)
            likeDislike = likeDislikeForm.cleaned_data['likeDislike']
            igsUser.recommendedGames.remove(gameId)
            if likeDislike == 'yes': 
                igsUser.likedIndieGames.add(gameId)
            else:
                igsUser.dislikedIndieGames.add(gameId)
            
            return redirect('/games/recommendations')
        
        return render(request,'users/gameDetails.html',{'game': game, 'likeDislikeForm': likeDislikeForm})
        
    else:
        return redirect('/')
    

#RECOMMEND ACTIONS
def choosePlatforms(request):
    if request.user.is_authenticated and not request.user.is_staff:
        igsUser = IGSUser.objects.get(user=request.user)
        if igsUser.platforms.count() == 0 or (igsUser.platforms.count() != 0 and igsUser.likedMainstreamGames.count() != 0):
            if request.method == "POST":
                platforms = request.POST.getlist('platforms')

                userPlatforms = []
                for p in platforms:
                    platform = Platform.objects.get(name=p.replace("/",""))
                    userPlatforms.append(platform)
                    
                if userPlatforms:    
                    igsUser.platforms.set(userPlatforms)
                    return redirect('/start/mainstreams')
                else:
                    platforms = Platform.objects.all()
                    return render(request, "start/platforms.html", {'platforms': platforms, 'noPlatform': 'noPlatform'}) 
            else:
                platforms = Platform.objects.all()
                return render(request, "start/platforms.html", {'platforms': platforms})
        else:
            return redirect('/start/mainstreams')
    else:
        return redirect('/')
    
def likeDislikeMainstream(request):
    if request.user.is_authenticated and not request.user.is_staff:
        igsUser = IGSUser.objects.get(user=request.user)
        if igsUser.platforms.count() != 0:
            if request.method == "GET":
                if igsUser.likedMainstreamGames.count() == 0:
                    likeDislikeForm = LikeMainstreanmsForm()
                    return render(request, "start/mainstreams.html", {'form': likeDislikeForm})
                else:
                    return redirect('/games/recommend')
            
            if request.method == "POST":
                likeDislikeForm = LikeMainstreanmsForm(data=request.POST)
                if likeDislikeForm.is_valid():
                    ids = request.POST.getlist('games')
                    for id in ids:
                        igsUser.likedMainstreamGames.add(id)
                    
                    return redirect('/games/recommend')
                
                return render(request, "start/mainstreams.html", {'form': likeDislikeForm})    
        else:    
            return redirect('/start/platforms')
    else:
        return redirect('/')
    
def recommend(request):
    if request.user.is_authenticated and not request.user.is_staff:
        igsUser = IGSUser.objects.get(user=request.user)
        if igsUser.platforms.count() == 0:
            return redirect('/start/platforms')
        elif igsUser.likedMainstreamGames.count() == 0:
            return redirect('/start/mainstreams')
        else:
            if request.method == "GET":
                loadSimilarities()
                result = recommendGames(request.user)
                games = []
                for r in result:
                    games.append(IndieGame.objects.get(id=r[0]))
                games.sort(key=lambda x: x.title)       
                igsUser.recommendedGames.set(games)
                return render(request, "users/recommended.html", {"games": games})
            
            return redirect('/')
    else:
        return redirect('/')
    
def recommendations(request):
    if request.user.is_authenticated and not request.user.is_staff:
        igsUser = IGSUser.objects.get(user=request.user)
        if igsUser.platforms.count() == 0:
            return redirect('/start/platforms')
        elif igsUser.likedMainstreamGames.count() == 0:
            return redirect('/start/mainstreams')
        else:
            if request.method == "GET": 
                games = igsUser.recommendedGames.all()
                return render(request, "users/recommended.html", {"games": games})
            
            return redirect('/')
    else:
        return redirect('/')
            
#ADMIN ACTIONS
def reloadDB(request):
    if request.user.is_staff:
        if request.method == "GET":
            form = LoadDjangoDBForm()
            return render(request, "admin/loadDB.html", {"form":form})
        
        if request.method == "POST":
            form = LoadDjangoDBForm(data=request.POST)
            if form.is_valid():
                deleteDjangoDB()
                
                pages = form.cleaned_data['pages']
                gamesPerGenre = form.cleaned_data['gamesPerGenre']
                
                loadDjangoDB(pages,gamesPerGenre)
                
                authorsNumber = Author.objects.all().count()
                genresNumber = Genre.objects.all().count()
                platformsNumber = Platform.objects.all().count()
                tagsNumber = Tag.objects.all().count()
                igames = IndieGame.objects.all().count()
                mgames = MainstreamGame.objects.all().count()
                
                complete = False
                completeLoad = form.cleaned_data['completeLoad']
                if completeLoad:
                    loadWhooshDB()
                    loadSimilarities()
                    complete = True
                    
                return render(request, "admin/loadDBSuccess.html", {"authorsNumber":authorsNumber,"genresNumber":genresNumber, "platformsNumber":platformsNumber,
                                                          "tagsNumber":tagsNumber, "igames":igames, "mgames":mgames, "complete":complete})
                
            return render(request, "admin/loadDB.html", {"form":form})
    else:
        return redirect('/')

def extendDB(request):
    if request.user.is_staff:
        if request.method == "GET":
            form = LoadDjangoDBForm()
            return render(request, "admin/loadDB.html", {"form":form})
        
        if request.method == "POST":
            form = LoadDjangoDBForm(data=request.POST)
            if form.is_valid():
                pages = form.cleaned_data['pages']
                gamesPerGenre = form.cleaned_data['gamesPerGenre']
                
                authorsNumber = Author.objects.all().count()
                genresNumber = Genre.objects.all().count()
                platformsNumber = Platform.objects.all().count()
                tagsNumber = Tag.objects.all().count()
                igames = IndieGame.objects.all().count()
                mgames = MainstreamGame.objects.all().count()
                
                loadDjangoDB(pages,gamesPerGenre)
                
                authorsNumber = Author.objects.all().count() - authorsNumber
                genresNumber = Genre.objects.all().count() - genresNumber
                platformsNumber = Platform.objects.all().count() - platformsNumber
                tagsNumber = Tag.objects.all().count() - tagsNumber
                igames = IndieGame.objects.all().count() - igames
                mgames = MainstreamGame.objects.all().count() - mgames
                
                complete = False
                completeLoad = form.cleaned_data['completeLoad']
                if completeLoad:
                    loadWhooshDB()
                    loadSimilarities()
                    complete = True
                
                return render(request, "admin/loadDBSuccess.html", {"authorsNumber":authorsNumber,"genresNumber":genresNumber, "platformsNumber":platformsNumber,
                                                          "tagsNumber":tagsNumber, "igames":igames, "mgames":mgames, "complete":complete})
                
            return render(request, "admin/loadDB.html", {"form":form})
    else:
        return redirect('/')
    

def loadWH(request):
    if request.user.is_staff:
        if request.method == "GET":
            igames = loadWhooshDB()
        return render(request, "admin/loadDBSuccess.html", {"authorsNumber":0,"genresNumber":0,"platformsNumber":0,
                                                      "tagsNumber":0,"igames":igames,"mgames":0})
    else:
        return redirect('/')
    
def loadRS(request):
    if request.user.is_staff:
        if request.method == "GET":
            loadSimilarities()
        return render(request, "admin/loadDBSuccess.html", {"authorsNumber":0,"genresNumber":0,"platformsNumber":0,
                                                      "tagsNumber":0,"igames":0,"mgames":0, "rsLoaded":"rsLoaded"})
    else:
        return redirect('/')
    