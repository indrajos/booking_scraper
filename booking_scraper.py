# IMPORTANT: developed and tested using Python 3.9 version

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import unicodedata

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.9,lt;q=0.8,et;q=0.7,de;q=0.6"}

# main function
def booking_scraper():
    checkin_date = input('Enter check-in date (default 2023-07-06): ') or '2023-07-06'
    checkout_date = input('Enter check-out date (default 2023-07-09): ') or '2023-07-09'
    city = input('Enter the city you travel (default Nida): ') or 'Nida'
    adults = input('Enter the amount of adult guests (default 2): ') or '2'
    children = input('Enter the amount of children guests (default 0): ') or '0'
    rooms = input('Enter amount of rooms (default 1): ') or '1'

    urls = get_Booking_listinings_url_list(checkin_date, checkout_date, city, adults, children, rooms)

    full_hotels_list = []
    for url in urls:
        one_page_data = get_list_of_listinings(url)
        full_hotels_list.extend(one_page_data)
    list_converter_to_csv(full_hotels_list, 'hotels_list.csv')
    return

# create URLS list for all search results
def get_Booking_listinings_url_list(checkin_date, checkout_date, city, adults, children, rooms):
    page_url = f'https://www.booking.com/searchresults.en-us.html?checkin={checkin_date}&checkout={checkout_date}&selected_currency=EUR&ss={city}&ssne={city}&ssne_untouched={city}&lang=en-us&sb=1&src_elem=sb&src=searchresults&dest_type=city&group_adults={adults}&no_rooms={rooms}&group_children={children}&sb_travel_purpose=leisure'
    response = requests.get(page_url, headers=headers)
    soup = BeautifulSoup(response.content, 'lxml')

    search_results = soup.find("h1").text
    properties_amount = re.search(r'\d+', search_results)

    if properties_amount == None:
        print('There are no results for these parameters')
        exit()
    else:
        urls_list = []
        urls_list.append(page_url)
        numb = 25
        link_no = int(properties_amount.group()) / 25
        iter = 1
        while iter <= link_no:
            next_url = page_url + '&offset=' + str(numb)
            urls_list.append(next_url)
            numb += 25
            iter += 1
        return urls_list

# get data for each hotel and put it to the list
def get_list_of_listinings(url):
    hotel_list = []
    response = requests.get(url, headers=headers)
    page_soup = BeautifulSoup(response.content, 'lxml')
    hotels = page_soup.find_all('div', {'data-testid': 'property-card'})

    for hotel in hotels:
        hotel_dict = {}
        hotel_dict['name'] = hotel.find('div', {'data-testid': 'title'}).text
        price = hotel.find('span', {'data-testid': 'price-and-discounted-price'})
        hotel_dict['price_eur'] = unicodedata.normalize("NFKD", price.text)

        line = hotel.find('div', {'data-testid': 'review-score'})
        if line is not None:
            line = line.text
            line = re.sub(" reviews?", '', line)
            hotel_dict['score'] = re.search("^\d\d|\d\.\d", line).group()
            line = re.sub("^\d\d|\d\.\d", '', line)
            hotel_dict['review'] = ''.join(re.findall("[a-zA-Z]*\s", line)).strip()
            hotel_dict['reviews_amount'] = re.sub("[a-zA-Z]*\s", '', line)
        else:
            hotel_dict['score'] = 'NaN'
            hotel_dict['review'] = 'NaN'
            hotel_dict['reviews_amount'] = 'NaN'

        hotel_list.append(hotel_dict)

    return hotel_list

# using hotels list create DataFrame and CSV file
def list_converter_to_csv(list_to_convert, file_name):
    df = pd.DataFrame(list_to_convert)
    df.to_csv(file_name, index=False)
    return



booking_scraper()