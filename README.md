**Final Project SI507**


## Project Title: Food Panda

## Introduction
This program runs a Flask application that retrieves Yelp data. It explores food options at specific locations. It takes the input from the user if they want to Dine-in or want a food delivery. A vaccination rate interactive graph is dispalyed and then the user is provided with a list of states and user is directed the city page based on the user input. Further the city input is taken into account and they data about the city restaurants is dispalyed on interactive graphs. Top-5 restaurants in the city are displayed. The program uses Python Anaconda, Flask, SQLAlchemy, Plotly, Flask Tables, a local database, a JSON cache file to cache data returned by the API and Datatables. 

## Data Sources
(1) The web from Wikipedia, which is the data source for the table "Cities" in the database. (https://en.wikipedia.org/wiki/List_of_United_States_cities_by_population). 

(2) Yelp Fusion, which is the data source for the table "Restaurants" in the database.
(https://www.yelp.com/developers/documentation/v3/business_search)

(3) The kaggle database was used for to procure latitude and longitude for every country and state. 
https://www.kaggle.com/paultimothymooney/latitude-and-longitude-for-every-country-and-state

(4)  The kaggle database was used to get the vaccination rates in each.  
https://www.kaggle.com/paultimothymooney/usa-covid19-vaccinations

(5) The kaggle database was used to get the state code and merge this data with data extracted from source 3. 
https://www.kaggle.com/omer2040/usa-states-to-region/version/1

## Presentation option
Terminal or Command Line was used to run the code. 
```
### Step 1: Apply an API Key for Yelp Fusion
(1) Go to "https://www.yelp.com/developers/documentation/v3/authentication" and create your app according to the instruction. 
(2) Create a new python file "secret.py" in the same folder as "program.py". And add the code:
API_KEY = '<your key>'
```  
### Step 2: Install packages
$ pip install -r requirements.txt --user
```
### Step 3: Run program.py    
$ python program.py
```  
### Step 4: Open "http://127.0.0.1:5000/ " in a browser

## Requirements
beautifulsoup4==4.9.0
bs4==0.0.1
requests==2.23.0
Flask==1.1.2
Jinja2==2.11.1
plotly==4.6.0
plotly-geo==1.0.0
geopandas==0.3.0
pyshp==1.2.10
shapely==1.6.3

## In this repository:
- `project.py` is the main program file
- `data.json` Sample data from the API
- `requirements.txt` to install all required modules. 
- `templates/`
  - `index.html` HTML template for the homepage
  - `selection.html` HTML template for the question 'Are you hungry?'
  - `mode.html` HTML template for selection for food eating option like Dine-In or Delivery 
  - `state.html` HTML template for state selection. 
  - `vaccination.html` HTML template for vaccination rate in US. 
  - `city.html` HTML template for city selection. 
  - `restaurant.html` HTML template with restaurant data. 
