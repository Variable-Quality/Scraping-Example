import requests
from bs4 import BeautifulSoup
import re

#Sends a GET request to books.toscrape.com, returns a Response object (not plaintext!!!)

#https://www.useragentstring.com/pages/useragentstring.php
headers = {'User-Agent' : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0"}
URL = "https://books.toscrape.com/catalogue/page-1.html"
html = requests.get(URL)

#Creates a BeautifulSoup object with the raw HTML of the page
#Also tells bs4 we're parsing HTML
soup = BeautifulSoup(html.text, "html.parser")

class Book():
    #I <3 objects

    def __init__(self, title:str, link:str, price:float, stars:int):
        self.title = title
        self.link = link
        self.price = price
        self.stars = stars

    def __str__(self):
        return self.title

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
            try:
                stars_str = article.find('p').get('class')[1].lower()
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



def main(soup:BeautifulSoup) -> None:

    result_1 = easiest_method(soup)

    for book in result_1:
        print(book.title + "\n", "{}/{}".format(URL, book.link) + "\n", str(book.price) + "\n", "Stars: {}".format("*"*book.stars))

    result_2 = backup_method(soup, True)

    for book in result_2:
        print(str(book) + "\n", "{}/{}".format(URL, book.link) + "\n", str(book.price) + "\n", "Stars: {}\n".format("*"*book.stars))



if __name__ == "__main__":
    main(soup)
