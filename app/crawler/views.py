# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.utils import timezone
from .models import Movie
from .crawler import Crawler
from .graph import Graph, Vertex
import json

# renders the home page
def render_home_page(request):
    Movie.excluded_movies = set()
    Movie.rated_movies = set()
    Movie.sort_selected = 7
    Movie.filter_selected = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    Movie.Q_arr = list()
    Movie.min_imdb_rating_filter = 0
    Movie.min_runtime_filter = 0
    Movie.max_runtime_filter = 0
    Movie.min_release_year_filter = 0
    Movie.max_release_year_filter = 0
    Movie.min_box_office_filter = 0
    Movie.max_box_office_filter = 0
    return render(request, 'home_page.html', {})

# renders the movie list page when the 'Start crawler' button is clicked
def render_movie_list(request):
    url_input = request.POST.get('url', '')
    json_input = request.POST.get('json', '')
    Movie.filter_selected = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    Movie.Q_arr = list()
    
    # JSON input case
    if (url_input == '') and (json_input != ''):
        Movie.objects.all().delete()
        json_input = json.loads(json_input)
        movie_data = Crawler(json_input, None)
        vertices = movie_data.g.unseen_movie_vertices
        for i in range(len(vertices)):
            vertex = vertices.pop()
            if (Movie.objects.filter(name=vertex.name).exists() == False) and (Movie.objects.filter(url=vertex.url).exists() == False):
                Movie.objects.create(name=vertex.name, url_name=vertex.name.replace(' ', '_'), release_year=vertex.release_year, runtime=vertex.runtime, runtime_str=vertex.runtime_str, box_office=vertex.box_office, box_office_str=vertex.box_office_str, genres=vertex.genres, actors=vertex.actors, directors=vertex.directors, writers=vertex.writers, imdb_rating=vertex.imdb_rating, num_imdb_ratings=vertex.num_imdb_ratings, num_imdb_ratings_str = vertex.num_imdb_ratings_str, imdb_popularity=vertex.imdb_popularity, imdb_popularity_str=vertex.imdb_popularity_str, tomatoes_critic_rating=vertex.tomatoes_critic_rating, tomatoes_user_rating=vertex.tomatoes_user_rating, metacritic_rating=vertex.metacritic_rating, oscar_wins=vertex.oscar_wins, oscar_noms=vertex.oscar_noms, url=vertex.url, poster=vertex.poster, recommended_value=vertex.recommended_value)
        movies = Movie.objects.order_by('recommended_value').reverse()
        for movie in Movie.rated_movies:
            movies = movies.exclude(name=movie)
        return render(request, 'movie_list.html', {'movies': movies, 'selected': Movie.sort_selected, 'checked': Movie.filter_selected})
    # URL input case
    elif (url_input != '') and (json_input == ''):
        Movie.objects.all().delete()
        movie_data = Crawler(None, url_input)
        vertices = movie_data.g.unseen_movie_vertices
        for i in range(len(vertices)):
            vertex = vertices.pop()
            if (Movie.objects.filter(name=vertex.name).exists() == False) and (Movie.objects.filter(url=vertex.url).exists() == False):
                Movie.objects.create(name=vertex.name, url_name=vertex.name.replace(' ', '_'), release_year=vertex.release_year, runtime=vertex.runtime, runtime_str=vertex.runtime_str, box_office=vertex.box_office, box_office_str=vertex.box_office_str, genres=vertex.genres, actors=vertex.actors, directors=vertex.directors, writers=vertex.writers, imdb_rating=vertex.imdb_rating, num_imdb_ratings=vertex.num_imdb_ratings, num_imdb_ratings_str = vertex.num_imdb_ratings_str, imdb_popularity=vertex.imdb_popularity, imdb_popularity_str=vertex.imdb_popularity_str, tomatoes_critic_rating=vertex.tomatoes_critic_rating, tomatoes_user_rating=vertex.tomatoes_user_rating, metacritic_rating=vertex.metacritic_rating, oscar_wins=vertex.oscar_wins, oscar_noms=vertex.oscar_noms, url=vertex.url, poster=vertex.poster, recommended_value=vertex.recommended_value)
        
        movies = Movie.objects
        for movie in Movie.rated_movies:
            movies = movies.exclude(name=movie)
        if (Movie.sort_selected == 0):
            movies = movies.order_by('imdb_rating').reverse()
        elif (Movie.sort_selected == 1):
            movies = movies.order_by('runtime')
        elif (Movie.sort_selected == 2):
            movies = movies.order_by('runtime').reverse()
        elif (Movie.sort_selected == 3):
            movies = movies.order_by('release_year')
        elif (Movie.sort_selected == 4):
            movies = movies.order_by('release_year').reverse()
        elif (Movie.sort_selected == 5):
            movies = movies.order_by('box_office')
        elif (Movie.sort_selected == 6):
            movies = movies.order_by('box_office').reverse()
        elif (Movie.sort_selected == 7):
            movies = movies.order_by('recommended_value').reverse()
        return render(request, 'movie_list.html', {'movies': movies, 'selected': Movie.sort_selected, 'checked': Movie.filter_selected})
    else:
        movies = Movie.objects
        for movie in Movie.rated_movies:
            movies = movies.exclude(name=movie)
        if (Movie.sort_selected == 0):
            movies = movies.order_by('imdb_rating').reverse()
        elif (Movie.sort_selected == 1):
            movies = movies.order_by('runtime')
        elif (Movie.sort_selected == 2):
            movies = movies.order_by('runtime').reverse()
        elif (Movie.sort_selected == 3):
            movies = movies.order_by('release_year')
        elif (Movie.sort_selected == 4):
            movies = movies.order_by('release_year').reverse()
        elif (Movie.sort_selected == 5):
            movies = movies.order_by('box_office')
        elif (Movie.sort_selected == 6):
            movies = movies.order_by('box_office').reverse()
        elif (Movie.sort_selected == 7):
            movies = movies.order_by('recommended_value').reverse()
        return render(request, 'movie_list.html', {'movies': movies, 'selected': Movie.sort_selected, 'checked': Movie.filter_selected})

