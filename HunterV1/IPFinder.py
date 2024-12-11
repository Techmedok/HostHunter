import re
import json
import logging
import time
from typing import List, Optional

import playwright.sync_api
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def ip_extract(input_text: str) -> Optional[str]:
    """
    Extract IP address (IPv4 or IPv6) from input text.
    
    Args:
        input_text (str): Text to extract IP from
    
    Returns:
        Optional[str]: Extracted IP address or None
    """
    try:
        ip_pattern = r'(\b(?:\d{1,3}\.){3}\d{1,3}\b)|(\b([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b)|(\b([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}(:[0-9a-fA-F]{1,4}){1,2}|\b([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,3}|\b([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,4})\b'
        match = re.search(ip_pattern, input_text)
        return match.group(0) if match else None
    except Exception as e:
        logger.error(f"Error extracting IP: {e}")
        return None

def GetSiteIP(
    url: str, 
    obtip: str, 
    cookies_path: str = "cookies.json", 
    verbose: bool = True,
    max_retries: int = 1
) -> List[str]:
    """
    Retrieve IP addresses for a given URL using Censys search.
    
    Args:
        url (str): URL to search
        obtip (str): Obtained IP as fallback
        cookies_path (str, optional): Path to cookies file. Defaults to "c.json".
        verbose (bool, optional): Enable verbose logging. Defaults to True.
        max_retries (int, optional): Maximum number of retries. Defaults to 1.
    
    Returns:
        List[str]: List of extracted IP addresses
    """
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    endpoint = f"https://search.censys.io/_search?resource=hosts&sort=RELEVANCE&per_page=25&virtual_hosts=EXCLUDE&q={url}"
    
    try:
        with open(cookies_path, "r") as file:
            cookies_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading cookies: {e}")
        return [obtip]
    
    for attempt in range(max_retries + 1):
        try:
            with playwright.sync_api.sync_playwright() as p:
                browser = p.firefox.launch(
                    headless=True,
                    args=[
                        '--no-sandbox', 
                        '--disable-gpu', 
                        '--disable-dev-shm-usage'
                    ]
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
                    page.goto(endpoint, 
                        wait_until='networkidle', 
                        timeout=30000  
                    )
                except playwright.sync_api.TimeoutError:
                    logger.warning(f"Timeout on page load (Attempt {attempt + 1})")
                    if attempt == max_retries:
                        return [obtip]
                    time.sleep(2)  
                    continue
                
                html_content = page.content()
                
                soup = BeautifulSoup(html_content, "html.parser")
                
                results = soup.find_all("div", class_="SearchResult result")
                
                titles = [
                    result.find("a", class_="SearchResult__title-text").get_text(strip=True)
                    for result in results
                    if result.find("a", class_="SearchResult__title-text")
                ]
                
                addresses = [
                    ip for title in titles 
                    if (ip := ip_extract(title)) is not None
                ]
                
                if not addresses:
                    addresses = [obtip]
                
                return addresses
        
        except Exception as e:
            logger.error(f"Unexpected error in IP extraction (Attempt {attempt + 1}): {e}")
            if attempt == max_retries:
                logger.error("Max retries reached. Returning fallback IP.")
                return [obtip]
            
            time.sleep(2)
    
    return [obtip]