from bs4 import BeautifulSoup
import requests
import re
import asyncio
import urllib


base_url = 'https://www.imdb.com'
check_lists = ['(TV Series)', '(Short)', '(Video Game)', '(Video short)', '(Video)', '(TV Movie)', 
               '(TV Mini-Series)', '(TV Series short)', '(TV Special)', '(TV Movie documentary)']

def get_cast_page_soup(url):
    try:
        response = requests.get(url)
        if not response.status_code // 100 == 2:
            return f"Error: Response is not successful. {response}"
        soup = BeautifulSoup(response.text)
        return soup
    except requests.exceptions.HTTPError as e:
        return f"Error: {e}"

def get_actor_page_soup(url):
    try:
        response = requests.get(url)
        if not response.status_code // 100 == 2:
            return f"Error: Response is not successful. {response}"
        else:
            soup = BeautifulSoup(response.text)
            return soup
    except requests.exceptions.HTTPError as e:
        return f"Error: {e}"

async def fetch(session, url, sem):
    async with sem:
        async with session.get(url) as response:
            return await response.text()

def get_lists(table):
    lists = []  

    if table is None:
        return []
    else:
        for row in table:
            if row.find('b'):
                text = row.find('b').next_sibling
                text = text.replace(r"\n{2,}","\n")
                text = text.strip()
                text_arr = re.findall(r'\(.+?\)|".+?"|\w+' , text)
                links = row.findAll('a')
                movie_name = row.find('a').text
                movie_url = row.find('a').get('href')
                full_movie_url = base_url + movie_url

                if len(links) == 1:
                    if len(text_arr) > 1:
                        text_to_check = text_arr[0]
                        if text_to_check not in check_lists:
                            lists.append((movie_name, full_movie_url))
                    elif len(text_arr) == 1:
                        text_to_check = text_arr[0]
                        if text_to_check not in check_lists:
                            lists.append((movie_name, full_movie_url))
                    else:
                        lists.append((movie_name, full_movie_url)) 
            
        return lists

def get_movie_credits_urls(current_movies):
    return [urllib.parse.urljoin(current_movie, 'fullcredits') for current_movie in current_movies]

def url_processing(url):
    return url.replace(r'/^https:\/\/www./', '')