# renders when the 'Clear all' button is clicked, clears all loaded movies
def clear_all_movies(request):
    Movie.objects.all().delete()
    Movie.excluded_movies = set()
    Movie.sort_selected = 7
    Movie.filter_selected = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    Movie.Q_arr = list()
    Movie.min_imdb_rating_filter = 0
    Movie.min_runtime_filter = 0
    Movie.max_runtime_filter = 0
    Movie.min_release_year_filter = 0
    Movie.max_release_year_filter = 0
    Movie.min_box_office_filter = 0
    Movie.max_box_office_filter = 0
    return render(request, 'movie_list.html', {'movies': []})

# renders when a movie's 'subtract' button is clicked, clears that specific movie
def clear_movie(request):
    movie_name = request.POST.get('movie_name', '')
    movie_name = movie_name.replace('_', ' ')
    
    Movie.excluded_movies.add(movie_name)
    movies = Movie.objects
    if (Movie.sort_selected == 0):
        movies = movies.order_by('imdb_rating').reverse()
    elif (Movie.sort_selected == 1):
        movies = movies.order_by('runtime')
    elif (Movie.sort_selected == 2):
        movies = movies.order_by('runtime').reverse()
    elif (Movie.sort_selected == 3):
        movies = movies.order_by('release_year')
    elif (Movie.sort_selected == 4):
        movies = movies.order_by('release_year').reverse()
    elif (Movie.sort_selected == 5):
        movies = movies.order_by('box_office')
    elif (Movie.sort_selected == 6):
        movies = movies.order_by('box_office').reverse()
    elif (Movie.sort_selected == 7):
        movies = movies.order_by('recommended_value').reverse()
    
    for movie in Movie.excluded_movies:
        movies = movies.exclude(name=movie)
    for movie in Movie.rated_movies:
        movies = movies.exclude(name=movie)
        
    if (Movie.min_imdb_rating_filter != 0):
        movies = movies.filter(imdb_rating__gte=Movie.min_imdb_rating_filter)
    if (Movie.min_runtime_filter != 0):
        movies = movies.filter(runtime__gte=Movie.min_runtime_filter)
    if (Movie.max_runtime_filter != 0):
        movies = movies.filter(runtime__lte=Movie.max_runtime_filter)
    if (Movie.min_release_year_filter != 0):
        movies = movies.filter(release_year__gte=Movie.min_release_year_filter)
    if (Movie.max_release_year_filter != 0):
        movies = movies.filter(release_year__lte=Movie.max_release_year_filter)
    if (Movie.min_box_office_filter != 0):
        movies = movies.filter(box_office__gte=Movie.min_box_office_filter)
    if (Movie.max_box_office_filter != 0):
        movies = movies.filter(box_office__lte=Movie.max_box_office_filter)
    
    return render(request, 'movie_list.html', {'movies': movies, 'selected': Movie.sort_selected, 'checked': Movie.filter_selected})

