from __future__ import print_function
from bs4 import BeautifulSoup
from graph import Graph, Vertex
from collections import OrderedDict
import numpy as np
import json
import logging
import requests

class Crawler:
    
    def __init__(self, load_data):
        # logging file
        logging.basicConfig(filename = 'crawler.log', filemode = 'w', level = logging.INFO)
        
        # global variables
        self.g = Graph()
        self.unseen_movies_list = list()
    
        self.crawl_movies(load_data)
    
    # main crawling function
    def crawl_movies(self, load_data):
        
        # loads graph from JSON data file if one is provided
        if (load_data != None):
            logging.info("Crawler is scraping " + str(len(load_data)) + " unseen movies")
            print("\nCrawler is scraping " + str(len(load_data)) + " unseen movies...\n")
            self.load_graph(load_data)
        else:
            start_page = raw_input("Enter the URL of your IMDb ratings to begin: ")
            if ("www.imdb.com" not in start_page):
                logging.warning("The link " + start_page + " cannot be scraped")
                print("The link provided cannot be scraped\n")
                self.crawl_movies(load_data)
            else:
                start_page_html = self.get_html(start_page)
                num_seen_movies = start_page_html.find('span', id = 'lister-header-current-size').text.encode('ascii', 'ignore')
                #num_seen_movies = str(5)
                logging.info("Crawler is scraping " + num_seen_movies + " seen movies")
                print("\nCrawler is scraping " + num_seen_movies + " seen movies...\n")
                num_seen_movies = int(num_seen_movies)
                
                self.get_movie_data(start_page_html, num_seen_movies, None, True)
        
    # helper function to gather data from a movie page given a 'url'
    def get_movie_data(self, start_page_html, num_movies, imdb_ratings_threshold, seen):
        
        scraped_movies = 0
        index = 0
        
        seen_imdb_ratings = list()
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
            
            # name
            if (seen == True):
                name = anchor_page[index].find_next('a').text.encode('ascii', 'ignore')
                    
            # removes TV shows from user ratings
            rating = page_html.find('meta', itemprop = 'contentRating')
            if (rating != None) and ('TV' in rating.get('content')):
                scraped_movies += 1
                index += 1
                logging.info('SKIPPED \'' + name + '\'; it is not a movie')
                print('SKIPPING: \'' + name + '\'')
                continue
            
            # user's IMDb rating
            if (seen == True):
                user_rating = anchor_page[index].find_next('div', class_ = 'ipl-rating-star ipl-rating-star--other-user small').find_next('span', class_ = 'ipl-rating-star__rating').text.encode('ascii', 'ignore')
            else:
                user_rating = 'Unrated'
            
            # release year
            release_year = page_html.find('span', id = 'titleYear')
            if (release_year != None):
                release_year = release_year.find_next('a').text.encode('ascii', 'ignore')
            else:
                scraped_movies += 1
                index += 1
                logging.info('SKIPPED \'' + name + '\'; scraper could not find a release year')
                print('SKIPPING: \'' + name + '\'')
                continue
            
            # genres
            genres = list(page_html.find('div', class_ = 'subtext').find_all_next('span', itemprop = 'genre'))
            for i in range(len(genres)):
                genres[i] = genres[i].text.encode('ascii', 'ignore')
            
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
                logging.info('SKIPPED \'' + name + '\'; scraper could not find a runtime')
                print('SKIPPING: \'' + name + '\'')
                continue
            else:
                hours = runtime.split('h ')
                minutes = int(hours[1].split('min')[0])
                hours = int(hours[0]) * 60
                total_min = hours + minutes
    
            # box office
            box_office = page_html.find('div', id = "titleDetails").find_next('h3', class_ = 'subheading').find_next('a').find_previous('div', class_ = 'txt-block').text.encode('ascii', 'ignore')
            if ('$' not in box_office):
                box_office = 'Unknown'
                box_office_val = 'Unknown'
            else:
                box_office = box_office.split('$', 1)
                box_office = '$' + box_office[1]
                box_office = box_office.split(' ')[0]
                box_office = box_office[:len(box_office) - 1]
                if ('$' in box_office):
                    box_office_val = int(box_office.split('$')[1].replace(',', ''))
                else:
                    box_office_val = int(box_office.replace(',', ''))
                
            #if ('$' in box_office):
            #    box_office_val = int(box_office.split('$')[1].replace(',', ''))
            #elif (box_office != 'Unknown'):
            #    box_office_val = int(box_office.replace(',', ''))
            #if (seen == True) and (int(user_rating) >= 8) and (box_office != 'Unknown'):
            #    seen_box_office.append(box_office_val)
            #elif (seen == False) and (box_office != 'Unknown') and (box_office_val < box_office_threshold):
            #    logging.info('Skipped \'' + name + '\'; IMDb rating of ' + str(box_office_val) + ' is below the threshold of ' + str(box_office_threshold))
            #    scraped_movies += 1
            #    continue
            
            # actors, directors, and writers
            creditors = page_html.find_all('div', class_ = 'credit_summary_item', limit = 3)
            actors = None
            directors = None
            writers = None
            if (len(creditors) == 3):
                actors = list(creditors[2].find_all('span', itemprop = 'name'))
                directors = list(creditors[0].find_all('span', itemprop = 'name'))
                writers = list(creditors[1].find_all('span', itemprop = 'name'))
            elif (len(creditors) == 2):
                actors = list(creditors[1].find_all('span', itemprop = 'name'))
                directors = list(creditors[0].find_all('span', itemprop = 'name'))
                writers = 'None'
            if (actors == None) or (directors == None):
                scraped_movies += 1
                index += 1
                logging.info('SKIPPED \'' + name + '\'; scraper could not find a list of actors or directors')
                print('SKIPPING: \'' + name + '\'')
                continue
                
            for i in range(len(actors)):
                actors[i] = actors[i].text.encode('ascii', 'ignore') 
            for i in range(len(directors)):
                directors[i] = directors[i].text.encode('ascii', 'ignore')
            if (writers != 'None'):
                for i in range(len(writers)):
                    writers[i] = writers[i].text.encode('ascii', 'ignore')
                
            # IMDb rating
            imdb_rating = page_html.find('span', itemprop = 'ratingValue').text.encode('ascii', 'ignore')
            if (seen == True) and (int(user_rating) >= 8):
                seen_imdb_ratings.append(float(imdb_rating))
            elif (seen == False) and (float(imdb_rating) < imdb_ratings_threshold):
                scraped_movies += 1
                logging.info('SKIPPED \'' + name + '\'; IMDb rating of ' + imdb_rating + ' is below the threshold of ' + str(imdb_ratings_threshold))
                print('SKIPPING: \'' + name + '\'')
                continue
            
            # number of IMDb ratings
            num_imdb_ratings = page_html.find('span', itemprop = 'ratingCount').text.encode('ascii', 'ignore')
            num_ratings_val = int(num_imdb_ratings.replace(',', ''))
    
            # IMDb popularity
            imdb_popularity = page_html.find('div', id = 'sidebar').find_previous('div', class_ = 'titleReviewBarSubItem')
            if (imdb_popularity == None) or ('Popularity' not in imdb_popularity.text.encode('ascii', 'ignore')):
                imdb_popularity = 'Unknown'
                popularity_val = 'Unknown'
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
            #if (' - ' in name):
            #    tomatoes_url = name.split(' - ')[1].replace(' ', '_')
            #    tomatoes_url = tomatoes_url.replace(',', '')
            #else:
            #    tomatoes_url = name.replace(' ', '_')
            #    tomatoes_url = tomatoes_url.replace(',', '')
            #tomatoes_page = get_html("https://www.rottentomatoes.com/m/" + tomatoes_url)
            #tomatoes_critic_rating = tomatoes_page.find('div', class_ = 'critic-score meter').find_next('span', class_ = 'meter-value superPageFontColor').text.encode('ascii', 'ignore')
            #tomatoes_user_rating = tomatoes_page.find('div', class_ = 'audience-score meter').find_next('span', class_ = 'superPageFontColor').text.encode('ascii', 'ignore')
            tomatoes_critic_rating = '0%'
            tomatoes_user_rating = '0%'
            
            # Metacritic rating
            metacritic_rating = page_html.find('div', class_ = 'titleReviewBarItem').find_next('span').text.encode('ascii', 'ignore')
            if (' ' in metacritic_rating):
                metacritic_rating = 'Unrated'
                metacritic_rating_val = 'Unrated'
            else:
                metacritic_rating_val = int(metacritic_rating)
            
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
            oscar_wins = str(oscar_wins)
            oscar_noms = str(oscar_noms)
            
            # updates the global movie sets for sorting
            if (seen == False):  
                unseen_movie_data = OrderedDict([("name", name), ("release_year", int(release_year)), ("runtime", total_min), ("box_office", box_office_val), ("genres", genres), ("actors", actors), ("directors", directors), ("writers", writers), ("imdb_rating", float(imdb_rating)), ("num_imdb_ratings", num_ratings_val), ("imdb_popularity", popularity_val), ("tomatoes_critic_rating", tomatoes_critic_rating), ("tomatoes_user_rating", tomatoes_user_rating), ("metacritic_rating", metacritic_rating_val), ("oscar_wins", int(oscar_wins)), ("oscar_noms", int(oscar_noms)), ("url", url)])
                self.unseen_movies_list.append(unseen_movie_data)
            
            # adds a Movie Vertex to the graph
            if (seen == True):
                print('ADDING SEEN MOVIE: \'' + name + '\'')
            else:
                print('ADDING UNSEEN MOVIE: \'' + name + '\'')
            vertex = Vertex([name, release_year, runtime, box_office, genres, actors, directors, writers, user_rating, imdb_rating, num_imdb_ratings, imdb_popularity, imdb_related_movies, tomatoes_critic_rating, tomatoes_user_rating, metacritic_rating, oscar_wins, oscar_noms, url, seen])
            self.g.add_vertex(vertex)
            
            # updates counters
            scraped_movies += 1
            index += 1
    
            # goes to the next page of the user's ratings
            if (seen == True) and (scraped_movies % 100 == 0) and (scraped_movies != num_movies):
                start_page_html = self.get_html("http://www.imdb.com" + start_page_html.find('a', class_ = 'flat-button lister-page-next next-page').get('href').encode('ascii', 'ignore'))
                index = 0
                anchor_page = start_page_html.find_all('h3', class_ = 'lister-item-header')
        
        # removes all the user's rated movies from the unseen movies set and sorts it
        if (seen == True):
            print('Added ' + str(self.g.total_seen_movies) + ' seen movies to the graph (skipped ' + str(num_movies - self.g.total_seen_movies) + ')')
            logging.info("Scraped the user's rated movies")
            unseen_movies_copy = self.g.unseen_movies.copy()
            for (n, l) in unseen_movies_copy:
                if (n in self.g.seen_movie_names) or (l in self.g.seen_movie_links):
                    self.g.unseen_movie_names.remove(n)
                    self.g.unseen_movie_links.remove(l)
                    self.g.unseen_movies.remove((n, l))
            
            imdb_ratings_threshold = np.array(seen_imdb_ratings)
            imdb_ratings_threshold = round(abs(np.mean(seen_imdb_ratings) - (2 * np.std(seen_imdb_ratings))), 1)
            #box_office_threshold = np.array(seen_box_office)
            #box_office_threshold = round(abs(np.mean(seen_box_office) - (2 * np.std(seen_box_office))), 1)
            
            print('IMDb Ratings Threshold: ' + str(imdb_ratings_threshold) + '\n')
            #print('Box Office Threshold: ' + str(box_office_threshold))
            self.get_movie_data(self.g.unseen_movies, len(self.g.unseen_movies), imdb_ratings_threshold, False)        
        else:
            print('Added ' + str(self.g.total_unseen_movies) + ' unseen movies to the graph (skipped ' + str(num_movies - self.g.total_unseen_movies) + ')')
            logging.info("Scraped the user's unseen movies")
            
            # stores the complete graph data in a JSON file
            with open('movie_data.json', 'w') as fp:
                logging.info("Logging unseen movie data...")
                json.dump(self.unseen_movies_list, fp, indent = 4) 
            
            # sorts the unseen movie set
            #sorted_unseen_by_year = list(unseen_movies_list)
            #sorted_unseen_by_year = sorted(sorted_unseen_by_year, key = lambda unseen_movies_list: unseen_movies_list[1], reverse = True)
            #sorted_unseen_by_runtime = list(unseen_movies_list)
            #sorted_unseen_by_runtime = sorted(sorted_unseen_by_runtime, key = lambda unseen_movies_list: unseen_movies_list[2], reverse = True)
            #sorted_unseen_by_box_office = list(unseen_movies_list)
            #sorted_unseen_by_box_office = sorted(sorted_unseen_by_box_office, key = lambda unseen_movies_list: unseen_movies_list[3], reverse = True)
            #sorted_unseen_by_imdb_rating = list(unseen_movies_list)
            #sorted_unseen_by_imdb_rating = sorted(sorted_unseen_by_imdb_rating, key = lambda unseen_movies_list: unseen_movies_list[4], reverse = True)
            
            #print(sorted_unseen_by_imdb_rating)
            #print(sorted_unseen_by_box_office)
            #query.get_query(g, sorted_unseen_by_year, sorted_unseen_by_runtime, sorted_unseen_by_box_office, sorted_unseen_by_imdb_rating)
            
    # helper function that gets the html code from a given 'url'
    def get_html(self, url):
        if ("www.imdb.com" in url) or ("www.rottentomatoes.com" in url):
            page = requests.get(url)
            page_data = page.text
            html = BeautifulSoup(page_data, "html.parser")
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
            
            release_year = str(elem['release_year']).encode('ascii', 'ignore')
            
            runtime = self.parse_runtime(elem['runtime'])
            
            box_office = self.parse_long_int(elem['box_office'], True)
            
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
            
            imdb_rating = str(elem['imdb_rating']).encode('ascii', 'ignore')
            
            num_imdb_ratings = self.parse_long_int(elem['num_imdb_ratings'], False)
            
            imdb_popularity = self.parse_long_int(elem['imdb_popularity'], False)
            
            imdb_related_movies = 'None'
            
            tomatoes_critic_rating = '0%'
            tomatoes_user_rating = '0%'
            
            metacritic_rating = str(elem['metacritic_rating']).encode('ascii', 'ignore')
            
            oscar_wins = str(elem['oscar_wins']).encode('ascii', 'ignore')
            oscar_noms = str(elem['oscar_noms']).encode('ascii', 'ignore')
            
            url = elem['url'].encode('ascii', 'ignore')
            
            print('ADDING UNSEEN MOVIE: \'' + name + '\'')
            vertex = Vertex([name, release_year, runtime, box_office, genres, actors, directors, writers, user_rating, imdb_rating, num_imdb_ratings, imdb_popularity, imdb_related_movies, tomatoes_critic_rating, tomatoes_user_rating, metacritic_rating, oscar_wins, oscar_noms, url, False])
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

