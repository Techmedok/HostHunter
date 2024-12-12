import requests
import logging
import time
from typing import Dict, Tuple, Optional
from requests.exceptions import RequestException, ConnectionError, Timeout

def GetSiteDataAndHeaders(
    domain: str, 
    timeout: int = 10, 
    max_retries: int = 1, 
    verbose: bool = True
) -> Optional[Tuple[Dict[str, str], str]]:
    """
    Fetch website data with robust error handling and retry mechanism.
    
    Args:
        domain (str): The domain to fetch data from
        timeout (int): Request timeout in seconds
        max_retries (int): Maximum number of retries for network failures (0-1)
        verbose (bool): Enable verbose logging
    
    Returns:
        Optional[Tuple[Dict[str, str], str]]: Tuple of headers and contents, or None if failed
    """
    max_retries = min(max(max_retries, 0), 1)
    
    logging.basicConfig(
        level= logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log', mode='a', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
    if not domain.startswith(('http://', 'https://')):
        domain = f"http://{domain}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        }

    
    for attempt in range(max_retries + 1):
        try:            
            response = requests.get(
                domain, 
                headers=headers, 
                timeout=timeout,
                verify=False 
            )
            
            response.raise_for_status()
                        
            return dict(response.headers), response.text
        
        except ConnectionError as e:
            logger.error(f"Connection error on attempt {attempt + 1}: {e}")
            if attempt == max_retries:
                logger.critical(f"Failed to connect to {domain} after {max_retries + 1} attempts")
                return None, None
            
            wait_time = 2 ** attempt
            time.sleep(wait_time)
        
        except Timeout as e:
            logger.error(f"Timeout error on attempt {attempt + 1}: {e}")
            if attempt == max_retries:
                logger.critical(f"Request to {domain} timed out after {max_retries + 1} attempts")
                return None, None
            
            wait_time = 2 ** attempt
            time.sleep(wait_time)
        
        except RequestException as e:
            logger.error(f"Request exception on attempt {attempt + 1}: {e}")
            if attempt == max_retries:
                logger.critical(f"Request to {domain} failed after {max_retries + 1} attempts")
                return None, None
            
            wait_time = 2 ** attempt
            time.sleep(wait_time)
        
        except Exception as e:
            logger.critical(f"Unexpected error: {e}")
            return None, None