# renders when a movie's 'Rate' button is clicked, clears that specific movie, and rates in on the user's IMDb page
def rate_movie(request):
    movie_name = request.POST.get('rated_movie', '')
    movie_name = movie_name.replace('_', ' ')
    Movie.rated_movies.add(movie_name)
    
    rated_value = request.POST.get('rated_value', '')
    
    movies = Movie.objects
    if (Movie.sort_selected == 0):
        movies = movies.order_by('imdb_rating').reverse()
    elif (Movie.sort_selected == 1):
        movies = movies.order_by('runtime')
    elif (Movie.sort_selected == 2):
        movies = movies.order_by('runtime').reverse()
    elif (Movie.sort_selected == 3):
        movies = movies.order_by('release_year')
    elif (Movie.sort_selected == 4):
        movies = movies.order_by('release_year').reverse()
    elif (Movie.sort_selected == 5):
        movies = movies.order_by('box_office')
    elif (Movie.sort_selected == 6):
        movies = movies.order_by('box_office').reverse()
    elif (Movie.sort_selected == 7):
        movies = movies.order_by('recommended_value').reverse()
    
    for movie in Movie.excluded_movies:
        movies = movies.exclude(name=movie)
    for movie in Movie.rated_movies:
        movies = movies.exclude(name=movie)
        
    if (Movie.min_imdb_rating_filter != 0):
        movies = movies.filter(imdb_rating__gte=Movie.min_imdb_rating_filter)
    if (Movie.min_runtime_filter != 0):
        movies = movies.filter(runtime__gte=Movie.min_runtime_filter)
    if (Movie.max_runtime_filter != 0):
        movies = movies.filter(runtime__lte=Movie.max_runtime_filter)
    if (Movie.min_release_year_filter != 0):
        movies = movies.filter(release_year__gte=Movie.min_release_year_filter)
    if (Movie.max_release_year_filter != 0):
        movies = movies.filter(release_year__lte=Movie.max_release_year_filter)
    if (Movie.min_box_office_filter != 0):
        movies = movies.filter(box_office__gte=Movie.min_box_office_filter)
    if (Movie.max_box_office_filter != 0):
        movies = movies.filter(box_office__lte=Movie.max_box_office_filter)
    
    return render(request, 'movie_list.html', {'movies': movies, 'selected': Movie.sort_selected, 'checked': Movie.filter_selected})

# re-renders the movie list page when the 'Sort by:' field is changed to order the list by the requested variable
def sort_by(request):
    sort_var = request.GET['sort_var']
    movies = Movie.objects
    if (sort_var == 'imdb_rating'):
        movies = Movie.objects.order_by('imdb_rating').reverse()
        Movie.sort_selected = 0
    elif (sort_var == 'runtime_low_to_high'):
        movies = Movie.objects.order_by('runtime')
        Movie.sort_selected = 1
    elif (sort_var == 'runtime_high_to_low'):
        movies = Movie.objects.order_by('runtime').reverse()
        Movie.sort_selected = 2
    elif (sort_var == 'release_year_old_to_new'):
        movies = Movie.objects.order_by('release_year')
        Movie.sort_selected = 3
    elif (sort_var == 'release_year_new_to_old'):
        movies = Movie.objects.order_by('release_year').reverse()
        Movie.sort_selected = 4
    elif (sort_var == 'box_office_low_to_high'):
        movies = Movie.objects.order_by('box_office')
        Movie.sort_selected = 5
    elif (sort_var == 'box_office_high_to_low'):
        movies = Movie.objects.order_by('box_office').reverse()
        Movie.sort_selected = 6
    elif (sort_var == 'recommended_value'):
        movies = movies.order_by('recommended_value').reverse()
        Movie.sort_selected = 7
        
    for movie in Movie.excluded_movies:
        movies = movies.exclude(name=movie)
    for movie in Movie.rated_movies:
        movies = movies.exclude(name=movie)
        
    if (Movie.min_imdb_rating_filter != 0):
        movies = movies.filter(imdb_rating__gte=Movie.min_imdb_rating_filter)
    if (Movie.min_runtime_filter != 0):
        movies = movies.filter(runtime__gte=Movie.min_runtime_filter)
    if (Movie.max_runtime_filter != 0):
        movies = movies.filter(runtime__lte=Movie.max_runtime_filter)
    if (Movie.min_release_year_filter != 0):
        movies = movies.filter(release_year__gte=Movie.min_release_year_filter)
    if (Movie.max_release_year_filter != 0):
        movies = movies.filter(release_year__lte=Movie.max_release_year_filter)
    if (Movie.min_box_office_filter != 0):
        movies = movies.filter(box_office__gte=Movie.min_box_office_filter)
    if (Movie.max_box_office_filter != 0):
        movies = movies.filter(box_office__lte=Movie.max_box_office_filter)
        
    return render(request, 'movie_list.html', {'movies': movies, 'selected': Movie.sort_selected, 'checked': Movie.filter_selected})

