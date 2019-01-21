from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.render_home_page, name='home_page'),
    url(r'^movies$', views.render_movie_list, name='movie_list'),
    url(r'^movies/clear_all$', views.clear_all_movies, name='clear_all_movies'),
    url(r'^clear_movie$', views.clear_movie, name='clear_movie'),
    url(r'^rate_movie$', views.rate_movie, name='rate_movie'),
    url(r'^sort_by$', views.sort_by, name='sort_by'),
    url(r'^filter_by$', views.filter_by, name='filter_by'),
    url(r'^search$', views.search, name='search'),
]