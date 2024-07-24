import requests 
import selenium
from bs4 import BeautifulSoup
import re

# URL da página que você quer fazer scraping
url = "https://www.strava.com/segments/search?filter_type=Run&keywords=La+Mision+35k&max-cat=5&min-cat=0&page=1&terrain=all&utf8=%E2%9C%93"

url_1_2022 = 'https://www.strava.com/segments/32632496'
url_2_2022 = 'https://www.strava.com/segments/32632505'
