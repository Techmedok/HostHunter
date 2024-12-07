import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

def normalize_social_link(link):
    link = link.rstrip('/')
    link = re.sub(r'^https?://(www\.)?', '', link).lower()
    link = link.split('?')[0].split('#')[0]
    return link

def extract_social_media_links(url):
    social_platforms = [
        'facebook.com', 'twitter.com', 'x.com', 'instagram.com', 
        'linkedin.com', 'youtube.com', 'pinterest.com', 
        'tiktok.com', 'threads.net', 'reddit.com', 'wa.me'
    ]
    
    social_links = {platform: set() for platform in social_platforms}
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(url, href)
            parsed_url = urlparse(full_url)
            
            for platform in social_platforms:
                if platform in parsed_url.netloc.lower():
                    normalized_link = normalize_social_link(full_url)
                    social_links[platform].add(normalized_link)
        
        social_links = {k: list(v) for k, v in social_links.items() if v}
        
        return social_links
    
    except requests.RequestException as e:
        print(f"Error fetching website: {e}")
        return {}

# website_url = 'https://techmedok.com'
# social_media_links = extract_social_media_links(website_url)
# print(social_media_links)