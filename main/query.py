from __future__ import print_function
import matplotlib.pyplot as plt
import numpy as np
import logging

# main query function to run after crawling is finished 
def get_query(g, sorted_unseen_by_year, sorted_unseen_by_runtime, sorted_unseen_by_box_office, sorted_unseen_by_imdb_rating):
    query = raw_input("Query commands:\n1 = List the unseen movies with the highest IMDb rating\n2 = List the unseen movies with the highest box office value\n3 = List the unseen movies with the shortest runtime\n4 = List the unseen movies with the longest runtime\n5 = List the oldest unseen movies\n6 = List the newest unseen movies\n\nEnter a query command number: ")
            
    # query function 1
    if (query == '1'):
        num = raw_input("Enter a number '#' to find out the '#' unseen movies with the highest IMDb rating: ")
        num = int(num)
        if (num > 0) and (num <= g.total_unseen_movies):
            print("The " + str(num) + " unseen movies with the highest IMDb rating are")
            names = list()
            floats = list()
            strings = list()
            for i in range(num):
                data = sorted_unseen_by_imdb_rating[i]
                names.append(data[0])
                floats.append(data[4])
                strings.append(str(data[4]))
                print(str(i + 1) + ". " + data[0] + " (IMDb rating: " + str(data[4]) + ")")
            
            # plotting the values
            xticks = np.arange(1, num + 1)
            xnames = list()              
            plt.bar(xticks, floats, align = 'center', color = 'b')
            for i in range(num):
                name = names[i]
                lines = name.split(' ')
                name = ''
                index = 0
                while (index < len(lines)):
                    if (index < (len(lines) - 1)):
                        if ((len(lines[index]) + len(lines[index + 1])) > 6):
                            name += (lines[index] + '\n')
                            index += 1
                        else:
                            name += (lines[index] + ' ' + lines[index + 1] + '\n')
                            index += 2
                    else:
                        name += lines[index]
                        index += 1
                xnames.append(name)
                plt.annotate(strings[i], (xticks[i] - 0.35, floats[i] + 0.1), fontweight = 'bold')
            plt.xticks(xticks, xnames)
            plt.ylabel('IMDb Rating')
            plt.title('Unseen Movies with the Highest IMDb Ratings')
            plt.show()
            
            print()
            logging.info("Query completed (command 1)")
        elif (num > g.total_unseen_movies):
            print("I'm sorry, we did not scrape that many unseen movie pages\n")
            logging.warning("Query could not be completed, not enough unseen movie pages")
        else:
            print("I'm sorry, that is a invalid number\n")
            logging.warning("Query could not be completed, invalid number provided")
        
    get_query(g, sorted_unseen_by_year, sorted_unseen_by_runtime, sorted_unseen_by_box_office, sorted_unseen_by_imdb_rating)
        