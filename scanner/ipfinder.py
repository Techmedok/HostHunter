from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import re
import socket

def IPExtract(input):
    ip_pattern = r'(\b(?:\d{1,3}\.){3}\d{1,3}\b)|(\b([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b)|(\b([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}(:[0-9a-fA-F]{1,4}){1,2}|\b([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,3}|\b([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,4})\b'
    match = re.search(ip_pattern, input)
    if match:
        return match.group(0)
    return None

def GetSiteIP(url, cookies_path = "c.json"):
    endpoint = f"https://search.censys.io/_search?resource=hosts&sort=RELEVANCE&per_page=25&virtual_hosts=EXCLUDE&q={url}"
    with open(cookies_path, "r") as file:
        cookies_data = json.load(file)

    with sync_playwright() as p:
        browser = p.firefox.launch(
            headless=True, 
            args=['--no-sandbox', '--disable-gpu']
        )
        
        context = browser.new_context()
        
        context.add_cookies([
            {
                'name': cookie['name'],
                'value': cookie['value'],
                'domain': cookie.get('domain', 'search.censys.io'),
                'path': '/'
            } for cookie in cookies_data
        ])
        
        page = context.new_page()
        
        try:
            page.goto(endpoint, wait_until='networkidle')
            
            html_content = page.content()
            
            soup = BeautifulSoup(html_content, "html.parser")
            
            results = soup.find_all("div", class_="SearchResult result")
            titles = [
                result.find("a", class_="SearchResult__title-text").get_text(strip=True)
                for result in results 
                if result.find("a", class_="SearchResult__title-text")
            ]
            
            Address = []
            for title in titles:
                IP = IPExtract(title)
                if IP:
                    Address.append(IP)
            
            if len(Address)==0:
                try:
                    ip = socket.gethostbyname(url)
                    Address = [ip]
                except socket.gaierror:
                    Address = [None]

            return Address
        
        finally:
            page.close()
            context.close()
            browser.close()

url = "techmedok.com"
print(GetSiteIP(url))