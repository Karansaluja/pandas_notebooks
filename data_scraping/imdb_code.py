from bs4 import BeautifulSoup
import requests
import re
import asyncio
import aiohttp
import urllib
import time

from imdb_helper_functions import get_lists, get_cast_page_soup, get_actor_page_soup, get_movie_credits_urls, fetch, url_processing

base_url = 'https://www.imdb.com'
actors = {
    'Dwayne Johnson': 'https://www.imdb.com/name/nm0425005/', 
    'Chris Hemsworth': 'https://www.imdb.com/name/nm1165110/', 
    'Robert Downey Jr.': 'https://www.imdb.com/name/nm0000375/',
    'Akshay Kumar': 'https://www.imdb.com/name/nm0474774/', 
    'Jackie Chan': 'https://www.imdb.com/name/nm0000329/', 
    'Bradley Cooper': 'https://www.imdb.com/name/nm0177896/', 
    'Adam Sandler': 'https://www.imdb.com/name/nm0001191/',
    'Scarlett Johansson': 'https://www.imdb.com/name/nm0424060/', 
    'Sofia Vergara': 'https://www.imdb.com/name/nm0005527/' ,
    'Chris Evans': 'https://www.imdb.com/name/nm0262635/'
}

def get_actors_by_movie_soup(cast_page_soup, num_of_actors_limit = None):
    try:
        actor_table = cast_page_soup.find('table', class_ ='cast_list')

        actor_lists = []

        if actor_table:
            for row in actor_table.findAll('tr')[1:]:
                columns = row.findAll('td')
                if len(columns) > 1:
                    actor_info = row.findAll('td')[1]
                    actor_url = actor_info.find('a').get('href')
                    full_actor_url = base_url + f"{actor_url}"
                    actor_name = actor_info.find('a').getText().strip('\n').lstrip().rstrip('\r')

                    actor_lists.append((actor_name, full_actor_url))
        
        if num_of_actors_limit:
            return actor_lists[:num_of_actors_limit]

        return actor_lists
    except(TypeError, KeyError,AttributeError) as e:
        print(f"Error: {e}")

def get_movies_by_actor_soup(actor_page_soup, num_of_movies_limit = None):
    try:
        movie_table = actor_page_soup.findAll('div', id=re.compile('^actor-|^actress-'))
        movie_lists = get_lists(movie_table)

        if num_of_movies_limit:
            return movie_lists[:num_of_movies_limit]
        
        return movie_lists
    except(TypeError, KeyError, AttributeError) as e:
        print(f"Error: {e}")

async def get_movie_distance(actor_start, actor_end, session, num_of_actors_limit = None, num_of_movies_limit = None):
    actor_start_url = actors[actor_start]
    start_actor_soup = get_actor_page_soup(actor_start_url)
    start_movie_lists = [movie_url for (_, movie_url) in get_movies_by_actor_soup(start_actor_soup, num_of_movies_limit)]
    start_movie_credit_lists = get_movie_credits_urls(start_movie_lists)

    current_distance = 1

    sem = asyncio.Semaphore(20)

    while True:
        actors_to_check = []
        movies_to_check = []

        #actors_list_url for each movie
        coroutines_movie_credits = [fetch(session, url, sem) for url in start_movie_credit_lists]
        current_movies_credit_responses = await asyncio.gather(*coroutines_movie_credits)

        #actor_lists for each movie, get_actors_by_movie_soup
        for current_movies_credit_response in current_movies_credit_responses:
            actors_to_check+=get_actors_by_movie_soup(BeautifulSoup(current_movies_credit_response), num_of_actors_limit)
                
        actors_to_check = list(dict.fromkeys(actors_to_check))

        for actor_name, _ in actors_to_check:
            if actor_name == actor_end:
                print('complete')
                print(actor_start, actor_end, current_distance)
                time.sleep(10)
                return current_distance
                
        current_distance += 1

        if current_distance > 2:
            return 'infinite'

        coroutines_actors = [fetch(session, url, sem) for (_, url) in actors_to_check]
        current_actors_responses = await asyncio.gather(*coroutines_actors)

        print(current_distance)

        for current_actor_response in current_actors_responses:
            movies_to_check += get_movies_by_actor_soup(BeautifulSoup(current_actor_response), num_of_movies_limit)
            
        movies_to_check = list(dict.fromkeys(movies_to_check))
        start_movie_credit_lists = [url_processing(url) for (_, url) in movies_to_check]

async def get_movie_distance_bi(actor_start, actor_end, session, num_of_actors_limit = None, num_of_movies_limit = None):
    actor_start_url = actors[actor_start]
    start_actor_soup = get_actor_page_soup(actor_start_url)
    start_movie_lists = [movie_url for (_, movie_url) in get_movies_by_actor_soup(start_actor_soup)]
    start_movie_credit_lists = get_movie_credits_urls(start_movie_lists)

    actor_end_url = actors[actor_end]
    end_actor_soup = get_actor_page_soup(actor_end_url)
    end_movie_lists = [movie_url for (_, movie_url) in get_movies_by_actor_soup(end_actor_soup)]
    end_movie_credit_lists = get_movie_credits_urls(end_movie_lists)

    current_distance = 1

    sem = asyncio.Semaphore(20)

    while True:
        actors_to_check = []
        actors_from_check = []

        #actors_list_url for each movie
        coroutines_movie_credits = [fetch(session, url, sem) for url in start_movie_credit_lists]
        current_movies_credit_responses = await asyncio.gather(*coroutines_movie_credits)

        #actor_lists for each movie, get_actors_by_movie_soup
        for current_movies_credit_response in current_movies_credit_responses:
            actors_to_check+=get_actors_by_movie_soup(BeautifulSoup(current_movies_credit_response), num_of_actors_limit)
                
        actors_to_check = list(dict.fromkeys(actors_to_check))

        for actor_name, _ in actors_to_check:
            if actor_name == actor_end:
                print('complete')
                print(actor_start, actor_end, current_distance)
                time.sleep(10)
                return current_distance
        

        coroutines_movie_credits_end = [fetch(session, url, sem) for url in end_movie_credit_lists]
        end_current_movies_credit_responses = await asyncio.gather(*coroutines_movie_credits_end)

        #actor_lists for each movie, get_actors_by_movie_soup
        for end_current_movies_credit_response in end_current_movies_credit_responses:
            actors_from_check+=get_actors_by_movie_soup(BeautifulSoup(end_current_movies_credit_response), num_of_actors_limit)
                
        actors_from_check = list(dict.fromkeys(actors_from_check))
        current_distance += 1

        for actor_name, _ in actors_from_check:
            for actor_name_start, _ in actors_to_check:
                if actor_name == actor_name_start:
                    print('complete')
                    print(actor_start, actor_end, current_distance)
                    time.sleep(10)
                    return current_distance
        
        current_distance += 1

        if current_distance > 2:
            return 'infinite'
    
def get_movie_descriptions_by_actor_soup(actor_page_soup, num_of_movies = None):
    try:
        movies_lists = get_movies_by_actor_soup(actor_page_soup, num_of_movies)
        
        texts = ''
        for _, movie_url in movies_lists:
            movie = get_actor_page_soup(movie_url)
            plot_summary = movie.find('div', id= 'titleStoryLine')
            if plot_summary:
                plot_summary_paragraph = plot_summary.find('p')
                if plot_summary_paragraph:
                    text = plot_summary_paragraph.getText().strip('\n').lstrip().rstrip().split('\n')[0]
                    texts += text
        
        return texts
    except(TypeError, KeyError, AttributeError) as e:
        print(f"Error: {e}")
        



    