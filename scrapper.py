import time 
import requests
from bs4 import BeautifulSoup
import numpy as np
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

source_url = "https://www.goodreads.com/list/show/1.Best_Books_Ever?page="

number_of_books_per_page = 100
pages_to_process = 50
start_page = 1

dataset = pd.DataFrame(columns=['Rank', 'Title', 'Author', 'Link', 'Score', 'Average Rating', 'Number of Ratings', 'Number of Votes'])

# fail safe mechanism - if process gets killed, we should read from the latest point and not from the start
if dataset.shape[0] > 0:
    start_page = number_of_books_per_page // int(dataset['Rank'].max())

# reading the data per page
start = time.time()
while start_page < pages_to_process:
    print(source_url+str(start_page))
    page = requests.get(source_url+str(start_page))
    soup = BeautifulSoup(page.text, "html.parser")

    temp_df = pd.DataFrame(columns=['Rank', 'Title', 'Author', 'Link', 'Score', 'Average Rating', 'Number of Ratings', 'Number of Votes'])
    
    temp_df['Author']               = pd.Series([i.find("span").text for i in soup.findAll("a",{"class":"authorName"})])
    temp_df['Title']                = pd.Series([i.find("span").text for i in soup.findAll("a",{"class":"bookTitle"})])
    temp_df['Link']                 = pd.Series([i['href'] for i in soup.findAll("a",{"class":"bookTitle"})])
    temp_df['Score']                = pd.Series([i.find("a").text for i in soup.findAll("span",{"class":"smallText uitext"})]).map(lambda s: re.split(': ', s)[1])
    rating_data                     = pd.Series([i.text for i in soup.findAll("span",{"class":"minirating"})])
    temp_df['Average Rating']       = rating_data.map(lambda r : re.split(' avg', r)[0])
    temp_df['Number of Ratings']    = rating_data.map(lambda n : re.search('(\d*\,?\d*\,?\d*) [ratings,rating]', n).group(1))
    temp_df['Rank']                 = pd.Series([i.text for i in soup.findAll("td",{"class":"number"})])
    temp_df['Number of Votes']      = pd.Series([i.text for i in soup.findAll("span",{"class":"smallText uitext"})]).map(lambda v: re.search('(\d*\,?\d*\,?\d*) people', v).group(1))

    dataset = pd.concat([dataset, temp_df])
    
    start_page += 1
    time.sleep(2) # sleep for 2 seconds so that IP does not get blocked

end = time.time()
print(str(end-start))
dataset.head()
