from django.db import models
from django.utils import timezone
    
class Movie(models.Model):
    name = models.CharField(max_length=200)
    url_name = models.CharField(max_length=200)
    release_year = models.PositiveIntegerField()
    runtime = models.PositiveIntegerField()
    runtime_str = models.CharField(max_length=200)
    box_office = models.IntegerField()
    box_office_str = models.CharField(max_length=200)
    genres = models.CharField(max_length=200)
    actors = models.CharField(max_length=200)
    directors = models.CharField(max_length=200)
    writers = models.CharField(max_length=200)
    imdb_rating = models.FloatField()
    num_imdb_ratings = models.IntegerField()
    num_imdb_ratings_str = models.CharField(max_length=200)
    imdb_popularity = models.PositiveIntegerField()
    imdb_popularity_str = models.CharField(max_length=200)
    tomatoes_critic_rating = models.IntegerField()
    tomatoes_user_rating = models.IntegerField()
    metacritic_rating = models.PositiveIntegerField()
    oscar_wins = models.IntegerField()
    oscar_noms = models.IntegerField()
    url = models.CharField(max_length=300)
    poster = models.CharField(max_length=300)
    recommended_value = models.FloatField()
    
    excluded_movies = set()
    rated_movies = set()
    
    sort_selected = 7
    
    min_imdb_rating_filter = 0
    min_runtime_filter = 0
    max_runtime_filter = 0
    min_release_year_filter = 0
    max_release_year_filter = 0
    min_box_office_filter = 0
    max_box_office_filter = 0
    
    filter_selected = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    Q_arr = list()

    def publish(self):
        self.save()
        
    def __str__(self):
        return self.name