# re-renders the movie list page when the submit button from the 'Filter by:' field is clicked to filter the movie list
def filter_by(request):
    movies = Movie.objects
    if (Movie.sort_selected == 0):
        movies = movies.order_by('imdb_rating').reverse()
    elif (Movie.sort_selected == 1):
        movies = movies.order_by('runtime')
    elif (Movie.sort_selected == 2):
        movies = movies.order_by('runtime').reverse()
    elif (Movie.sort_selected == 3):
        movies = movies.order_by('release_year')
    elif (Movie.sort_selected == 4):
        movies = movies.order_by('release_year').reverse()
    elif (Movie.sort_selected == 5):
        movies = movies.order_by('box_office')
    elif (Movie.sort_selected == 6):
        movies = movies.order_by('box_office').reverse()
    elif (Movie.sort_selected == 7):
        movies = movies.order_by('recommended_value').reverse()
        
    min_imdb_rating = request.POST.get('min_imdb_rating', '')
    min_runtime = request.POST.get('min_runtime', '')
    max_runtime = request.POST.get('max_runtime', '')
    min_release_year = request.POST.get('min_release_year', '')
    max_release_year = request.POST.get('max_release_year', '')
    min_box_office = request.POST.get('min_box_office', '')
    max_box_office = request.POST.get('max_box_office', '')
    
    if (Movie.min_imdb_rating_filter != 0):
        movies = movies.filter(imdb_rating__gte=Movie.min_imdb_rating_filter)
    if (Movie.min_runtime_filter != 0):
        movies = movies.filter(runtime__gte=Movie.min_runtime_filter)
    if (Movie.max_runtime_filter != 0):
        movies = movies.filter(runtime__lte=Movie.max_runtime_filter)
    if (Movie.min_release_year_filter != 0):
        movies = movies.filter(release_year__gte=Movie.min_release_year_filter)
    if (Movie.max_release_year_filter != 0):
        movies = movies.filter(release_year__lte=Movie.max_release_year_filter)
    if (Movie.min_box_office_filter != 0):
        movies = movies.filter(box_office__gte=Movie.min_box_office_filter)
    if (Movie.max_box_office_filter != 0):
        movies = movies.filter(box_office__lte=Movie.max_box_office_filter)

    if (min_imdb_rating != ''):
        movies = movies.filter(imdb_rating__gte=min_imdb_rating)
        Movie.min_imdb_rating_filter = min_imdb_rating
    if (min_runtime != ''):
        movies = movies.filter(runtime__gte=min_runtime)
        Movie.min_runtime_filter = min_runtime
    if (max_runtime != ''):
        movies = movies.filter(runtime__lte=max_runtime) 
        Movie.max_runtime_filter = max_runtime
    if (min_release_year != ''):
        movies = movies.filter(release_year__gte=min_release_year)
        Movie.min_release_year_filter = min_release_year
    if (max_release_year != ''):
        movies = movies.filter(release_year__lte=max_release_year) 
        Movie.max_release_year_filter = max_release_year
    if (min_box_office != ''):
        movies = movies.filter(box_office__gte=min_box_office)
        Movie.min_box_office_filter = min_box_office
    if (max_box_office != ''):
        movies = movies.filter(box_office__lte=max_box_office) 
        Movie.max_box_office_filter = max_box_office
        
    action = request.POST.get('action')
    adventure = request.POST.get('adventure')
    animation = request.POST.get('animation')
    biography = request.POST.get('biography')
    comedy = request.POST.get('comedy')
    crime = request.POST.get('crime')
    documentary = request.POST.get('documentary')
    drama = request.POST.get('drama')
    fantasy = request.POST.get('fantasy')
    history = request.POST.get('history')
    horror = request.POST.get('horror')
    musical = request.POST.get('musical')
    mystery = request.POST.get('mystery')
    romance = request.POST.get('romance')
    sci_fi = request.POST.get('sci_fi')
    sport = request.POST.get('sport')
    thriller = request.POST.get('thriller')
    war = request.POST.get('war')
    western = request.POST.get('western')
    
    if (action == 'on'):
        Movie.filter_selected[0] = 1
        Movie.Q_arr.append(Q(genres__contains='Action'))
    if (adventure == 'on'):
        Movie.filter_selected[1] = 1
        Movie.Q_arr.append(Q(genres__contains='Adventure'))
    if (animation == 'on'):
        Movie.filter_selected[2] = 1
        Movie.Q_arr.append(Q(genres__contains='Animation'))
    if (biography == 'on'):
        Movie.filter_selected[3] = 1
        Movie.Q_arr.append(Q(genres__contains='Biography'))
    if (comedy == 'on'):
        Movie.filter_selected[4] = 1
        Movie.Q_arr.append(Q(genres__contains='Comedy'))
    if (crime == 'on'):
        Movie.filter_selected[5] = 1
        Movie.Q_arr.append(Q(genres__contains='Crime'))
    if (documentary == 'on'):
        Movie.filter_selected[6] = 1
        Movie.Q_arr.append(Q(genres__contains='Documentary'))
    if (drama == 'on'):
        Movie.filter_selected[7] = 1
        Movie.Q_arr.append(Q(genres__contains='Drama'))
    if (fantasy == 'on'):
        Movie.filter_selected[8] = 1
        Movie.Q_arr.append(Q(genres__contains='Fantasy'))
    if (history == 'on'):
        Movie.filter_selected[9] = 1
        Movie.Q_arr.append(Q(genres__contains='History'))
    if (horror == 'on'):
        Movie.filter_selected[10] = 1
        Movie.Q_arr.append(Q(genres__contains='Horror'))
    if (musical == 'on'):
        Movie.filter_selected[11] = 1
        Movie.Q_arr.append(Q(genres__contains='Musical'))
    if (mystery == 'on'):
        Movie.filter_selected[12] = 1
        Movie.Q_arr.append(Q(genres__contains='Mystery'))
    if (romance == 'on'):
        Movie.filter_selected[13] = 1
        Movie.Q_arr.append(Q(genres__contains='Romance'))
    if (sci_fi == 'on'):
        Movie.filter_selected[14] = 1
        Movie.Q_arr.append(Q(genres__contains='Sci-Fi'))
    if (sport == 'on'):
        Movie.filter_selected[15] = 1
        Movie.Q_arr.append(Q(genres__contains='Sport'))
    if (thriller == 'on'):
        Movie.filter_selected[16] = 1
        Movie.Q_arr.append(Q(genres__contains='Thriller'))
    if (war == 'on'):
        Movie.filter_selected[17] = 1
        Movie.Q_arr.append(Q(genres__contains='War'))
    if (western == 'on'):
        Movie.filter_selected[18] = 1
        Movie.Q_arr.append(Q(genres__contains='Western'))
    
    if (len(Movie.Q_arr) == 1):
        movies = movies.filter(Movie.Q_arr[0])
    elif (len(Movie.Q_arr) == 2):
        movies = movies.filter(Movie.Q_arr[0] | Movie.Q_arr[1])
    elif (len(Movie.Q_arr) == 3):
        movies = movies.filter(Movie.Q_arr[0] | Movie.Q_arr[1] | Movie.Q_arr[2])
    elif (len(Movie.Q_arr) == 4):
        movies = movies.filter(Movie.Q_arr[0] | Movie.Q_arr[1] | Movie.Q_arr[2] | Movie.Q_arr[3])
    elif (len(Movie.Q_arr) == 5):
        movies = movies.filter(Movie.Q_arr[0] | Movie.Q_arr[1] | Movie.Q_arr[2] | Movie.Q_arr[3] | Movie.Q_arr[4])
    elif (len(Movie.Q_arr) == 6):
        movies = movies.filter(Movie.Q_arr[0] | Movie.Q_arr[1] | Movie.Q_arr[2] | Movie.Q_arr[3] | Movie.Q_arr[4] | Movie.Q_arr[5])
    elif (len(Movie.Q_arr) == 7):
        movies = movies.filter(Movie.Q_arr[0] | Movie.Q_arr[1] | Movie.Q_arr[2] | Movie.Q_arr[3] | Movie.Q_arr[4] | Movie.Q_arr[5] | Movie.Q_arr[6])
    elif (len(Movie.Q_arr) == 8):
        movies = movies.filter(Movie.Q_arr[0] | Movie.Q_arr[1] | Movie.Q_arr[2] | Movie.Q_arr[3] | Movie.Q_arr[4] | Movie.Q_arr[5] | Movie.Q_arr[6] | Movie.Q_arr[7])
    elif (len(Movie.Q_arr) == 9):
        movies = movies.filter(Movie.Q_arr[0] | Movie.Q_arr[1] | Movie.Q_arr[2] | Movie.Q_arr[3] | Movie.Q_arr[4] | Movie.Q_arr[5] | Movie.Q_arr[6] | Movie.Q_arr[7] | Movie.Q_arr[8])
    elif (len(Movie.Q_arr) == 10):
        movies = movies.filter(Movie.Q_arr[0] | Movie.Q_arr[1] | Movie.Q_arr[2] | Movie.Q_arr[3] | Movie.Q_arr[4] | Movie.Q_arr[5] | Movie.Q_arr[6] | Movie.Q_arr[7] | Movie.Q_arr[8] | Movie.Q_arr[9])
    elif (len(Movie.Q_arr) == 11):
        movies = movies.filter(Movie.Q_arr[0] | Movie.Q_arr[1] | Movie.Q_arr[2] | Movie.Q_arr[3] | Movie.Q_arr[4] | Movie.Q_arr[5] | Movie.Q_arr[6] | Movie.Q_arr[7] | Movie.Q_arr[8] | Movie.Q_arr[9] | Movie.Q_arr[10])
    elif (len(Movie.Q_arr) == 12):
        movies = movies.filter(Movie.Q_arr[0] | Movie.Q_arr[1] | Movie.Q_arr[2] | Movie.Q_arr[3] | Movie.Q_arr[4] | Movie.Q_arr[5] | Movie.Q_arr[6] | Movie.Q_arr[7] | Movie.Q_arr[8] | Movie.Q_arr[9] | Movie.Q_arr[10] | Movie.Q_arr[11])
    elif (len(Movie.Q_arr) == 13):
        movies = movies.filter(Movie.Q_arr[0] | Movie.Q_arr[1] | Movie.Q_arr[2] | Movie.Q_arr[3] | Movie.Q_arr[4] | Movie.Q_arr[5] | Movie.Q_arr[6] | Movie.Q_arr[7] | Movie.Q_arr[8] | Movie.Q_arr[9] | Movie.Q_arr[10] | Movie.Q_arr[11] | Movie.Q_arr[12])
    elif (len(Movie.Q_arr) == 14):
        movies = movies.filter(Movie.Q_arr[0] | Movie.Q_arr[1] | Movie.Q_arr[2] | Movie.Q_arr[3] | Movie.Q_arr[4] | Movie.Q_arr[5] | Movie.Q_arr[6] | Movie.Q_arr[7] | Movie.Q_arr[8] | Movie.Q_arr[9] | Movie.Q_arr[10] | Movie.Q_arr[11] | Movie.Q_arr[12] | Movie.Q_arr[13])
    elif (len(Movie.Q_arr) == 15):
        movies = movies.filter(Movie.Q_arr[0] | Movie.Q_arr[1] | Movie.Q_arr[2] | Movie.Q_arr[3] | Movie.Q_arr[4] | Movie.Q_arr[5] | Movie.Q_arr[6] | Movie.Q_arr[7] | Movie.Q_arr[8] | Movie.Q_arr[9] | Movie.Q_arr[10] | Movie.Q_arr[11] | Movie.Q_arr[12] | Movie.Q_arr[13] | Movie.Q_arr[14])
    elif (len(Movie.Q_arr) == 16):
        movies = movies.filter(Movie.Q_arr[0] | Movie.Q_arr[1] | Movie.Q_arr[2] | Movie.Q_arr[3] | Movie.Q_arr[4] | Movie.Q_arr[5] | Movie.Q_arr[6] | Movie.Q_arr[7] | Movie.Q_arr[8] | Movie.Q_arr[9] | Movie.Q_arr[10] | Movie.Q_arr[11] | Movie.Q_arr[12] | Movie.Q_arr[13] | Movie.Q_arr[14] | Movie.Q_arr[15])
    elif (len(Movie.Q_arr) == 17):
        movies = movies.filter(Movie.Q_arr[0] | Movie.Q_arr[1] | Movie.Q_arr[2] | Movie.Q_arr[3] | Movie.Q_arr[4] | Movie.Q_arr[5] | Movie.Q_arr[6] | Movie.Q_arr[7] | Movie.Q_arr[8] | Movie.Q_arr[9] | Movie.Q_arr[10] | Movie.Q_arr[11] | Movie.Q_arr[12] | Movie.Q_arr[13] | Movie.Q_arr[14] | Movie.Q_arr[15] | Movie.Q_arr[16])
    elif (len(Movie.Q_arr) == 18):
        movies = movies.filter(Movie.Q_arr[0] | Movie.Q_arr[1] | Movie.Q_arr[2] | Movie.Q_arr[3] | Movie.Q_arr[4] | Movie.Q_arr[5] | Movie.Q_arr[6] | Movie.Q_arr[7] | Movie.Q_arr[8] | Movie.Q_arr[9] | Movie.Q_arr[10] | Movie.Q_arr[11] | Movie.Q_arr[12] | Movie.Q_arr[13] | Movie.Q_arr[14] | Movie.Q_arr[15] | Movie.Q_arr[16] | Movie.Q_arr[17])
    
    for movie in Movie.excluded_movies:
        movies = movies.exclude(name=movie)

    return render(request, 'movie_list.html', {'movies': movies, 'selected': Movie.sort_selected, 'checked': Movie.filter_selected})

