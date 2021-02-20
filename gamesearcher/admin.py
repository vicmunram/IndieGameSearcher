from django.contrib import admin
from .models import Author, Genre, Platform, Tag, MainstreamGame, IndieGame, IGSUser

# Register your models here.
admin.site.register(MainstreamGame)
admin.site.register(IndieGame)
admin.site.register(Author)
admin.site.register(Genre)
admin.site.register(Platform)
admin.site.register(Tag)
admin.site.register(IGSUser)
