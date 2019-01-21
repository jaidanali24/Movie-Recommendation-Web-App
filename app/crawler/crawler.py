from __future__ import print_function
from bs4 import BeautifulSoup
from graph import Graph, Vertex
from collections import OrderedDict, Counter
from unidecode import unidecode
import numpy as np
import json
import logging
import requests
from cgitb import html

class Crawler:
    
    def __init__(self, load_data, url):
        # logging file
        logging.basicConfig(filename = 'crawler.log', filemode = 'w', level = logging.INFO)
        
        # global variables
        self.g = Graph()
        self.unseen_movies_list = list()
    
        self.crawl_movies(load_data, url)
    
    # main crawling function
    def crawl_movies(self, load_data, url):
        
        # loads graph from JSON data file if one is provided
        if (load_data != None):
            logging.info("Crawler is scraping " + str(len(load_data)) + " unseen movies")
            print("\nCrawler is scraping " + str(len(load_data)) + " unseen movies...\n")
            self.load_graph(load_data)
        else:
            #start_page = raw_input("Enter the URL of your IMDb ratings to begin: ")
            start_page = url
            if ("www.imdb.com" not in start_page):
                logging.warning("The link " + start_page + " cannot be scraped")
                print("The link provided cannot be scraped\n")
                self.crawl_movies(load_data)
            else:
                start_page_html = self.get_html(start_page)
                num_seen_movies = start_page_html.find('span', id = 'lister-header-current-size').text.encode('ascii', 'ignore')
                #num_seen_movies = str(20)
                logging.info("Crawler is scraping " + num_seen_movies + " seen movies")
                print("\nCrawler is scraping " + num_seen_movies + " seen movies...\n")
                num_seen_movies = int(num_seen_movies)
                
                self.get_movie_data(start_page_html, num_seen_movies, True)
                        
    # helper function to gather data from a movie page given a 'url'
    def get_movie_data(self, start_page_html, num_movies, seen):
        
        scraped_movies = 0
        index = 0
        
        #seen_imdb_ratings = list()
        #seen_box_office = list()
        
        if (seen == True):
                anchor_page = start_page_html.find_all('h3', class_ = 'lister-item-header')
        else:
            logging.info("Crawler is scraping " + str(num_movies) + " unseen movies")
            print("Crawler is scraping " + str(num_movies) + " unseen movies...\n")
            anchor_page = start_page_html
        
        while (scraped_movies != num_movies):
            if (seen == True):
                url = "http://www.imdb.com" + anchor_page[index].find_next('a').get('href').encode('ascii', 'ignore')
                #url = "https://www.imdb.com/title/tt0101746/?ref_=nv_sr_3"
            else:
                name, url = anchor_page.pop()
            
            page_html = self.get_html(url)
            recommended_value = 0.0
            
            # name
            if (seen == True):
                name = unidecode(unicode(anchor_page[index].find_next('a').text))
                
            # removes TV shows from user ratings
            rating = page_html.find('meta', itemprop = 'contentRating')
            if (rating != None) and ('TV' in rating.get('content')):
                scraped_movies += 1
                index += 1
                #logging.info('SKIPPED \'' + name + '\'; it is not a movie')
                #print('SKIPPING: \'' + name + '\'')
                continue
            
            # user's IMDb rating
            if (seen == True):
                user_rating = anchor_page[index].find_next('div', class_ = 'ipl-rating-star ipl-rating-star--other-user small').find_next('span', class_ = 'ipl-rating-star__rating').text.encode('ascii', 'ignore')
                if (user_rating >= 9):
                    self.g.high_rated_movies += 1
            else:
                user_rating = 'Unrated'
            
            # release year
            release_year = page_html.find('span', id = 'titleYear')
            if (release_year != None):
                release_year = int(release_year.find_next('a').text.encode('ascii', 'ignore'))
                if (seen == True) and (user_rating >= 9):
                    self.g.average_release_year += release_year
                elif (seen == False):
                    value = abs(float(release_year) - self.g.average_release_year)
                    if (value < 6) or (release_year > self.g.average_release_year):
                        recommended_value += 55
                    elif (release_year < 1970):
                        recommended_value -= 15
                    elif (value < 9):
                        recommended_value += 45
                    elif (value < 12):
                        recommended_value += 35
                    elif (value < 15):
                        recommended_value += 25
                    else:
                        recommended_value += float((1/value) * 300)
            else:
                scraped_movies += 1
                index += 1
                #logging.info('SKIPPED \'' + name + '\'; scraper could not find a release year')
                #print('SKIPPING: \'' + name + '\'')
                continue
            
            # genres
            genres = list(page_html.find('div', class_ = 'subtext').find_all_next('span', itemprop = 'genre'))
            for i in range(len(genres)):
                genres[i] = genres[i].text.encode('ascii', 'ignore')
                if (seen == True) and (user_rating >= 9):
                    if (genres[i] == 'Action'):
                        self.g.favorite_genres[0] +=1
                    if (genres[i] == 'Adventure'):
                        self.g.favorite_genres[1] +=1
                    if (genres[i] == 'Animation'):
                        self.g.favorite_genres[2] +=1
                    if (genres[i] == 'Biography'):
                        self.g.favorite_genres[3] +=1
                    if (genres[i] == 'Comedy'):
                        self.g.favorite_genres[4] +=1
                    if (genres[i] == 'Crime'):
                        self.g.favorite_genres[5] +=1
                    if (genres[i] == 'Documentary'):
                        self.g.favorite_genres[6] +=1
                    if (genres[i] == 'Drama'):
                        self.g.favorite_genres[7] +=1
                    if (genres[i] == 'Fantasy'):
                        self.g.favorite_genres[8] +=1
                    if (genres[i] == 'History'):
                        self.g.favorite_genres[9] +=1
                    if (genres[i] == 'Horror'):
                        self.g.favorite_genres[10] +=1
                    if (genres[i] == 'Musical'):
                        self.g.favorite_genres[11] +=1
                    if (genres[i] == 'Mystery'):
                        self.g.favorite_genres[12] +=1
                    if (genres[i] == 'Romance'):
                        self.g.favorite_genres[13] +=1
                    if (genres[i] == 'Sci-Fi'):
                        self.g.favorite_genres[14] +=1
                    if (genres[i] == 'Sport'):
                        self.g.favorite_genres[15] +=1
                    if (genres[i] == 'Thriller'):
                        self.g.favorite_genres[16] +=1
                    if (genres[i] == 'War'):
                        self.g.favorite_genres[17] +=1
                    if (genres[i] == 'Western'):
                        self.g.favorite_genres[18] +=1
                elif (seen == False):
                    if (genres[i] == 'Action'):
                        recommended_value += float(self.g.favorite_genres[0]/2)
                    if (genres[i] == 'Adventure'):
                        recommended_value += float(self.g.favorite_genres[1]/2)
                    if (genres[i] == 'Animation'):
                        recommended_value += float(self.g.favorite_genres[2]/2)
                    if (genres[i] == 'Biography'):
                        recommended_value += float(self.g.favorite_genres[3]/2)
                    if (genres[i] == 'Comedy'):
                        recommended_value += float(self.g.favorite_genres[4]/2)
                    if (genres[i] == 'Crime'):
                        recommended_value += float(self.g.favorite_genres[5]/2)
                    if (genres[i] == 'Documentary'):
                        recommended_value += float(self.g.favorite_genres[6]/2)
                    if (genres[i] == 'Drama'):
                        recommended_value += float(self.g.favorite_genres[7]/2)
                    if (genres[i] == 'Fantasy'):
                        recommended_value += float(self.g.favorite_genres[8]/2)
                    if (genres[i] == 'History'):
                        recommended_value += float(self.g.favorite_genres[9]/2)
                    if (genres[i] == 'Horror'):
                        recommended_value += float(self.g.favorite_genres[10]/2)
                    if (genres[i] == 'Musical'):
                        recommended_value += float(self.g.favorite_genres[11]/2)
                    if (genres[i] == 'Mystery'):
                        recommended_value += float(self.g.favorite_genres[12]/2)
                    if (genres[i] == 'Romance'):
                        recommended_value += float(self.g.favorite_genres[13]/2)
                    if (genres[i] == 'Sci-Fi'):
                        recommended_value += float(self.g.favorite_genres[14]/2)
                    if (genres[i] == 'Sport'):
                        recommended_value += float(self.g.favorite_genres[15]/2)
                    if (genres[i] == 'Thriller'):
                        recommended_value += float(self.g.favorite_genres[16]/2)
                    if (genres[i] == 'War'):
                        recommended_value += float(self.g.favorite_genres[17]/2)
                    if (genres[i] == 'Western'):
                        recommended_value += float(self.g.favorite_genres[18]/2)
            
            # runtime
            runtime = page_html.find('div', class_ = 'title_wrapper').find_next('time')
            if (runtime != None):
                runtime = runtime.text.encode('ascii', 'ignore')
                runtime = runtime[25:]
                runtime = runtime.split(' ', 2)
                if (runtime[1] == ''):
                    runtime = runtime[0].split('\n')[0] + ' 0min'
                else:
                    runtime = runtime[0] + ' ' + runtime[1]
                    runtime = runtime.split('n')[0] + 'n'
            if (runtime == None) or ('h' not in runtime):
                scraped_movies += 1
                index += 1
                #logging.info('SKIPPED \'' + name + '\'; scraper could not find a runtime')
                #print('SKIPPING: \'' + name + '\'')
                continue
            else:
                hours = runtime.split('h ')
                minutes = int(hours[1].split('min')[0])
                hours = int(hours[0]) * 60
                total_min = hours + minutes
                if (seen == True) and (user_rating >= 9):
                    self.g.average_runtime += total_min
                if (seen == False) and (total_min < 75):
                    scraped_movies += 1
                    index += 1
                    #logging.info('SKIPPED \'' + name + '\'; movie too short')
                    #print('SKIPPING: \'' + name + '\'')
                    continue
                elif (seen == False):
                    value = abs(float(total_min) - self.g.average_runtime)
                    if (value <= 15):
                        recommended_value += 40
                    elif (value <= 20):
                        recommended_value += 30
                    elif (value <= 25):
                        recommended_value += 20
                    elif (value <= 30):
                        recommended_value += 10
                    else:
                        recommended_value += float((1/value) * 300)
    
            # box office
            box_office = page_html.find('div', id = "titleDetails").find_next('h3', class_ = 'subheading').find_next('a').find_previous('div', class_ = 'txt-block').text.encode('ascii', 'ignore')
            if ('$' not in box_office):
                box_office = 'Unknown'
                box_office_val = 0
            else:
                box_office = box_office.split('$', 1)
                box_office = '$' + box_office[1]
                box_office = box_office.split(' ')[0]
                box_office = box_office[:len(box_office) - 1]
                if ('$' in box_office):
                    box_office_val = int(box_office.split('$')[1].replace(',', ''))
                else:
                    box_office_val = int(box_office.replace(',', ''))
                if (seen == False) and (box_office_val < 45000):
                    scraped_movies += 1
                    index += 1
                    #logging.info('SKIPPED \'' + name + '\'; box office value too low')
                    #print('SKIPPING: \'' + name + '\'')
                    continue
                elif (seen == False):
                    if (box_office_val >= 2000000000):
                        recommended_value += 80
                    elif (box_office_val >= 1500000000):
                        recommended_value += 70
                    elif (box_office_val >= 1000000000):
                        recommended_value += 60
                    elif (box_office_val >= 500000000):
                        recommended_value += 50
                    elif (box_office_val >= 350000000):
                        recommended_value += 40
                    elif (box_office_val >= 200000000):
                        recommended_value += 30
                    elif (release_year == 2018) or (box_office_val >= 100000000):
                        recommended_value += 25
                    else:
                        recommended_value += 20
            
            # actors, directors, and writers
            creditors = page_html.find_all('div', class_ = 'credit_summary_item', limit = 3)
            actors = None
            directors = None
            writers = None
            creditor_links = set()
            if (len(creditors) == 3):
                actors = list(creditors[2].find_all('span', itemprop = 'name'))
                directors = list(creditors[0].find_all('span', itemprop = 'name'))
                writers = list(creditors[1].find_all('span', itemprop = 'name'))
                
                # if the user's rating is at least 9, search the actors/directors/writers for related movies
                if (seen == True) and (int(user_rating) >= 9):
                    creditor_links = creditor_links.union(set(creditors[0].find_all_next('a', limit = 3)))
                    creditor_links = creditor_links.union(set(creditors[1].find_all_next('a', limit = 3)))
                    creditor_links = creditor_links.union(set(creditors[2].find_all_next('a', limit = 3)))
                    for link in creditor_links:
                        if (("http://www.imdb.com" + link.get('href').encode('ascii', 'ignore')) not in self.g.creditor_links) and (link.get('href').encode('ascii', 'ignore').startswith('/')):
                            self.g.creditor_links.add("http://www.imdb.com" + link.get('href').encode('ascii', 'ignore'))
            elif (len(creditors) == 2):
                actors = list(creditors[1].find_all('span', itemprop = 'name'))
                directors = list(creditors[0].find_all('span', itemprop = 'name'))
                writers = 'None'
                
                # if the user's rating is at least 9, search the actors/directors for related movies
                if (seen == True) and (int(user_rating) >= 9):

                    creditor_links = creditor_links.union(set(creditors[0].find_all_next('a', limit = 3)))
                    creditor_links = creditor_links.union(set(creditors[1].find_all_next('a', limit = 3)))
                    for link in creditor_links:
                        if (("http://www.imdb.com" + link.get('href').encode('ascii', 'ignore')) not in self.g.creditor_links) and (link.get('href').encode('ascii', 'ignore').startswith('/')):
                            self.g.creditor_links.add("http://www.imdb.com" + link.get('href').encode('ascii', 'ignore'))   
            if (actors == None) or (directors == None):
                scraped_movies += 1
                index += 1
                #logging.info('SKIPPED \'' + name + '\'; scraper could not find a list of actors or directors')
                #print('SKIPPING: \'' + name + '\'')
                continue
            for i in range(len(actors)):
                actors[i] = actors[i].text.encode('ascii', 'ignore') 
            for i in range(len(directors)):
                directors[i] = directors[i].text.encode('ascii', 'ignore')
            if (writers != 'None'):
                for i in range(len(writers)):
                    writers[i] = writers[i].text.encode('ascii', 'ignore')
                
            # IMDb rating
            if (page_html.find('span', itemprop = 'ratingValue') != None):
                imdb_rating = float(page_html.find('span', itemprop = 'ratingValue').text.encode('ascii', 'ignore'))
                if (seen == False) and (imdb_rating < 6.0):
                    scraped_movies += 1
                    index += 1
                    #logging.info('SKIPPED \'' + name + '\'; IMDb rating too low')
                    #print('SKIPPING: \'' + name + '\'')
                    continue
                elif (seen == False):
                    if (imdb_rating >= 8.5):
                        recommended_value += 100
                    elif (imdb_rating >= 8.3):
                        recommended_value += 90
                    elif (imdb_rating >= 8.1):
                        recommended_value += 80
                    elif (imdb_rating >= 7.9):
                        recommended_value += 70
                    elif (imdb_rating >= 7.6):
                        recommended_value += 50
                    elif (imdb_rating >= 7.3):
                        recommended_value += 30
                    elif (imdb_rating < 7.0):
                        recommended_value -= 20
            else:
                scraped_movies += 1
                index += 1
                #logging.info('SKIPPED \'' + name + '\'; scraper could not find an IMDb rating')
                #print('SKIPPING: \'' + name + '\'')
                continue
            
            # number of IMDb ratings
            num_imdb_ratings = page_html.find('span', itemprop = 'ratingCount').text.encode('ascii', 'ignore')
            num_ratings_val = int(num_imdb_ratings.replace(',', ''))
            if (seen == False) and (num_ratings_val < 10000):
                scraped_movies += 1
                index += 1
                #logging.info('SKIPPED \'' + name + '\'; not enough IMDb ratings')
                #print('SKIPPING: \'' + name + '\'')
                continue
            elif (seen == False):
                if (num_ratings_val > 1500000):
                    recommended_value += 65
                elif (num_ratings_val > 1000000):
                    recommended_value += 55
                elif (num_ratings_val > 750000):
                    recommended_value += 45
                elif (num_ratings_val > 500000) or ((release_year >= 2017) and (num_ratings_val > 300000)):
                    recommended_value += 35
                elif (num_ratings_val > 300000) or ((release_year >= 2017) and (num_ratings_val > 200000)):
                    recommended_value += 25
                elif (num_ratings_val > 200000) or (release_year == 2018):
                    recommended_value += 15
                else:
                    recommended_value += 10
    
            # IMDb popularity
            imdb_popularity = page_html.find('div', id = 'sidebar').find_previous('div', class_ = 'titleReviewBarSubItem')
            if (imdb_popularity == None) or ('Popularity' not in imdb_popularity.text.encode('ascii', 'ignore')):
                imdb_popularity = 'Unknown'
                popularity_val = 0
            else: 
                imdb_popularity = imdb_popularity.find_next('span', class_ = 'subText').text.encode('ascii', 'ignore')
                imdb_popularity = imdb_popularity[21:]
                imdb_popularity = imdb_popularity.split(' ')[0]
                imdb_popularity = imdb_popularity[:len(imdb_popularity) - 1]
                popularity_val = int(imdb_popularity.replace(',', ''))
            
            # IMDb related movies
            if (seen == True):
                imdb_related_movies = page_html.find('div', class_ = 'rec_slide')
                if (imdb_related_movies != None):
                    imdb_related_movies = list(imdb_related_movies.find_all_next('div', class_ = 'rec_item', limit = 6))
                    for i in range(len(imdb_related_movies)):
                        unseen_url = 'http://www.imdb.com' + imdb_related_movies[i].find_next('a').get('href')
                        unseen_name = imdb_related_movies[i].find_next('img').get('title').encode('ascii', 'ignore')
                        if (unseen_name not in self.g.unseen_movie_names) and (unseen_url not in self.g.unseen_movie_links):
                            self.g.unseen_movie_names.add(unseen_name)
                            self.g.unseen_movie_links.add(unseen_url)
                            self.g.unseen_movies.add((unseen_name, unseen_url))
                else:
                    imdb_related_movies = 'None' 
            else:
                imdb_related_movies = 'None'
                
            # Rotten Tomatoes ratings
            if (seen == True):
                tomatoes_critic_rating = 0
                tomatoes_user_rating = 0
            else:
                tomatoes_url = name.replace(':', '')
                tomatoes_url = tomatoes_url.replace('.', '')
                tomatoes_url = tomatoes_url.replace('-', '_')
                tomatoes_url = tomatoes_url.replace('&', 'and')
                tomatoes_url = tomatoes_url.replace('\'', '')
                tomatoes_url = tomatoes_url.replace('/', '')
                tomatoes_url_2 = tomatoes_url.replace(' ', '_').lower()
                tomatoes_url = tomatoes_url.replace('The ', '')
                tomatoes_url = tomatoes_url.replace('A ', '')
                tomatoes_url = tomatoes_url.replace(' ', '_').lower()
                tomatoes_url_3 = tomatoes_url + '_' + str(release_year)
                
                tomatoes_page = self.get_html("https://www.rottentomatoes.com/m/" + tomatoes_url)
                if (tomatoes_page == None):
                    tomatoes_page = self.get_html("https://www.rottentomatoes.com/m/" + tomatoes_url_3)
                    if (tomatoes_page == None):
                        tomatoes_page = self.get_html("https://www.rottentomatoes.com/m/" + tomatoes_url_2)
                if (tomatoes_page == None) or (tomatoes_page.find('div', id = 'all-critics-numbers').find_next('p').text == 'Tomatometer Not Available...'):
                    tomatoes_page = None
                    search_url = 'https://www.google.com/search?q=' + tomatoes_url_2.replace('_', '+') + '+' + str(release_year)
                    search_page = self.get_html(search_url)
                    find_movie = list(search_page.find_all('div', class_ = 'hJND5c'))
                    for i in range(len(find_movie)):
                        find_movie[i] = find_movie[i].find_next('cite').text
                        if ("www.rottentomatoes.com/m" in find_movie[i]):
                            tomatoes_page = self.get_html(find_movie[i])
                            break                        
                if (tomatoes_page == None):
                    tomatoes_critic_rating = 0
                    tomatoes_user_rating = 0
                else:
                    if (tomatoes_page.find('div', class_ = 'critic-score meter') != None):
                        tomatoes_critic_rating = tomatoes_page.find('div', class_ = 'critic-score meter').find_next('span', class_ = 'meter-value superPageFontColor').text.encode('ascii', 'ignore')
                        tomatoes_critic_rating = int(tomatoes_critic_rating.split('%')[0])
                    else:
                        tomatoes_critic_rating = 0
                        
                    if (tomatoes_page.find('div', class_ = 'audience-score meter') != None):
                        tomatoes_user_rating = tomatoes_page.find('div', class_ = 'audience-score meter').find_next('span', class_ = 'superPageFontColor').text.encode('ascii', 'ignore')
                        tomatoes_user_rating = int(tomatoes_user_rating.split('%')[0])
                    else:
                        tomatoes_user_rating = 0
                    
                if (tomatoes_critic_rating >= 95):
                    recommended_value += 50
                elif (tomatoes_critic_rating >= 90):
                    recommended_value += 40
                elif (tomatoes_critic_rating >= 85):
                    recommended_value += 30
                elif (tomatoes_critic_rating >= 80):
                    recommended_value += 20
                elif (tomatoes_critic_rating <= 65):
                    recommended_value -= 20
                    
                if (tomatoes_user_rating >= 95):
                    recommended_value += 50
                elif (tomatoes_user_rating >= 90):
                    recommended_value += 40
                elif (tomatoes_user_rating >= 85):
                    recommended_value += 30
                elif (tomatoes_user_rating >= 80):
                    recommended_value += 20
                elif (tomatoes_user_rating <= 65):
                    recommended_value -= 20

            # Metacritic rating
            if (page_html.find('div', class_ = 'titleReviewBarItem') != None):
                metacritic_rating = page_html.find('div', class_ = 'titleReviewBarItem').find_next('span').text.encode('ascii', 'ignore')
                if (' ' in metacritic_rating):
                    metacritic_rating = 'Unrated'
                    metacritic_rating_val = 0
                else:
                    metacritic_rating_val = int(metacritic_rating)
            else:
                metacritic_rating = 'Unrated'
                metacritic_rating_val = 0
                
            # Oscar wins and nominations
            oscar_wins = 0
            oscar_noms = 0
            awards = page_html.find('div', id = 'titleAwardsRanks')
            if (awards != None):
                awards_page = awards.find_next('span', class_ = 'see-more inline').find_next('a')
                if (awards_page != None) and (awards_page.text.encode('ascii', 'ignore') == 'See more awards'):
                    awards_page = self.get_html("http://www.imdb.com" + awards_page.get('href'))
                    awards_page = awards_page.find('div', class_ = 'article listo').find_next('h3').find_next('h3')
                    if ('Academy Awards' in awards_page.text.encode('ascii', 'ignore')):
                        awards_page = awards_page.find_next('table').select('tr')
                        for i in range(len(awards_page)):
                            award = awards_page[i].select('b')
                            if (len(award) == 1):
                                if (award[0].text.encode('ascii', 'ignore') == 'Winner'):
                                    continue
                                elif (award[0].text.encode('ascii', 'ignore') == 'Nominee'):
                                    oscar_noms = (len(awards_page) - i)
                            oscar_wins = (len(awards_page) - oscar_noms)
            if (seen == False):
                recommended_value += (10 * oscar_wins)
                recommended_value += (5 * oscar_noms)
            
            # movie poster
            if (page_html.find('div', class_ = 'poster') != None):
                poster = page_html.find('div', class_ = 'poster').find_next('img').get('src')
            else:
                scraped_movies += 1
                index += 1
                #logging.info('SKIPPED \'' + name + '\'; scraper could not find a movie poster')
                #print('SKIPPING: \'' + name + '\'')
                continue
            
            # updates the global movie sets for sorting
            if (seen == False): 
                unseen_movie_data = OrderedDict([("name", name), ("release_year", release_year), ("runtime", total_min), ("box_office", box_office_val), ("genres", genres), ("actors", actors), ("directors", directors), ("writers", writers), ("imdb_rating", imdb_rating), ("num_imdb_ratings", num_ratings_val), ("imdb_popularity", popularity_val), ("tomatoes_critic_rating", tomatoes_critic_rating), ("tomatoes_user_rating", tomatoes_user_rating), ("metacritic_rating", metacritic_rating_val), ("oscar_wins", oscar_wins), ("oscar_noms", oscar_noms), ("url", url), ("poster", poster), ("recommended_value", recommended_value)])
                self.unseen_movies_list.append(unseen_movie_data)
            
            # adds a Movie Vertex to the graph
            if (seen == True):
                print('ADDING SEEN MOVIE: \'' + name + '\'')
            else:
                print('ADDING UNSEEN MOVIE: \'' + name + '\'')
            vertex = Vertex([name, release_year, total_min, runtime, box_office_val, box_office, genres, actors, directors, writers, user_rating, float(imdb_rating), num_ratings_val, num_imdb_ratings, popularity_val, imdb_popularity, imdb_related_movies, tomatoes_critic_rating, tomatoes_user_rating, metacritic_rating_val, oscar_wins, oscar_noms, url, seen, poster, recommended_value])
            self.g.add_vertex(vertex)
            
            # updates counters
            scraped_movies += 1
            index += 1
    
            # goes to the next page of the user's ratings
            if (seen == True) and (scraped_movies % 100 == 0) and (scraped_movies != num_movies):
                start_page_html = self.get_html("http://www.imdb.com" + start_page_html.find('a', class_ = 'flat-button lister-page-next next-page').get('href').encode('ascii', 'ignore'))
                index = 0
                anchor_page = start_page_html.find_all('h3', class_ = 'lister-item-header')
        
        if (seen == True):
            # updates the graph's averages for high rated movies
            self.g.average_release_year = float(self.g.average_release_year/self.g.high_rated_movies)
            self.g.average_runtime = float(self.g.average_runtime/self.g.high_rated_movies)
            
            # removes all the user's rated movies from the unseen movies set and sorts it
            print('Added ' + str(self.g.total_seen_movies) + ' seen movies to the graph (skipped ' + str(num_movies - self.g.total_seen_movies) + ')')
            logging.info("Scraped the user's rated movies")
            unseen_movies_copy = self.g.unseen_movies.copy()
            for (n, l) in unseen_movies_copy:
                if (n in self.g.seen_movie_names) or (l in self.g.seen_movie_links):
                    self.g.unseen_movie_names.remove(n)
                    self.g.unseen_movie_links.remove(l)
                    self.g.unseen_movies.remove((n, l))
            
            # adds movies related to the creditors that have not been seen to the unseen movies set    
            print('Checking ' + str(len(self.g.creditor_links)) + ' related movies...\n')
            for link in self.g.creditor_links:
                creditor_page = self.get_html(link)
                if (creditor_page.find('div', id = 'knownfor') != None):
                    known_for = list(creditor_page.find('div', id = 'knownfor').find_all_next('a', class_ = 'knownfor-ellipsis', limit = 4))
                    for i in range(len(known_for)):
                        if (known_for[i].text.encode('ascii', 'ignore') not in self.g.seen_movie_names) and (known_for[i].text.encode('ascii', 'ignore') not in self.g.unseen_movie_names):
                            self.g.unseen_movie_names.add(known_for[i].text)
                            self.g.unseen_movie_links.add("http://www.imdb.com" + known_for[i].get('href').encode('ascii', 'ignore'))
                            self.g.unseen_movies.add((known_for[i].text, "http://www.imdb.com" + known_for[i].get('href').encode('ascii', 'ignore')))
                            #print('CHECKING UNSEEN MOVIE: ' + known_for[i].text)
            print()
            
            # runs the crawler on the scraped unseen movies
            self.get_movie_data(self.g.unseen_movies, len(self.g.unseen_movies), False)        
        else:
            print('Added ' + str(self.g.total_unseen_movies) + ' unseen movies to the graph (skipped ' + str(num_movies - self.g.total_unseen_movies) + ')')
            logging.info("Scraped the user's unseen movies")
            
            # stores the complete graph data in a JSON file
            with open('movie_data.json', 'w') as fp:
                logging.info("Logging unseen movie data...")
                json.dump(self.unseen_movies_list, fp, indent = 4) 
            
            
    # helper function that gets the html code from a given 'url'
    def get_html(self, url):
        if ("www.imdb.com" in url) or ("www.google.com" in url):
            page = requests.get(url)
            page_data = page.text
            html = BeautifulSoup(page_data, "html.parser")
            return html
        elif ("www.rottentomatoes.com" in url):
            page = requests.get(url)
            page_data = page.text
            html = BeautifulSoup(page_data, "html.parser")
            if (html.find('aside', id = 'movieListColumn') == None) and ("https://www.rottentomatoes.com/search" not in url):
                return None
            else:
                return html
        else:
            logging.warning("The link " + url + " cannot be scraped")
            print("The link provided cannot be scraped\n")
            self.crawl_movies(None)
            
    # loads data from a given JSON file into the graph structure
    def load_graph(self, load_data):
        
        # adds all the unseen movie vertices
        for elem in load_data:
            name = elem['name'].encode('ascii', 'ignore')
            
            release_year = elem['release_year']
            
            runtime = elem['runtime']
            runtime_str = self.parse_runtime(elem['runtime'])

            box_office = elem['box_office']
            box_office_str = self.parse_long_int(elem['box_office'], True)
            
            genres = list()
            for i in range(len(elem['genres'])):
                genres.append(elem['genres'][i].encode('ascii', 'ignore'))
                
            actors = list()
            for i in range(len(elem['actors'])):
                actors.append(elem['actors'][i].encode('ascii', 'ignore'))
                
            directors = list()
            for i in range(len(elem['directors'])):
                directors.append(elem['directors'][i].encode('ascii', 'ignore'))
                
            writers = list()
            for i in range(len(elem['writers'])):
                writers.append(elem['writers'][i].encode('ascii', 'ignore'))
            
            user_rating = 'Unrated'
            
            imdb_rating = elem['imdb_rating']
            
            num_imdb_ratings = elem['num_imdb_ratings']
            num_imdb_ratings_str = self.parse_long_int(elem['num_imdb_ratings'], False)
            
            imdb_popularity = elem['imdb_popularity']
            imdb_popularity_str = self.parse_long_int(elem['imdb_popularity'], False)
            
            imdb_related_movies = 'None'
            
            tomatoes_critic_rating = elem['tomatoes_critic_rating']
            tomatoes_user_rating = elem['tomatoes_user_rating']
            
            metacritic_rating = elem['metacritic_rating']
            
            oscar_wins = elem['oscar_wins']
            oscar_noms = elem['oscar_noms']
            
            url = elem['url'].encode('ascii', 'ignore')
            
            poster = elem['poster']
            
            recommended_value = elem['recommended_value']
            
            print('ADDING UNSEEN MOVIE: \'' + name + '\'')
            vertex = Vertex([name, release_year, runtime, runtime_str, box_office, box_office_str, genres, actors, directors, writers, user_rating, imdb_rating, num_imdb_ratings, num_imdb_ratings_str, imdb_popularity, imdb_popularity_str, imdb_related_movies, tomatoes_critic_rating, tomatoes_user_rating, metacritic_rating, oscar_wins, oscar_noms, url, False, poster, recommended_value])
            self.g.add_vertex(vertex)
            
    # helper function to convert runtime int to runtime string
    def parse_runtime(self, runtime):
        hours = 0
        minutes = runtime
        while (minutes >= 60):
            minutes -= 60
            hours += 1
        runtime_str = str(hours) + "h " + str(minutes) + "min" 
        return runtime_str
    
    # helper function to convert an int to a string
    def parse_long_int(self, val, dollar_amount):
        val = str(val)
        if (len(val) > 3):
            val_list = [val[i-3:i] for i in range(len(val), 0, -3)]
            val_str = ''
            if (len(val) > 9):
                buf = len(val) - 9
                val_list[3] = val[0:buf]
            elif (len(val) < 9) and (len(val) > 6):
                buf = 10 - len(val)
                val_list[2] = val[0:(4 - buf)]
            elif (len(val) < 6):
                buf = 7 - len(val)
                val_list[1] = val[0:(4 - buf)]
            for i in range(len(val_list) - 1, -1, -1):
                val_str += (val_list[i] + ',')
            val_str = val_str[:len(val_str) - 1]
            if (dollar_amount == True):
                val_str = '$' + val_str
            return val_str
        else:
            return str(val)

