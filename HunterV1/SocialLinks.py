import logging
from bs4 import BeautifulSoup
import re

logging.basicConfig(filename='app.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def normalize_social_link(link):
    try:
        link = link.rstrip('/')
        link = re.sub(r'^https?://(www\.)?', '', link).lower()
        link = link.split('?')[0].split('#')[0]
        return 'https://' + link
    except Exception as e:
        logging.error(f"Error normalizing link {link}: {e}")
        return None

def ExtractSocialLinks(content):
    social_platforms = [
        'facebook.com', 'twitter.com', 'x.com', 'instagram.com', 
        'linkedin.com', 'youtube.com', 'pinterest.com', 
        'tiktok.com', 'threads.net', 'reddit.com', 'wa.me'
    ]
    
    social_links = {platform: set() for platform in social_platforms}
    
    try:
        soup = BeautifulSoup(content, 'html.parser')
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            for platform in social_platforms:
                if platform in href.lower():
                    normalized_link = normalize_social_link(href)
                    if normalized_link:
                        social_links[platform].add(normalized_link)
    except Exception as e:
        logging.error(f"Error extracting social links from content: {e}")
    
    social_links = {k: list(v) for k, v in social_links.items() if v}
    
    return social_links