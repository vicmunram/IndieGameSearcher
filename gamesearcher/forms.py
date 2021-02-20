#encoding:utf-8
from django import forms
from django.forms import ModelForm
from .models import IndieGame
from gamesearcher.models import MainstreamGame
from django.core.exceptions import ValidationError
        
class LoadDjangoDBForm(forms.Form):
    pages = forms.IntegerField(min_value=0, label='Pages to scrap for Indie Games')
    gamesPerGenre = forms.IntegerField(min_value=0, label='MainStream games to scrap per genre')
    completeLoad = forms.BooleanField(required=False, label='Load all systems')
    
class FilterForm(ModelForm):
    firstDate = forms.DateField(required=False, label="Last version from", input_formats=['%d-%m-%Y'])
    lastDate = forms.DateField(required=False, label="To", input_formats=['%d-%m-%Y'])
    
    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.fields['status'].required = False
        self.fields['firstDate'].widget.attrs['placeholder'] = 'dd-mm-yyyy'
        self.fields['lastDate'].widget.attrs['placeholder'] = 'dd-mm-yyyy'
    
    class Meta:
        model = IndieGame
        fields = '__all__'
        exclude = ['title', 'imageURL', 'description', 'tags', 'authors', 'downloadURL', 'lastVersionDate']
        
class SearchForm(forms.Form):
    text = forms.CharField(label="", required=False)
    title = forms.BooleanField(required=False, initial=True)
    description = forms.BooleanField(required=False, initial=True)
    tags = forms.BooleanField(required=False, initial=True)
    author = forms.BooleanField(required=False, initial=True)
    
class LikeMainstreanmsForm(forms.Form):
    def clean_games(self):
        games = self.cleaned_data.get('games')
        if len(games) < 8:
            raise ValidationError("You have to choose at least 8 videogames")
        return games
    
    games = forms.ModelMultipleChoiceField(
        queryset = MainstreamGame.objects.all(),
        widget  = forms.CheckboxSelectMultiple,
        label = ""
    )
    
class LikeDislikeForm(forms.Form):
    yesNo = (('yes', 'Yes'),('no', 'No'),)
    likeDislike = forms.ChoiceField(choices=yesNo, label="Did you like the game? ")
    
        

        