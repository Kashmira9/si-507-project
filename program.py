from bs4 import BeautifulSoup
import requests
import json
import secret
import sqlite3
import plotly.graph_objs as go
import plotly
from plotly.subplots import make_subplots
from plotly.offline import plot 
from flask import Flask, render_template, Markup

# from openpyxl import load_workbook
import plotly.figure_factory as ff
import webbrowser
import csv
import time

import pandas as pd
import plotly.express as px
# from datetime import datetime
# import matplotlib.pyplot as plt

DB_NAME = 'final_project.sqlite'
API_KEY = secret.API_KEY
HEADERS = {'Authorization': 'Bearer {}'.format(API_KEY),
           'User-Agent': 'UMSI 507 Course Project - Python Scraping',
           'From': 'ksawant@umich.edu',
}

app = Flask(__name__)


#########################################
################ Class ##################x
#########################################

class City:
    '''deifinition of the class city

    Instance Attributes
    -------------------
    id_pos: int
        the id(position) of the city instance in the data
    name: string
        the name of the city instance
    state: string
        the state name that the city is located at
    population: int
        the population of the city
    area: float
        the area of the city in Square mile
    latitude: string
        the latitude of the city center
    longitude: string
        the longitude of the city center
    
    '''
    def __init__(self, id_pos=0, name=None, state=None, population=0, area=0, latitude='', longitude=''):
        self.id_pos = id_pos
        self.name = name
        self.state = state
        self.population = population
        self.area = area
        self.latitude = latitude
        self.longitude = longitude

class Restaurant:
    '''definition of the class restaurant

     Instance Attributes
    -------------------
    rating: int
        the rating for the restaurant in the range [0, 5]
    price: int
        the rating for the restaurant in the range [1, 3]
    phone: string
        the phone number for the restaurant
    category: string
        the category that the restaurant belong to
    yelp_id: string
        the unique identifer for the restaurant
    url: string
        the website for the restaurant on Yelp
    review_num: int
        the number of reviews of the restaurant
    name: string
        the official name of the restaurant
    city: string
        the city name that the restaurant located at
    state: string
        the state name that the restaurant is located at
    city_id: int
        the id of the city in the table "cities"
    '''
    def __init__(self, rating=0, price=None, phone='', category='', yelp_id='', url='', 
                 review_num=0, name='', city='', state='', city_id = 0):
        self.rating = rating
        self.price = price
        self.phone = phone
        self.category = category
        self.yelp_id = yelp_id
        self.url = url
        self.review_num = review_num
        self.name = name
        self.city = city
        self.state = state
        self.city_id = city_id

#########################################
############### Caching #################
#########################################

