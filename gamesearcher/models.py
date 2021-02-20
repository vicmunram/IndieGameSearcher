from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Author(models.Model):
    name = models.CharField(max_length=50)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Genre(models.Model):
    name = models.CharField(max_length=50)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
class Platform(models.Model):
    name = models.CharField(max_length=50)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
class Status(models.TextChoices):
    RELEASED = 'Released'
    PROTOTYPE = 'Prototype'
    ONHOLD = 'On hold'
    INDEV = 'In development'
    CANCELED = 'Canceled'
    
class Tag(models.Model):
    name = models.CharField(max_length=50)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class GameCommonInfo(models.Model):
    title = models.CharField(max_length=50, unique=True)
    imageURL = models.URLField(max_length=120)
    platforms = models.ManyToManyField(Platform, blank=True)
    genres = models.ManyToManyField(Genre, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    
    class Meta:
        abstract = True
        ordering = ['title']

class MainstreamGame(GameCommonInfo):  
    def __str__(self):
        return self.title

class IndieGame(GameCommonInfo):
    description = models.TextField(default="No description")
    authors = models.ManyToManyField(Author)
    status = models.CharField(choices=Status.choices,max_length=14)
    lastVersionDate = models.DateField()
    downloadURL = models.URLField(max_length=120)
    
    def __str__(self):
        return self.title
    
class IGSUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    platforms = models.ManyToManyField(Platform, blank=True)
    likedMainstreamGames = models.ManyToManyField(MainstreamGame, blank=True)
    recommendedGames = models.ManyToManyField(IndieGame, blank=True, related_name='recommendedGames')
    likedIndieGames = models.ManyToManyField(IndieGame, blank=True)
    dislikedIndieGames = models.ManyToManyField(IndieGame, blank=True, related_name='dislikedIndieGames')
    
    def __str__(self):
        return self.user.username