# re-renders the movie list page when the submit button from the 'Search...' field is clicked to search the movie list
def search(request):
    movies = Movie.objects

    if (Movie.sort_selected == 0):
        movies = movies.order_by('imdb_rating').reverse()
    elif (Movie.sort_selected == 1):
        movies = movies.order_by('runtime')
    elif (Movie.sort_selected == 2):
        movies = movies.order_by('runtime').reverse()
    elif (Movie.sort_selected == 3):
        movies = movies.order_by('release_year')
    elif (Movie.sort_selected == 4):
        movies = movies.order_by('release_year').reverse()
    elif (Movie.sort_selected == 5):
        movies = movies.order_by('box_office')
    elif (Movie.sort_selected == 6):
        movies = movies.order_by('box_office').reverse()
    elif (Movie.sort_selected == 7):
        movies = movies.order_by('recommended_value').reverse()
        
    if 'submit' in request.POST:
        search_value = request.POST.get('search', '')
        movies = movies.filter(Q(name__contains=search_value) | Q(actors__contains=search_value) | Q(directors__contains=search_value))
        
    min_imdb_rating = request.POST.get('min_imdb_rating', '')
    min_runtime = request.POST.get('min_runtime', '')
    max_runtime = request.POST.get('max_runtime', '')
    min_release_year = request.POST.get('min_release_year', '')
    max_release_year = request.POST.get('max_release_year', '')
    min_box_office = request.POST.get('min_box_office', '')
    max_box_office = request.POST.get('max_box_office', '')
    
    if (Movie.min_imdb_rating_filter != 0):
        movies = movies.filter(imdb_rating__gte=Movie.min_imdb_rating_filter)
    if (Movie.min_runtime_filter != 0):
        movies = movies.filter(runtime__gte=Movie.min_runtime_filter)
    if (Movie.max_runtime_filter != 0):
        movies = movies.filter(runtime__lte=Movie.max_runtime_filter)
    if (Movie.min_release_year_filter != 0):
        movies = movies.filter(release_year__gte=Movie.min_release_year_filter)
    if (Movie.max_release_year_filter != 0):
        movies = movies.filter(release_year__lte=Movie.max_release_year_filter)
    if (Movie.min_box_office_filter != 0):
        movies = movies.filter(box_office__gte=Movie.min_box_office_filter)
    if (Movie.max_box_office_filter != 0):
        movies = movies.filter(box_office__lte=Movie.max_box_office_filter)

    if (min_imdb_rating != ''):
        movies = movies.filter(imdb_rating__gte=min_imdb_rating)
        Movie.min_imdb_rating_filter = min_imdb_rating
    if (min_runtime != ''):
        movies = movies.filter(runtime__gte=min_runtime)
        Movie.min_runtime_filter = min_runtime
    if (max_runtime != ''):
        movies = movies.filter(runtime__lte=max_runtime) 
        Movie.max_runtime_filter = max_runtime
    if (min_release_year != ''):
        movies = movies.filter(release_year__gte=min_release_year)
        Movie.min_release_year_filter = min_release_year
    if (max_release_year != ''):
        movies = movies.filter(release_year__lte=max_release_year) 
        Movie.max_release_year_filter = max_release_year
    if (min_box_office != ''):
        movies = movies.filter(box_office__gte=min_box_office)
        Movie.min_box_office_filter = min_box_office
    if (max_box_office != ''):
        movies = movies.filter(box_office__lte=max_box_office) 
        Movie.max_box_office_filter = max_box_office
        
    if (len(Movie.Q_arr) == 1):
        movies = movies.filter(Movie.Q_arr[0])
    elif (len(Movie.Q_arr) == 2):
        movies = movies.filter(Movie.Q_arr[0] | Movie.Q_arr[1])
    elif (len(Movie.Q_arr) == 3):
        movies = movies.filter(Movie.Q_arr[0] | Movie.Q_arr[1] | Movie.Q_arr[2])
    elif (len(Movie.Q_arr) == 4):
        movies = movies.filter(Movie.Q_arr[0] | Movie.Q_arr[1] | Movie.Q_arr[2] | Movie.Q_arr[3])
    elif (len(Movie.Q_arr) == 5):
        movies = movies.filter(Movie.Q_arr[0] | Movie.Q_arr[1] | Movie.Q_arr[2] | Movie.Q_arr[3] | Movie.Q_arr[4])
    elif (len(Movie.Q_arr) == 6):
        movies = movies.filter(Movie.Q_arr[0] | Movie.Q_arr[1] | Movie.Q_arr[2] | Movie.Q_arr[3] | Movie.Q_arr[4] | Movie.Q_arr[5])
    elif (len(Movie.Q_arr) == 7):
        movies = movies.filter(Movie.Q_arr[0] | Movie.Q_arr[1] | Movie.Q_arr[2] | Movie.Q_arr[3] | Movie.Q_arr[4] | Movie.Q_arr[5] | Movie.Q_arr[6])
    elif (len(Movie.Q_arr) == 8):
        movies = movies.filter(Movie.Q_arr[0] | Movie.Q_arr[1] | Movie.Q_arr[2] | Movie.Q_arr[3] | Movie.Q_arr[4] | Movie.Q_arr[5] | Movie.Q_arr[6] | Movie.Q_arr[7])
    elif (len(Movie.Q_arr) == 9):
        movies = movies.filter(Movie.Q_arr[0] | Movie.Q_arr[1] | Movie.Q_arr[2] | Movie.Q_arr[3] | Movie.Q_arr[4] | Movie.Q_arr[5] | Movie.Q_arr[6] | Movie.Q_arr[7] | Movie.Q_arr[8])
    elif (len(Movie.Q_arr) == 10):
        movies = movies.filter(Movie.Q_arr[0] | Movie.Q_arr[1] | Movie.Q_arr[2] | Movie.Q_arr[3] | Movie.Q_arr[4] | Movie.Q_arr[5] | Movie.Q_arr[6] | Movie.Q_arr[7] | Movie.Q_arr[8] | Movie.Q_arr[9])
    elif (len(Movie.Q_arr) == 11):
        movies = movies.filter(Movie.Q_arr[0] | Movie.Q_arr[1] | Movie.Q_arr[2] | Movie.Q_arr[3] | Movie.Q_arr[4] | Movie.Q_arr[5] | Movie.Q_arr[6] | Movie.Q_arr[7] | Movie.Q_arr[8] | Movie.Q_arr[9] | Movie.Q_arr[10])
    elif (len(Movie.Q_arr) == 12):
        movies = movies.filter(Movie.Q_arr[0] | Movie.Q_arr[1] | Movie.Q_arr[2] | Movie.Q_arr[3] | Movie.Q_arr[4] | Movie.Q_arr[5] | Movie.Q_arr[6] | Movie.Q_arr[7] | Movie.Q_arr[8] | Movie.Q_arr[9] | Movie.Q_arr[10] | Movie.Q_arr[11])
    elif (len(Movie.Q_arr) == 13):
        movies = movies.filter(Movie.Q_arr[0] | Movie.Q_arr[1] | Movie.Q_arr[2] | Movie.Q_arr[3] | Movie.Q_arr[4] | Movie.Q_arr[5] | Movie.Q_arr[6] | Movie.Q_arr[7] | Movie.Q_arr[8] | Movie.Q_arr[9] | Movie.Q_arr[10] | Movie.Q_arr[11] | Movie.Q_arr[12])
    elif (len(Movie.Q_arr) == 14):
        movies = movies.filter(Movie.Q_arr[0] | Movie.Q_arr[1] | Movie.Q_arr[2] | Movie.Q_arr[3] | Movie.Q_arr[4] | Movie.Q_arr[5] | Movie.Q_arr[6] | Movie.Q_arr[7] | Movie.Q_arr[8] | Movie.Q_arr[9] | Movie.Q_arr[10] | Movie.Q_arr[11] | Movie.Q_arr[12] | Movie.Q_arr[13])
    elif (len(Movie.Q_arr) == 15):
        movies = movies.filter(Movie.Q_arr[0] | Movie.Q_arr[1] | Movie.Q_arr[2] | Movie.Q_arr[3] | Movie.Q_arr[4] | Movie.Q_arr[5] | Movie.Q_arr[6] | Movie.Q_arr[7] | Movie.Q_arr[8] | Movie.Q_arr[9] | Movie.Q_arr[10] | Movie.Q_arr[11] | Movie.Q_arr[12] | Movie.Q_arr[13] | Movie.Q_arr[14])
    elif (len(Movie.Q_arr) == 16):
        movies = movies.filter(Movie.Q_arr[0] | Movie.Q_arr[1] | Movie.Q_arr[2] | Movie.Q_arr[3] | Movie.Q_arr[4] | Movie.Q_arr[5] | Movie.Q_arr[6] | Movie.Q_arr[7] | Movie.Q_arr[8] | Movie.Q_arr[9] | Movie.Q_arr[10] | Movie.Q_arr[11] | Movie.Q_arr[12] | Movie.Q_arr[13] | Movie.Q_arr[14] | Movie.Q_arr[15])
    elif (len(Movie.Q_arr) == 17):
        movies = movies.filter(Movie.Q_arr[0] | Movie.Q_arr[1] | Movie.Q_arr[2] | Movie.Q_arr[3] | Movie.Q_arr[4] | Movie.Q_arr[5] | Movie.Q_arr[6] | Movie.Q_arr[7] | Movie.Q_arr[8] | Movie.Q_arr[9] | Movie.Q_arr[10] | Movie.Q_arr[11] | Movie.Q_arr[12] | Movie.Q_arr[13] | Movie.Q_arr[14] | Movie.Q_arr[15] | Movie.Q_arr[16])
    elif (len(Movie.Q_arr) == 18):
        movies = movies.filter(Movie.Q_arr[0] | Movie.Q_arr[1] | Movie.Q_arr[2] | Movie.Q_arr[3] | Movie.Q_arr[4] | Movie.Q_arr[5] | Movie.Q_arr[6] | Movie.Q_arr[7] | Movie.Q_arr[8] | Movie.Q_arr[9] | Movie.Q_arr[10] | Movie.Q_arr[11] | Movie.Q_arr[12] | Movie.Q_arr[13] | Movie.Q_arr[14] | Movie.Q_arr[15] | Movie.Q_arr[16] | Movie.Q_arr[17])
        
    for movie in Movie.excluded_movies:
        movies = movies.exclude(name=movie)
    for movie in Movie.rated_movies:
        movies = movies.exclude(name=movie)
        
    return render(request, 'movie_list.html', {'movies': movies, 'selected': Movie.sort_selected, 'checked': Movie.filter_selected})

    