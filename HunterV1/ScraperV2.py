import os
import random
import time
import re
from urllib.parse import urlparse, quote
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

class WebScraper:
    def __init__(self, user_agents=None, cache_dir='webpage_cache'):
        """
        Initialize the web scraper with performance and caching optimizations
        
        :param user_agents: List of user agents to rotate
        :param cache_dir: Directory to store cached web pages
        """
        self.user_agents = user_agents or [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
        ]
        
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def _sanitize_url(self, url):
        """
        Sanitize and validate the URL
        
        :param url: URL to sanitize
        :return: Cleaned and validated URL
        """
        if isinstance(url, tuple):
            url = url[0] if url else ''
        
        url = url.strip()
        
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        return url

    def _get_cache_path(self, url):
        """
        Generate a unique cache filename for a given URL
        
        :param url: URL to generate cache filename for
        :return: Path to cache file
        """
        try:
            parsed_url = urlparse(url)
            safe_filename = f"{parsed_url.netloc}_{quote(parsed_url.path, safe='')}.html"
            
            safe_filename = re.sub(r'[<>:"/\\|?*]', '_', safe_filename)
            safe_filename = safe_filename.replace('__', '_').replace(' ', '_')
            
            return os.path.join(self.cache_dir, safe_filename[:255])  
        except Exception as e:
            print(f"Error generating cache path: {e}")
            return os.path.join(self.cache_dir, 'invalid_url.html')

    def is_cache_valid(self, cache_path, max_age_hours=24):
        """
        Check if cached file is still valid
        
        :param cache_path: Path to cache file
        :param max_age_hours: Maximum age of cache in hours
        :return: Boolean indicating cache validity
        """
        if not os.path.exists(cache_path):
            return False
        
        file_age = (time.time() - os.path.getmtime(cache_path)) / 3600
        return file_age < max_age_hours

    def scrape_website(self, url, timeout=15, use_cache=True):
        """
        Scrape a website with performance and caching optimizations
        
        :param url: URL to scrape
        :param timeout: Request timeout in seconds
        :param use_cache: Whether to use caching mechanism
        :return: Page content or None if scraping fails
        """
        url = self._sanitize_url(url)

        cache_path = self._get_cache_path(url)
        if use_cache and self.is_cache_valid(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                print(f"Error reading cache: {e}")

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,  
                    channel="msedge",  
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-accelerated-2d-canvas',
                        '--no-first-run',
                        '--no-zygote',
                        '--single-process',
                        '--disable-gpu'
                    ]
                )

                try:
                    context = browser.new_context(
                        user_agent=random.choice(self.user_agents),
                        viewport={'width': 1920, 'height': 1080},
                        ignore_https_errors=True,
                        java_script_enabled=True,
                        bypass_csp=True,
                        extra_http_headers={
                            'Accept-Language': 'en-US,en;q=0.9',
                            'Referer': random.choice([
                                'https://www.google.com',
                                'https://www.bing.com'
                            ])
                        }
                    )

                    context.add_init_script("""
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined
                        });
                        delete navigator.connection;
                    """)

                    page = context.new_page()
                    
                    page.set_default_timeout(timeout * 1000)
                    
                    def intercept_route(route):
                        resource_type = route.request.resource_type
                        if resource_type in ['image', 'media', 'font', 'stylesheet']:
                            route.abort()
                        else:
                            route.continue_()

                    page.route('**/*', intercept_route)

                    page.goto(url, 
                        wait_until='domcontentloaded',
                        timeout=timeout * 1000
                    )

                    page.wait_for_load_state('networkidle', timeout=timeout * 1000)

                    content = page.content()

                    if use_cache:
                        try:
                            with open(cache_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                        except Exception as e:
                            print(f"Error writing cache: {e}")

                    return content

                except Exception as e:
                    print(f"Scraping error for {url}: {e}")
                    return None
                finally:
                    browser.close()

        except Exception as e:
            print(f"Playwright initialization error: {e}")
            return None

def Scraper(url):
    scraper = WebScraper()
    content = scraper.scrape_website(url)
    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text()
    cleaned_text = "\n".join([line for line in text.splitlines() if line.strip()])
    return cleaned_text

# url = "anukampa.mp.gov.in"
# print(Scraper(url))