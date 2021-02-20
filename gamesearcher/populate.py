#encoding:utf-8
from bs4 import BeautifulSoup
import urllib.request
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
from .models import Author, Genre, Platform, Tag, MainstreamGame, IndieGame
from datetime import datetime
import re, os, shutil

def deleteDjangoDB():
    Author.objects.all().delete()
    Genre.objects.all().delete()
    Platform.objects.all().delete()
    Tag.objects.all().delete()
    MainstreamGame.objects.all().delete()
    IndieGame.objects.all().delete()


def loadDjangoDB(pages=12,gamesPerGenre=7):
    
    def extractItchioGenres():
        
        f = urllib.request.urlopen("https://itch.io/games")
        s = BeautifulSoup(f,"html.parser")
        genres = s.select("div.browse_filter_group_widget:nth-child(4) > ul:nth-child(2)")[0].find_all(href=re.compile("/games/genre|/games/tag"))
        
        for g in genres:
            Genre.objects.get_or_create(name=g.text)
    
    def extractIndieGames(pages):
        
        itchioURL = "https://itch.io/games/new-and-popular"
        page = ""
        
        for i in range(0,pages):
            if(i != 0):
                page = "?page=" + str(i+1)
        
            f = urllib.request.urlopen(itchioURL+page)
            s = BeautifulSoup(f,"html.parser")
            games = s.find_all("div", attrs={"class":"game_cell"})
    
            for g in games:
                gameTitleLink = g.find("a", attrs={"class":"title game_link"})
                gameImage = g.find("div", attrs={"class":"game_thumb"})
                
                #Comprobamos si el videojuego ya se encuentra en la BBDD
                numResults = IndieGame.objects.filter(title=gameTitleLink.string).count()
                if numResults == 0:
                    description = g.find("div", attrs={"class":"game_text"})
        
                    game = extractDetails(gameTitleLink['href'],description)
                    
                    if game is not None:
                        game.title = gameTitleLink.string
                        game.downloadURL = gameTitleLink['href']
                        if gameImage.has_attr('data-background_image'):
                            game.imageURL = gameImage['data-background_image']
                        
                        game.save()
                    
    def extractDetails(url,description):
            f = urllib.request.urlopen(url)
            s = BeautifulSoup(f,"html.parser")
            
            #Comprobamos si es accesible, es decir, no necesitamos una cuenta de itch.io
            isAccesible= s.find("div", attrs={"class":"more_information_toggle"})
            
            if isAccesible:
                
                #Instanciamos el videojuego
                game = IndieGame()
                
                if description is None:
                    desc = s.find("div", attrs={"class":"formatted_description user_formatted"})
                    if desc:
                        desc2 = s.find("div", attrs={"class":"formatted_description user_formatted"}).find("p")
                        if desc2:  
                            description = s.find("div", attrs={"class":"formatted_description user_formatted"}).find("p").text
                            if description:
                                game.description = description 
                else:
                    game.description = description.text
                
                status = s.find("td", string="Status").find_next("td").find("a").text
                game.status = status
                
                lastVersionDate = datetime.strptime(s.find("td", string=re.compile("(Published|Updated)")).find_next("td").find("abbr")['title'][0:-8],"%d %B %Y")
                game.lastVersionDate = lastVersionDate
                
                game.save()
                
                #M2M Relationships
                authors = []
                authorsTd = s.find("td", string="Author")
                if not authorsTd:
                    authorsTd = s.find("td", string="Authors")
                authorsLinks = authorsTd.find_next("td").find_all("a")
                for l in authorsLinks:
                    author, created = Author.objects.get_or_create(name=l.text)
                    authors.append(author.id)
                    
                game.authors.set(authors)   
                
                genres = []
                genresTd = s.find("td", string="Genre")
                if genresTd:
                    genresLinks = genresTd.find_next("td").find_all("a")
                    for l in genresLinks:
                        genre, created = Genre.objects.get_or_create(name=l.text)
                        genres.append(genre.id)
                    
                    game.genres.set(genres)
                
                platforms = []
                platformsTd = s.find("td", string="Platforms")
                if platformsTd:
                    platformLinks = platformsTd.find_next("td").find_all("a")
                    for l in platformLinks:
                        platform, created = Platform.objects.get_or_create(name=l.text)
                        platforms.append(platform.id)
                    
                    game.platforms.set(platforms)
                    
                    
                tags = []
                tagsTd = s.find("td", string="Tags")
                if tagsTd:
                    tagsLinks = tagsTd.find_next("td").find_all("a")
                    for l in tagsLinks:
                        tag, created = Tag.objects.get_or_create(name=l.text.lower())
                        tags.append(tag.id) 
                
                    game.tags.set(tags)
                    
                return game
                
            else:
                return None
            
    def extractMainstreamGames(gamesPerGenre):
        if gamesPerGenre > 0:
            mainGenres = Genre.objects.all()
            
            for g in mainGenres:
                genreName = g.name
                if genreName != "Other":
                    if genreName == "Role Playing": genreName = "RPG"
                    f = urllib.request.urlopen("https://store.steampowered.com/tags/en/" + genreName.replace(" ","") + "/")
                    s = BeautifulSoup(f,"html.parser")
                    
                    games = s.find("div", attrs={"id":"TopSellersRows"}).find_all("a", attrs={"class":"tab_item"}, limit=gamesPerGenre)
                    
                    for g in games:
                        
                        title = g.find("div", attrs={"class":"tab_item_name"}).text
                        
                        #Comprobamos si el videojuego ya se encuentra en la BBDD
                        numResults = MainstreamGame.objects.filter(title=title).count() + IndieGame.objects.filter(title=title).count()
                        if numResults == 0:
                            
                            game = MainstreamGame()
                            game.title = title
                        
                            imageURL = g.find("img")['src'].replace("capsule_184x69","header")
                            game.imageURL = imageURL
                            
                            f = urllib.request.urlopen(g['href'])
                            s = BeautifulSoup(f,"html.parser")
                            
                            platforms = []
                            
                            win = g.find("span", attrs={"class":"platform_img win"})
                            if win: platforms.append(Platform.objects.get_or_create(name="Windows"))
                            
                            mac = g.find("span", attrs={"class":"platform_img mac"})
                            if mac: platforms.append(Platform.objects.get_or_create(name="macOS"))
                            
                            linux = g.find("span", attrs={"class":"platform_img linux"})
                            if linux: platforms.append(Platform.objects.get_or_create(name="Linux"))
                            
                            genres = []
                            tags = []
                            
                            allTags = s.find_all("a", attrs={"class":"app_tag"})
                            for t in allTags:
                                tag = t.text.strip()
                                numResults = Genre.objects.filter(name=tag).count()
                                if numResults == 1:
                                    genre = Genre.objects.get(name=t.text.strip())
                                    genres.append(genre)
                                else:
                                    tag, created = Tag.objects.get_or_create(name=tag.lower())
                                    tags.append(tag.id) 
                                        
                            game.save()
                            
                            game.platforms.set(platforms)
                            game.genres.set(genres)
                            game.tags.set(tags)
         
    extractItchioGenres()
    extractIndieGames(pages)
    extractMainstreamGames(gamesPerGenre)

def loadWhooshDB():
    schema = Schema(idIndieGame=ID(stored=True, unique=True), title=TEXT(), description=TEXT(), authors=TEXT(),
                     tags=TEXT())
    
    if os.path.exists("igs_index"):
        shutil.rmtree("igs_index")

    os.mkdir("igs_index")
    
    ix = create_in("igs_index", schema=schema)
    writer = ix.writer()
    
    games = IndieGame.objects.all()
    
    i = 0
    for game in games:
        tagsText = ""
        first = True
        for t in game.tags.all():
            if first:
                tagsText = t.name
                first = False
            else:
                tagsText = tagsText + ", " + t.name
                
        authorsText = ""
        first = True
        for a in game.authors.all():
            if first:
                authorsText = a.name
                first = False
            else:
                authorsText = authorsText + ", " + a.name
        
        writer.add_document(
            idIndieGame=str(game.id),
            title=game.title,
            description=game.description,
            authors=authorsText,
            tags=tagsText,
        )
        i = i + 1
    writer.commit()
    
    return i