def load_cache(cache_file_name):
    '''Load response text cache if already generated, else initiate an empty dictionary.
    
    Parameters
    ----------
    None
    
    Returns
    -------
    cache: dictionary
        The dictionary which maps url to response text.
    '''
    try:
        cache_file = open(cache_file_name, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache

def save_cache(cache, cache_file_name):
    '''Save the cache
    
    Parameters
    ----------
    cache: dictionary
        The dictionary which maps url to response.
    
    Returns
    -------
    None
    '''
    cache_file = open(cache_file_name, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()

CACHE_FILE = 'cache.json'
CACHE_DICT = load_cache(CACHE_FILE)

    


#########################################
########### Data Processing #############
#########################################

def db_create_table_cities():
    ''' create the table named "Cities" in the database
    
    Parameters
    ----------
    None
    
    Returns
    -------
    none
    '''
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    # drop_cities_sql = 'DROP TABLE IF EXISTS "Cities"'
    create_cities_sql = '''
        CREATE TABLE IF NOT EXISTS "Cities" (
            "Id" INTEGER PRIMARY KEY UNIQUE, 
            "Name" TEXT NOT NULL,
            "State" TEXT NOT NULL, 
            "Population" INTEGER NOT NULL,
            "Area" REAL NOT NULL,
            "Latitude" TEXT NOT NULL,
            "Longitude" TEXT NOT NULL
        )
    '''
    # cur.execute(drop_cities_sql)
    cur.execute(create_cities_sql)
    conn.commit()
    conn.close()

def db_create_table_restaurants():
    ''' create the table named "Restaurants" in the database
    
    Parameters
    ----------
    None
    
    Returns
    -------
    none
    '''
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    # drop_restaurants_sql = 'DROP TABLE IF EXISTS "Restaurants"'
    create_restaurants_sql = '''
        CREATE TABLE IF NOT EXISTS "Restaurants" (
            "Id" INTEGER PRIMARY KEY AUTOINCREMENT, 
            "Name" TEXT NOT NULL UNIQUE,
            "City_id" INTEGER NOT NULL,
            "City" TEXT NOT NULL,
            "State" TEXT NOT NULL,
            "Rating" INTEGER,
            "Price" INTEGER,
            "Category" TEXT,
            "Phone" TEXT,
            "Yelp_id" TEXT NOT NULL UNIQUE,
            "Url" TEXT,
            "Number of Review" INTEGER
        )
    '''
    # cur.execute(drop_restaurants_sql)
    cur.execute(create_restaurants_sql)
    conn.commit()
    conn.close()

def db_write_table_cities(city_instances):
    ''' write data into the table "Cities" in the database
    
    Parameters
    ----------
    city_instances: list
        a list of city instances
    
    Returns
    -------
    none
    '''
    insert_cities_sql = '''
        INSERT OR IGNORE INTO Cities
        VALUES (?, ?, ?, ?, ?, ?, ?)
    '''
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    for c in city_instances:
        cur.execute(insert_cities_sql, 
                        [c.id_pos, c.name, c.state, c.population, c.area, c.latitude, c.longitude])
    
    conn.commit()
    conn.close()

def db_write_table_restaurants(restaurant_instances):
    ''' write data into the table "Restaurants" in the database
    
    Parameters
    ----------
    restaurant_instances: list
        a list of restaurant instances
    
    Returns
    -------
    none
    '''
    insert_restaurants_sql = '''
        INSERT OR IGNORE INTO Restaurants
        VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    for r in restaurant_instances:
        cur.execute(insert_restaurants_sql,
            [r.name, r.city_id, r.city, r.state, r.rating, r.price, r.category, r.phone, r.yelp_id, r.url, r.review_num]
        )
    
    conn.commit()
    conn.close()

def build_city_instance():
    ''' function that scrapes the wikpedia page and build city instances 
    
    Parameters
    ----------
    none
    
    Returns
    -------
    city_instances: list
        a list of 314 different city instances
    '''
    # CACHE_DICT = load_cache(CACHE_FILE)
    city_instances = []
    site_url = 'https://en.wikipedia.org/wiki/List_of_United_States_cities_by_population'
    url_text = make_url_request_using_cache(url_or_uniqkey=site_url)
    soup = BeautifulSoup(url_text, 'html.parser')
    tr_list = soup.find('table', class_='wikitable sortable').find('tbody').find_all('tr')[1:] # total 314 cities in the list, each in a row
    for tr in tr_list: # each tr is a city row, td is the data in each column
        td_list = tr.find_all('td')
        id_pos = int(td_list[0].text.strip())
        name = str(td_list[1].find('a').text.strip())
        try:
            state = str(td_list[2].find('a').text.strip())
        except:
            state = td_list[2].text.strip()
        population = int(td_list[4].text.strip().replace(',', ''))
        area = float(td_list[6].text.strip().split('\xa0')[0].replace(',', ''))
        lati_longi = td_list[10].find('span', class_='geo-dec').text.strip().split(' ')
        latitude = str(lati_longi[0])
        longitude = str(lati_longi[1])
        instance = City(id_pos=id_pos, name=name, state=state, population=population, 
                        area=area, latitude=latitude, longitude=longitude
        )
        city_instances.append(instance)
    
    return city_instances


def build_restaurant_instance(city_instances):
    ''' function that searches restaurant in different cities
        according to the city_instances list from the Yelp Fusion API 
    
    Parameters
    ----------
    city_instances: list
        a list of 314 different city instances
    
    Returns
    -------
    restaurant_instances: list
        a list of thousands of different restaurant instances
    '''
    # CACHE_DICT = load_cache(CACHE_FILE)
    restaurant_instances = []
    endpoint_url = 'https://api.yelp.com/v3/businesses/search'
    for c in city_instances:
        city = c.name
        params = {'location': city + ',' + c.state , 'term': 'restaurants', 'limit': 50}
        uniqkey = construct_unique_key(endpoint_url, params)
        results = make_url_request_using_cache(url_or_uniqkey=uniqkey, params=params)
        if 'businesses' in results.keys():
            for business in results['businesses']:
                rating = business['rating']
                try:
                    price = len(business['price'].strip())
                except:
                    price = None
                phone = business['display_phone']
                try:
                    category = business['categories'][0]['title']
                except:
                    category = ''
                yelp_id = business['id']
                url = business['url']
                review_num = business['review_count']
                name = business['name']
                state = business['location']['state']
                instance = Restaurant(rating=rating, price=price, phone=phone, category=category, yelp_id=yelp_id, 
                                      url=url, review_num=review_num, name=name, city=city, state=state, city_id=c.id_pos)
                restaurant_instances.append(instance)
    
    return restaurant_instances
    


def construct_unique_key(baseurl, params):
    ''' constructs a key that is guaranteed to uniquely and 
    repeatably identify an API request by its baseurl and params

    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dictionary
        A dictionary of param: param_value pairs

    Returns
    -------
    string
        the unique key as a string
    '''
    param_strings = []
    connector = '_'
    for k in params.keys():
        param_strings.append(f'{k}_{params[k]}')
    
    param_strings.sort()
    unique_key = baseurl + connector + connector.join(param_strings)
    return unique_key

def make_url_request_using_cache(url_or_uniqkey, params=None):
    '''Given a url, fetch if cache not exist, else use the cache.
    
    Parameters
    ----------
    url: string
        The URL for a specific web page
    cache_dict: dictionary
        The dictionary which maps url to response text
    params: dictionary
        A dictionary of param: param_value pairs
    
    Returns
    -------
    cache[url]: response
    '''
    if url_or_uniqkey in CACHE_DICT.keys():
        print('Using cache')
        return CACHE_DICT[url_or_uniqkey]

    print('Fetching')
    if params == None: # dictionary: url -> response.text
        # time.sleep(1)
        response = requests.get(url_or_uniqkey, headers=HEADERS)
        CACHE_DICT[url_or_uniqkey] = response.text
    else: # dictionary: uniqkey -> response.json()
        endpoint_url = 'https://api.yelp.com/v3/businesses/search'
        response = requests.get(endpoint_url, headers = HEADERS, params=params)
        CACHE_DICT[url_or_uniqkey] = response.json()
    
    save_cache(CACHE_DICT, CACHE_FILE)
    return CACHE_DICT[url_or_uniqkey]

def build_database():
    '''initialize and create the database according to the city instances 
       and restaurant instances (either fetch or use cache)
    
    Parameters
    ----------
    none
    
    Returns
    -------
    none
    '''
    print('Building database...')
    city_instances = build_city_instance()
    db_create_table_cities()
    db_write_table_cities(city_instances)
    restaurant_instances = build_restaurant_instance(city_instances)
    db_create_table_restaurants()
    db_write_table_restaurants(restaurant_instances)
    print('Finished building database!')

def searchDB(query):
    '''Search the database and return the results given the sqlite query
    
    Parameters
    ----------
    query: string 
        a sqlite query command
    
    Returns
    -------
    result: list
        a list of tuples that contains the results
    '''
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    result = cursor.execute(query).fetchall()
    connection.close()
    return result



#########################################
########### Data Presentation ###########
#########################################

def process_name(city_name):
    '''process the input name in order to make it compatible with the database
    (e.g., change the name "new york" into "New York")
    
    Parameters
    ----------
    city_name: string
        the name of the city before formatting
    
    Returns
    -------
    city_name: string
        the name of the city after formatting
    '''
    split = city_name.split(' ')
    res = ''
    for word in split:
        if word == 'of':
            res += word.lower() + ' '
        else:
            res += word.lower().capitalize() + ' '
    return res.strip()

def get_avg_and_sort(results):
    '''given a query search results, return the average value for the given category
       and sort the results in descending order
    
    Parameters
    ----------
    resutls: list of tuples
        the query search returned by the database
    
    Returns
    -------
    xvals: list
        the name of the attribute
    yvals: list
        the average value for the corresponding attribute
    '''
    # result is the list of tuples returned by database query. The tuple must be length of 2!
    dict_rating = {}
    for row in results:
        data0 = row[0]
        data1 = float(row[1])
        if data0 in dict_rating.keys():
            dict_rating[data0].append(data1)
        else:
            temp = []
            temp.append(data1)
            dict_rating[data0] = temp

    dict_avg = {}
    for key, value in dict_rating.items():
        total = 0
        for val in value:
            total += val
        avg = float(total / len(value))
        dict_avg[key] = avg

    sorted_dict = sorted(dict_avg.items(), key=lambda x:x[1], reverse=True)
    xvals = []
    yvals = []
    for i in range(len(sorted_dict)):
        xvals.append(sorted_dict[i][0])
        yvals.append(sorted_dict[i][1])

    return xvals, yvals

def flask_plot(xvals, yvals, titles, fig_types):
    ''' this function generetes either bar chart or pie chart 
        and return the plot that is used for displaying in
        the html webpage

    Parammeters
    -----------
    xvals: list
        a list of x values
    yvals: list
        a list of y values that correspond to the x values
    title: string
        the title of the plot
    fig_type: string
        either "bar" or "pie" that defines the output plot type

    Returns
    --------
    fig_div: string
        the plot that is readable by html files
    '''
    idxs = [[1, 1], [1, 2], [1, 3], [1, 4], [2, 1], [2, 2], [2, 3]]
    figure_types = [
        [{'type': 'pie'}, {'type': 'pie'}, {'type': 'pie'}, {'type': 'bar'}], 
        [{'type': 'bar'}, {'type': 'bar'}, {'type': 'bar'}, {'type': 'bar'}]
    ]
    assert len(xvals) == len(yvals) == len(titles) == len(fig_types) == len(idxs)

    fig = make_subplots(rows=2, cols=4, specs=figure_types, subplot_titles=(titles))

    for xval, yval, title, fig_type, idx in zip(xvals, yvals, titles, fig_types, idxs):
        if fig_type == 'pie':
            fig.add_trace(go.Pie(labels=xval, values=yval), row=idx[0], col=idx[1])
            fig.update_traces(hole=.4, hoverinfo="label+percent+name", row=idx[0], col=idx[1])
        elif fig_type == 'bar':
            fig.add_trace(go.Bar(x=xval, y=yval), row=idx[0], col=idx[1])
    
    fig.update_layout(width=1600, height=800, annotations=[dict(font_size=10, showarrow=False)])
    fig.update_annotations(font=dict(size=10))
    fig.for_each_xaxis(lambda axis: axis.title.update(font=dict(size=10)))

    for i in fig['layout']['annotations']:
        i['font'] = dict(size=10)
    fig_div = plot(fig, output_type="div")
    return fig_div


########## plots for cities or states ############

def pieplot_restaurant_categories(name, target):
    ''' a function that generate a pieplot for the percentage
        of each restaurant category in the city or state specified 

    Parameters
    ----------
    name: string
        a city name or a state name
    target: string
        indicates the name is a city or a state
    id_pos: int
        the id that uniquely identify a city

    Returns
    -------
    string
        the plot that is readable by html files
    '''
    name = process_name(name)
    query = '''SELECT r.Category FROM Restaurants as r
                JOIN Cities as c ON c.Id=r.City_id'''
    if target == 'city':
        query += ''' WHERE r.City="{}"'''.format(name)
    elif target == 'state':
        query += ''' WHERE c.State="{}"'''.format(name)
    
    results = searchDB(query)
    dict_category = {}
    for row in results:
        category = row[0]
        if category in dict_category.keys():
            dict_category[category] += 1
        else:
            dict_category[category] = 1
    
    sorted_list = sorted(dict_category.items(), key=lambda x:x[1], reverse=True)
    labels = []
    values = []
    for row in sorted_list[:3]:
        labels.append(row[0])
        values.append(row[1])
    
    others_num = 0
    for row in sorted_list[3:]:
        others_num += row[1]
    
    labels.append('Others')
    values.append(others_num)
    title = '''Popular Restaurant Types in {} {}'''.format(name, target.capitalize())
    return labels, values, title, 'pie'

def pieplot_rating(name, target):
    ''' a function that generate a pieplot for the percentage
        of ratings of the restaurants in the city or state specified 

    Parameters
    ----------
    name: string
        a city name or a state name
    target: string
        indicates the name is a city or a state
    id_pos: int
        the id that uniquely identify a city

    Returns
    -------
    string
        the plot that is readable by html files
    '''
    name = process_name(name)
    query = '''SELECT r.Rating FROM Restaurants as r
                JOIN Cities as c ON c.Id=r.City_id'''
    if target == 'city':
        query += ''' WHERE r.City="{}"'''.format(name)
    elif target == 'state':
        query += ''' WHERE c.State="{}"'''.format(name)
    
    results = searchDB(query)
    dict_rating = {}
    for row in results:
        rating = float(row[0])
        if rating in dict_rating.keys():
            dict_rating[rating] += 1
        else:
            dict_rating[rating] = 1
    
    labels = list(dict_rating.keys())
    values = list(dict_rating.values())
    title = 'Restaurant Rating Percentage in {} {}'.format(name, target.capitalize())
    return labels, values, title, 'pie'

def pieplot_price(name, target):
    ''' a function that generate a pieplot for the percentage
        of prices of the restaurants in the city or state specified 

    Parameters
    ----------
    name: string
        a city name or a state name
    target: string
        indicates the name is a city or a state
    id_pos: int
        the id that uniquely identify a city

    Returns
    -------
    string
        the plot that is readable by html files
    '''
    name = process_name(name)
    query = '''SELECT r.Price FROM Restaurants as r
                JOIN Cities as c ON c.Id=r.City_id'''
    if target == 'city':
        query += ''' WHERE r.City="{}" AND r.Price NOTNULL'''.format(name)
    elif target == 'state':
        query += ''' WHERE c.State="{}" AND r.Price NOTNULL'''.format(name)
    
    results = searchDB(query)
    dict_price = {}
    for row in results:
        price = int(row[0])
        if price in dict_price.keys():
            dict_price[price] += 1
        else:
            dict_price[price] = 1
    
    labels = list(dict_price.keys())
    values = list(dict_price.values())
    title = 'Restaurant Price Percentage in {} {}'.format(name, target.capitalize())
    return labels, values, title, 'pie'

def barplot_avgrating_each_category(name, target):
    ''' a function that generate a barplot for the average rating 
        of differnt restaurant types in the city or state specified 

    Parameters
    ----------
    name: string
        a city name or a state name
    target: string
        indicates the name is a city or a state
    id_pos: int
        the id that uniquely identify a city

    Returns
    -------
    string
        the plot that is readable by html files
    '''
    name = process_name(name)
    query = '''SELECT r.Category, r.Rating FROM Restaurants as r
                JOIN Cities as c ON c.Id=r.City_id'''
    if target == 'city':
        query += ''' WHERE r.City="{}"'''.format(name)
    elif target == 'state':
        query += ''' WHERE c.State="{}"'''.format(name)
    
    results = searchDB(query)
    xvals, yvals = get_avg_and_sort(results)
    title = 'Average Rating of Restaurants By Category in {} {}'.format(name, target.capitalize())
    return xvals, yvals, title, 'bar'

def barplot_avgprice_each_category(name, target):
    ''' a function that generate a barplot for the average price 
        of differnt restaurant types in the city or state specified 

    Parameters
    ----------
    name: string
        a city name or a state name
    target: string
        indicates the name is a city or a state
    id_pos: int
        the id that uniquely identify a city

    Returns
    -------
    string
        the plot that is readable by html files
    '''
    name = process_name(name)
    query = '''SELECT r.Category, r.Price FROM Restaurants as r
                JOIN Cities as c ON c.Id=r.City_id'''
    if target == 'city':
        query += ''' WHERE r.City="{}" AND r.Price NOTNULL'''.format(name)
    elif target == 'state':
        query += ''' WHERE c.State="{}" AND r.Price NOTNULL'''.format(name)
    
    results = searchDB(query)
    xvals, yvals = get_avg_and_sort(results)
    title = 'Average Price of Restaurants By Category in {} {}'.format(name, target.capitalize())
    return xvals, yvals, title, 'bar'
  
def barplot_avgreview_each_category(name, target):
    ''' a function that generate a barplot for the average number of reviews 
        of differnt restaurant types in the city or state specified 

    Parameters
    ----------
    name: string
        a city name or a state name
    target: string
        indicates the name is a city or a state
    id_pos: int
        the id that uniquely identify a city

    Returns
    -------
    string
        the plot that is readable by html files
    '''
    name = process_name(name)
    query = '''SELECT r.Category, r.[Number of Review] FROM Restaurants as r
                JOIN Cities as c ON c.Id=r.City_id'''
    if target == 'city':
        query += ''' WHERE r.City="{}"'''.format(name)
    elif target == 'state':
        query += ''' WHERE c.State="{}"'''.format(name)
    
    results = searchDB(query)
    xvals, yvals = get_avg_and_sort(results)
    title = 'Average Number of Reviews of Different Categories in {} {}'.format(name, target.capitalize())
    return xvals, yvals, title, 'bar'
  
def barplot_toprated_restaurant(name, target):
    ''' a function that generate a barplot for the top rated restaurants
        in the city or state specified 

    Parameters
    ----------
    name: string
        a city name or a state name
    target: string
        indicates the name is a city or a state
    id_pos: int
        the id that uniquely identify a city

    Returns
    -------
    string
        the plot that is readable by html files
    '''
    name = process_name(name)
    query = '''SELECT r.Name, r.Rating FROM Restaurants as r
                JOIN Cities as c ON c.Id=r.City_id'''
    if target == 'city':
        query += ''' WHERE r.City="{}" ORDER BY r.Rating DESC'''.format(name)
    elif target == 'state':
        query += ''' WHERE c.State="{}" ORDER BY r.Rating DESC'''.format(name)
    
    results = searchDB(query)
    xvals = []
    yvals = []
    for row in results[:50]:
        xvals.append(str(row[0]))
        yvals.append(float(row[1]))
   
    title = 'Top Rated Restaurants in {} {}'.format(name, target.capitalize())
    return xvals, yvals, title, 'bar'
   
def barplot_topprice_restaurant(name, target):
    ''' a function that generate a barplot for the most 
        expensive restaurants in the city or state specified 

    Parameters
    ----------
    name: string
        a city name or a state name
    target: string
        indicates the name is a city or a state
    id_pos: int
        the id that uniquely identify a city

    Returns
    -------
    string
        the plot that is readable by html files
    '''
    name = process_name(name)
    query = '''SELECT r.Name, r.Price FROM Restaurants as r
                JOIN Cities as c ON c.Id=r.City_id'''
    if target == 'city':
        query += ''' WHERE r.City="{}"
                    AND r.Price NOTNULL ORDER BY r.Price DESC'''.format(name)
    elif target == 'state':
        query += ''' WHERE c.State="{}" AND r.Price NOTNULL ORDER BY r.Price DESC'''.format(name)
    
    results = searchDB(query)
    xvals = []
    yvals = []
    for row in results[:50]:
        xvals.append(str(row[0]))
        yvals.append(int(row[1]))
   
    title = 'Most Expensive Restaurants in {} {}'.format(name, target.capitalize())
    return xvals, yvals, title, 'bar'

def barplot_mostreviewed_restaurant(name, target):
    ''' a function that generate a barplot for the most 
        reviewed restaurants in the city or state specified 

    Parameters
    ----------
    name: string
        a city name or a state name
    target: string
        indicates the name is a city or a state
    id_pos: int
        the id that uniquely identify a city

    Returns
    -------
    string
        the plot that is readable by html files
    '''
    name = process_name(name)
    query = '''SELECT r.Name, r.[Number of Review] FROM Restaurants as r
                JOIN Cities as c ON c.Id=r.City_id'''
    if target == 'city':
        query +=  ''' WHERE r.City="{}" ORDER BY r.[Number of Review] DESC'''.format(name)
    elif target == 'state':
        query += ''' WHERE c.State="{}" ORDER BY r.[Number of Review] DESC'''.format(name)
    
    results = searchDB(query)
    xvals = []
    yvals = []
    for row in results[:50]:
        xvals.append(str(row[0]))
        yvals.append(float(row[1]))
    
    title = 'Top Restaurants With Most Number of Reviews in {} {}'.format(name, target.capitalize())
    return xvals, yvals, title, 'bar'


########################################

def get_cities_data(name, topx=6):
    print(f"get_cities_data: City name: {name}")
    name = process_name(name)
    query = '''SELECT c.Name FROM Cities as c
                WHERE c.State="{}"'''.format(name)
    results = searchDB(query)
    print(f"results")
    print(results)
    results = results[:topx]
    return [result[0] for result in results]

def get_restaurant_data(name, topx=5):
    name = process_name(name)
    query = '''SELECT * FROM Restaurants as r
                WHERE r.City="{}"'''.format(name)
    results = searchDB(query)

    #1 name, 5 rating, 6 price, 7 category, 8 phone, 10 url, 11 reviews

    new_results = [(result[1], result[5], result[6], result[7], result[8], result[10], result[11]) for result in results]
    new_results.sort(key = lambda x: x[1], reverse=True)
    new_results = new_results[:topx]
    return new_results
   

#########################################
########### Vaccination Plot ############
#########################################

def plot_vaccination():
    state_codes = pd.read_csv('static/csv/world_country_and_usa_states_latitude_and_longitude_values.csv')
    state_codes = state_codes[['usa_state','usa_state_code']]

    vaccine_data = pd.read_csv('static/csv/us_state_vaccinations.csv') 
    states = pd.read_csv('static/csv/states.csv')
    vaccine_data = vaccine_data.replace("New York State", "New York")
    vaccine_data = vaccine_data.merge(state_codes, left_on='location', right_on='usa_state')
    vaccine_data = vaccine_data.merge(states, left_on='location', right_on='State')

    df_new = pd.DataFrame(vaccine_data)

    fig = px.choropleth(df_new, 
        locations="usa_state_code", 
        color = "people_fully_vaccinated_per_hundred",
        labels = {'usa_state_code': 'US State Code','people_fully_vaccinated_per_hundred':'People Fully Vaccinated Per Hundred'},
        locationmode = 'USA-states', 
        hover_name="location",
        range_color=[0,70],
        color_continuous_scale = 'RdBu',
        scope="usa",
        title='Percent fully vaccinated population <br>',
        height=750,
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # fig.show()
    # fig.write_html("myplot.html")
    # graph1Plot = plotly.offline.plot(fig, 
    #             config={"displayModeBar": False}, 
    #             show_link=False, include_plotlyjs=False, 
    #             output_type='div')
    return graphJSON


#########################################
############# Flask Web App #############
#########################################

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/selection')
def selection():
    return render_template('selection.html')

@app.route('/mode')
def mode():
    return render_template('mode.html')

@app.route('/no')
def no():
    return render_template('no.html')

@app.route('/dine-in/vaccination')
def vaccination():
    graphJSON = plot_vaccination()
    return render_template('vaccination.html', graphJSON=graphJSON)

# @app.route('/state1')
# def state1():
#     return render_template('state1.html')

@app.route('/<mode>/state')
def state(mode):
    return render_template('state.html', mode=mode)

@app.route('/<mode>/states/<state>')
def states(mode, state):
    print(f"states {state}")
    cities = get_cities_data(state, topx=6)
    assert len(cities) == 6, "Length of cities not 6"
    modes = ["food delivery", "dine in"]
    city1 = cities[0]
    city2 = cities[1]
    city3 = cities[2]
    city4 = cities[3]
    city5 = cities[4]
    city6 = cities[5]
    return render_template('city.html', state=state, mode=mode, city1=city1, city2=city2, city3=city3, city4=city4, city5=city5, city6=city6)

@app.route('/<mode>/states/<state>/city/<city>')
def city_info(mode, state, city):

    xvals = []
    yvals = [] 
    titles = [] 
    ts = []
    for f in [
        pieplot_restaurant_categories,
        pieplot_rating, 
        pieplot_price, 
        # barplot_avgrating_each_category,
        barplot_avgprice_each_category,
        barplot_avgreview_each_category,
        barplot_toprated_restaurant,
        barplot_topprice_restaurant,
        # barplot_mostreviewed_restaurant,
    ]:
        xval, yval, title, t = f(city, target="city")
        xvals.append(xval)
        yvals.append(yval)
        titles.append(title)
        ts.append(t)

    fig = flask_plot(xvals, yvals, titles, ts)


    return render_template('restaurant_info.html', mode=mode, state=state,city=city, 
        fig=Markup(fig)
        )

@app.route('/<mode>/states/<state>/city/<city>/info')
def restaurant_info2(mode, state, city):
    results = get_restaurant_data(city, topx=5)
    #1 name, 5 rating, 6 price, 7 category, 8 phone, 10 url, 11 reviews

    r1_text = f"Rating: {results[0][1]}<br>Price: {results[0][2]}<br>Category: {results[0][3]}<br>Phone: {results[0][4]}<br>Reviews: {results[0][6]}"
    r2_text = f"Rating: {results[1][1]}<br>Price: {results[1][2]}<br>Category: {results[1][3]}<br>Phone: {results[1][4]}<br>Reviews: {results[1][6]}"
    r3_text = f"Rating: {results[2][1]}<br>Price: {results[2][2]}<br>Category: {results[2][3]}<br>Phone: {results[2][4]}<br>Reviews: {results[2][6]}"
    r4_text = f"Rating: {results[3][1]}<br>Price: {results[3][2]}<br>Category: {results[3][3]}<br>Phone: {results[3][4]}<br>Reviews: {results[3][6]}"
    r5_text = f"Rating: {results[4][1]}<br>Price: {results[4][2]}<br>Category: {results[4][3]}<br>Phone: {results[4][4]}<br>Reviews: {results[4][6]}"


    Restaurant_1 = results[0][0]
    Restaurant_2 = results[1][0]
    Restaurant_3 = results[2][0]
    Restaurant_4 = results[3][0]
    Restaurant_5 = results[4][0]

    r1_link = results[0][5]
    r2_link = results[1][5]
    r3_link = results[2][5]
    r4_link = results[3][5]
    r5_link = results[4][5]

    return render_template('info.html', 
        Restaurant_1=Restaurant_1,
        Restaurant_2=Restaurant_2,
        Restaurant_3=Restaurant_3,
        Restaurant_4=Restaurant_4,
        Restaurant_5=Restaurant_5,
        r1_link=r1_link,
        r2_link=r2_link,
        r3_link=r3_link,
        r4_link=r4_link,
        r5_link=r5_link,
        r1_text=r1_text,
        r2_text=r2_text,
        r3_text=r3_text,
        r4_text=r4_text,
        r5_text=r5_text,
    )



if __name__ == '__main__':
    build_database()
    app.run(debug=True, use_reloader=False)
   
   