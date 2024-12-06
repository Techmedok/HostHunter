# from bs4 import BeautifulSoup
# import requests
# import json

# cookies_file = "c.json" 
# with open(cookies_file, "r") as file:
#     cookies_data = json.load(file)

# cookies = {cookie["name"]: cookie["value"] for cookie in cookies_data}
# url = "https://search.censys.io/_search?resource=hosts&sort=RELEVANCE&per_page=25&virtual_hosts=EXCLUDE&q=techmedok.com"
# response = requests.get(url, cookies=cookies)



# print(response)

# # Parse the HTML content using BeautifulSoup
# soup = BeautifulSoup(response, 'html.parser')

# # Extract all 'SearchResult result' divs and their 'a' tag's text content
# results = soup.find_all("div", class_="SearchResult result")
# titles = [result.find("a", class_="SearchResult__title-text").get_text(strip=True) for result in results]

# print(titles)


from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import json
import time 

s = time.time()

cookies_file = "c.json"
with open(cookies_file, "r") as file:
    cookies_data = json.load(file)

url = "https://search.censys.io/_search?resource=hosts&sort=RELEVANCE&per_page=25&virtual_hosts=EXCLUDE&q=1tamilblasters.fit"

options = Options()
options.add_argument("--headless")
driver = webdriver.Firefox(options=options)

driver.get(url)

for cookie in cookies_data:
    driver.add_cookie({
        "name": cookie["name"],
        "value": cookie["value"],
        "domain": cookie.get("domain", "search.censys.io"),
    })

driver.get(url)

html_content = driver.page_source

driver.quit()

soup = BeautifulSoup(html_content, "html.parser")

results = soup.find_all("div", class_="SearchResult result")

titles = [result.find("a", class_="SearchResult__title-text").get_text(strip=True) for result in results if result.find("a", class_="SearchResult__title-text")]

print(titles)
e = time.time()
print(e-s)