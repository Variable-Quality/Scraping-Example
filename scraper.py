import requests
from bs4 import BeautifulSoup
import re
import os
import json

#Creating important directories

if not os.path.exists("json"):
    os.mkdir("json")

if not os.path.exists("cache"):
    os.mkdir("cache")


#Sends a GET request to books.toscrape.com, returns a Response object (not plaintext!!!)

#https://www.useragentstring.com/pages/useragentstring.php
headers = {'User-Agent' : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0"}
URL = "https://books.toscrape.com"
html = requests.get(URL, headers=headers)

#Creates a BeautifulSoup object with the raw HTML of the page
#Also tells bs4 we're parsing HTML
soup = BeautifulSoup(html.text, "html.parser")

class Book():
    #I <3 objects

    def __init__(self, title:str, link:str, price:float, stars:int):
        #Mandatory attributes
        self.title = title
        self.link = link
        self.price = price
        self.stars = stars

        #Optional attributes
        self.description = ""
        self.is_available = False

    #defines how the object works when converted to a string
    def __str__(self):
        return self.title

    def as_dict(self) -> dict:
        #There are other ways of doing this programatically
        #For this example this is fine

        return {"title" : self.title, "url": self.link, "price": str(self.price), "stars": self.stars, "description": self.description, "availability" : str(self.is_available)}

def easiest_method(soup:BeautifulSoup) -> list:
    #Primary method, each has a unique class

    #Finds all <article> tags on the page
    articles = soup.find_all("article")
    
    books = []
    for article in articles:

        #Checks the text in the "class" attrib to see if it contains product_pod
        #If it does, it makes a Book object and adds to a list

        if "product_pod" in article.get("class"):
            title_tag = article.find_all("a")[1]
            price_raw = article.find('p',{"class": "price_color"})
            #I mean I could just cut the first character off but wheres the fun in that
            #Also some currencies come at the end I guess? idk
            
            price = re.sub(r"[^0-9.]", '', price_raw.text)

            #This is a bad way of doing this but this is an example so
            #Its bad because it could possibly MAYBE pick up a false book object
            #There are a ton of other things that would have to go wrong but this is still bad
            #Oh well!
            try:
                stars_str = article.find('p').get('class')[1].lower()
            except:
                stars = 0
                b = Book(title_tag.get("title"), title_tag.get("href"), float(price), stars)
                books.append(b)
                continue


            #match case is 3.10+ only and we love backwards compatability
            if "one" in stars_str:
                stars = 1
            elif "two" in stars_str:
                stars = 2
            elif "three" in stars_str:
                stars = 3
            elif "four" in stars_str:
                stars = 4
            elif "five" in stars_str:
                stars = 5
            else:
                stars = 0

            b = Book(title_tag.get("title"), title_tag.get("href"), float(price), stars)
            books.append(b)

    #Returns the list of books found
    return books

def backup_method(soup:BeautifulSoup, debug:bool = False) -> list:
    #Secondary Method, narrowing down search area
    li_count = len(soup.find_all("li"))
    print("Number of li elements anywhere on the page: {}\n".format(li_count))

    if debug: input("")
    ol_count = len(soup.find_all("ol"))

    print("Number of ol elements anywhere on the page: {}\n".format(ol_count))
    if debug: input("")

    #Since there is only one ordered list, we can assume it'll be the body
    body = soup.find("ol")

    body_li_count = len(body.find_all("li"))
    print("Number of li elements within page body: {}\n".format(body_li_count))
    
    if debug: input("")
    #Creates a list of all li elements within the "body" soup object
    listings = body.find_all("li")
    
    books = []
    for listing in listings:
        title_tag = listing.find_all("a")[1]
        price_raw = listing.find("p", {"class" : "price_color"})
        
        
        #Again, reminder, horrible way of doing this
        #I'm writing this code while in Kansas City lol
        try:
            stars_str = listing.find('p').get('class')[1].lower()
        except:
            stars = 0
            b = Book(title_tag.get("title"), title_tag.get("href"), float(price), stars)
            books.append(b)
            continue


        if "one" in stars_str:
            stars = 1
        elif "two" in stars_str:
            stars = 2
        elif "three" in stars_str:
            stars = 3
        elif "four" in stars_str:
            stars = 4
        elif "five" in stars_str:
            stars = 5
        else:
            stars = 0
        
        price = re.sub(r"[^0-9.]", '', price_raw.text)
        b = Book(title_tag.get("title"), title_tag.get("href"), float(price), stars)
        books.append(b)

    return books

def cache_page(url:str, page_name:str) -> None:
    #ALWAYS sanitize filenames!!!!
    #Operating systems can be finnicky so its easier to just guarantee the file name will work properly everywhere*

    headers = {'User-Agent' : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0"}
    html = requests.get(url, headers=headers)

    #Removes spaces since they're largely just for looks
    #And it makes typing the html file name out a bit harder
    filename = re.sub(r"[^a-zA-Z0-9]", '', page_name)
    with open("cache/{}.html".format(filename), "w") as f:
        f.write(html.text)

def get_information(books:list, force_cache=False) -> list:
    ret = []
    for book in books:
        title = re.sub(r"[^a-zA-Z0-9]", '', book.title)
        filename = "cache/{}.html".format(title)

        if not os.path.isfile(filename) or force_cache:
            #If the page isnt cached, cache it
            #Usually I relegate this to a function but I cba refactoring this code
            
            page_link = "{}/{}".format(URL, book.link)
            print(page_link)
            cache_page(page_link, title)

        with open(filename, "r") as f:
            
            l_html = f.read()
        


        l_soup = BeautifulSoup(l_html, "html.parser")


        #Unreliable way of finding the description
        #Would be nicer to find it by class or something
        desc = l_soup.find("article").find_all("p")[3].text
        book.description = desc.replace("\n"," ")

        #Each table is 7 items long, with the 6th being accessibility
        availability = l_soup.find_all("tr")[5]
        if "in stock" in availability.text.lower():
            book.stock_count = int(re.sub(r"[^0-9]", '', availability.text))
            book.is_available = True
        else:
            book.stock_count = 0
            book.is_available = False
        
        ret.append(book)

    return ret
        
        
def dump_to_json(book) -> None:
    #Simple class to dump a book into a json file

    w_dict = book.as_dict()
    filename = re.sub(r"[^a-zA-Z0-9]", "", book.title) + ".json"
    json_obj = json.dumps(w_dict, indent=4)

    with open(f"json/{filename}", "w") as f:
        f.write(json_obj)
       
def main(soup:BeautifulSoup) -> None:

    t_result = easiest_method(soup)
    result = get_information(t_result)
    for book in result:
                                #This page uses non-complete URLS for its hrefs
                                #So I do this to make it look nicer
                                #You could also store the URL in this format
                                #But thats more memory then (not like that matters in python lol)
        print(book.title + "\n", "{}/{}".format(URL, book.link) + "\n", str(book.price) + "\n", "Stars: {}\n".format("*"*book.stars), "Stock Count: {}\n".format(book.stock_count))

        cache_page(f"{URL}/{book.link}", book.title)
        dump_to_json(book)


    result_2 = backup_method(soup, False)

    for book in result_2:
        print(str(book) + "\n", "{}/{}".format(URL, book.link) + "\n", str(book.price) + "\n", "Stars: {}\n".format("*"*book.stars))

        #cache_page(f"{URL}/{book.link}", book.title)

        #If you wanted to only use the 2nd method you could uncomment this line
        #However, it writes the exact same info

if __name__ == "__main__":
    main(soup)
