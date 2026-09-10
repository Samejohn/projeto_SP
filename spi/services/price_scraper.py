from bs4 import BeautifulSoup
import requests
import csv

url = "https://books.toscrape.com/"
response = requests.get(url)

print(response.status_code)

sup = BeautifulSoup(response.text, "html.parser")
books = sup.find_all("article", class_="product_pod")
for book in books:
    title = book.h3.a.attrs["title"]
    price = book.find("p", class_="price_color").text
    print(f"Title: {title}, Price: {price}")
