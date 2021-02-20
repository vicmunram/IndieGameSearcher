from .models import IGSUser, IndieGame
from collections import Counter
import shelve

def loadSimilarities():
    shelf = shelve.open('dataRS.dat')
    indieGamesKeywords = indieGamesGenresAndTags()
    usersKeywords = usersGenresAndTags()
    shelf['similarities'] = computeSimilarities(indieGamesKeywords, usersKeywords)
    shelf.close()
    
def computeSimilarities(indieGamesKeywords, usersKeywords):
    res = {}
    for u in usersKeywords:
        if usersKeywords[u]:
            topIndieGames = {}
            for i in indieGamesKeywords:
                topIndieGames[i] = diceCoefficient(set(usersKeywords[u]), set(indieGamesKeywords[i]))
            res[u] = Counter(topIndieGames).most_common(75)
    return res    

def recommendGames(user):
    igsUser = IGSUser.objects.get(user=user)
    shelf = shelve.open("dataRS.dat")
    res = []
    i = 0
    for gameId, score in shelf['similarities'][user]:
        game = IndieGame.objects.get(id=gameId)
        if not set(game.platforms.all()).isdisjoint(set(igsUser.platforms.all())) and not game in list(igsUser.likedIndieGames.all()) and not game in list(igsUser.dislikedIndieGames.all()) and i<9:
            res.append([gameId, 100 * score])
            i = i + 1
            
        if i == 9: break
               
    shelf.close()
    
    return res

def usersGenresAndTags():
    users = {}
    for u in IGSUser.objects.all():
        user = u.user
        keywords = []
        genres = []
        tags = []
        likedMGames = u.likedMainstreamGames.all()
        if likedMGames:
            for game in likedMGames:
                genres.extend(game.genres.all())
                tags.extend(game.tags.all())
                
        likedIGames = u.likedIndieGames.all()
        if likedIGames:
            for game in likedIGames:
                genres.extend(game.genres.all())
                tags.extend(game.tags.all())
                
        dislikedIGames = u.dislikedIndieGames.all()
        if dislikedIGames:
            for game in dislikedIGames:
                for t in game.tags.all():
                    if t in tags:tags.remove(t)
            
        commonGenres = Counter(genres).most_common(3)
        commonTags = Counter(tags).most_common(8)
        
        for g in commonGenres:
            keywords.append(g[0].id)
        for t in commonTags:
            keywords.append(t[0].id)  
                
        users[user] = keywords
            
    return users

def indieGamesGenresAndTags():
    games = {}
    for game in IndieGame.objects.all():
        id = game.id
        keywords = []

        for g in game.genres.all():
            keywords.append(g.id)
        for t in game.tags.all():
            keywords.append(t.id)
            
        games[id] = keywords
        
    return games
        
def diceCoefficient(set1, set2):
    return 2 * len(set1.intersection(set2)) / (len(set1) + len(set2))