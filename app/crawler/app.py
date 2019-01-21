from crawler import Crawler
import json

#load_data = json.load(open('movie_data.json'))
load_data = None

Crawler(load_data, 'https://www.imdb.com/user/ur65913399/ratings')
#Crawler(load_data, None)