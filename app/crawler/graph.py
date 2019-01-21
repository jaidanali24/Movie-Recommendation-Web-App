from __future__ import print_function
from collections import defaultdict
import logging

class Vertex():
    
    # vertex initializer
    def __init__(self, data):
        data = list(data)
        self.name = data[0]
        self.release_year = data[1]
        self.runtime = data[2]
        self.runtime_str = data[3]
        self.box_office = data[4]
        self.box_office_str = data[5]
        self.genres = data[6]
        self.actors = data[7]
        self.directors = data[8]
        self.writers = data[9]
        self.user_rating = data[10]
        self.imdb_rating = data[11]
        self.num_imdb_ratings = data[12]
        self.num_imdb_ratings_str = data[13]
        self.imdb_popularity = data[14] 
        self.imdb_popularity_str = data[15]
        self.imdb_related_movies = data[16]  
        self.tomatoes_critic_rating = data[17]
        self.tomatoes_user_rating = data[18]
        self.metacritic_rating = data[19]
        self.oscar_wins = data[20]
        self.oscar_noms = data[21]
        self.url = data[22]
        self.seen = data[23]
        self.poster = data[24]
        self.neighbors = list()
        self.recommended_value = data[25]
        
class Graph():
    
    # initializes a Graph object as a dictionary set using a defaultdict object
    def __init__(self, graph_dict = None):
        if (graph_dict == None):
            graph_dict = defaultdict(set)
        self.graph = graph_dict
        self.seen_movie_vertices = set()
        self.seen_movie_names = set()
        self.seen_movie_links = set()
        self.unseen_movie_vertices = set()
        self.unseen_movies = set()
        self.unseen_movie_names = set()
        self.unseen_movie_links = set()
        self.creditor_links = set()
        self.total_seen_movies = 0 
        self.total_unseen_movies = 0 
        self.favorite_genres = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.average_release_year = 0.0
        self.average_runtime = 0.0
        self.high_rated_movies = 0
    
    # adds a vertex 'v' to the graph  
    def add_vertex(self, v):
        if (v.seen == True):
            self.graph[v] = list()
            self.seen_movie_vertices.add(v)
            self.seen_movie_names.add(v.name)
            self.seen_movie_links.add(v.url)
            self.total_seen_movies += 1
            genres_string = parse_string_list(v.genres)
            directors_string = parse_string_list(v.directors)
            writers_string = parse_string_list(v.writers)
            actors_string = parse_string_list(v.actors)
            print("Year: " + str(v.release_year) + "; Genres: " + genres_string + "; Runtime: " + v.runtime_str + "; Box Office: " + v.box_office_str + "; Actors: " + actors_string + "; Directors: " + directors_string + "; Writers: " + writers_string + "; User Rating: " + v.user_rating + "; IMDb Rating: " + str(v.imdb_rating) + "; Number of IMDb Ratings: " + v.num_imdb_ratings_str + "; IMDb Popularity: " + v.imdb_popularity_str + "; Rotten Tomatoes Rating: " + str(v.tomatoes_critic_rating) + "% (critic)/" + str(v.tomatoes_user_rating) + "% (user); Metacritic Rating: " + str(v.metacritic_rating) + "; Oscar Wins: " + str(v.oscar_wins) + "; Oscar Nominations: " + str(v.oscar_noms) + "; Total Movies: " + str(self.total_seen_movies) + "\n")
            logging.info('ADDED SEEN VERTEX for \'' + v.name + '\'')
        else:
            self.graph[v] = list()
            self.unseen_movie_vertices.add(v)
            self.total_unseen_movies += 1
            genres_string = parse_string_list(v.genres)
            directors_string = parse_string_list(v.directors)
            writers_string = parse_string_list(v.writers)
            actors_string = parse_string_list(v.actors)
            print("Year: " + str(v.release_year) + "; Genres: " + genres_string + "; Runtime: " + v.runtime_str + "; Box Office: " + v.box_office_str + "; Actors: " + actors_string + "; Directors: " + directors_string + "; Writers: " + writers_string + "; User Rating: " + v.user_rating + "; IMDb Rating: " + str(v.imdb_rating) + "; Number of IMDb Ratings: " + v.num_imdb_ratings_str + "; IMDb Popularity: " + v.imdb_popularity_str + "; Rotten Tomatoes Rating: " + str(v.tomatoes_critic_rating) + "% (critic)/" + str(v.tomatoes_user_rating) + "% (user); Metacritic Rating: " + str(v.metacritic_rating) + "; Oscar Wins: " + str(v.oscar_wins) + "; Oscar Nominations: " + str(v.oscar_noms) + "; Total Movies: " + str(self.total_unseen_movies) + "; Recommended Value: " + str(v.recommended_value) + "\n")
            logging.info('ADDED UNSEEN VERTEX for \'' + v.name + '\'')
    
    # adds edges between vertices 'v1' and 'v2' if both vertices exist in the graph and have opposite 'seen' values 
    def add_edge(self, v1, v2):
        if (v1 in self.graph) and (v2 in self.graph) and (v1.seen != v2.seen):
            print('ADDING CONNECTION: (' + v1.name + ', ' + v2.name + ')')
            self.graph[v1].append(v2.name)
            self.graph[v2].append(v1.name)
            v1.neighbors.append(v2.name)
            v2.neighbors.append(v1.name)
            if (v1.seen == True) and (v2.seen == False):
                logging.info("Undirected edge added between Seen Movie \'" + v1.name + "\' and Unseen Movie \'" + v2.name + "\'")
            elif (v1.seen == False) and (v2.seen == True):
                logging.info("Undirected edge added between Seen Movie \'" + v2.name + "\' and Unseen Movie \'" + v1.name + "\'")
            
# helper function to print a list of strings
def parse_string_list(li):
    ret_str = str()
    for i in range(len(li)):
        if (i == 0):
            ret_str = li[i]
        elif (i == 1) and (len(li) == 2):
            ret_str = ret_str + " and " + li[i]
        elif (i == len(li) - 1):
            ret_str = ret_str + ", and " + li[i]
        else:
            ret_str = ret_str + ", " + li[i]
    
    return ret_str
    
    