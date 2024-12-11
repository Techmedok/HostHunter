import requests
import logging
import time
from typing import List, Dict, Tuple
from requests.exceptions import ConnectionError, Timeout, HTTPError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def GetMaiServerData(domain: str, max_retries: int = 2, timeout: int = 10) -> Tuple[List[Dict], List[Dict]]:
    """
    Retrieve mail server data for a given domain with robust error handling and retry mechanism.
    
    Args:
        domain (str): The domain to lookup mail server information for
        max_retries (int): Maximum number of retry attempts
        timeout (int): Timeout for each request in seconds
    
    Returns:
        Tuple of lists containing incoming and outgoing mail server information
    """
    request_url = f"https://hosting-checker.net/api/hosting/{domain}"
    
    for attempt in range(max_retries + 1):
        try:            
            response = requests.get(request_url, timeout=timeout)
            
            response.raise_for_status()
            
            mail_server_data = response.json()
            
            incoming_mail_servers = []
            if mail_server_data.get("incomingMail", {}).get("providers"):
                for provider in mail_server_data["incomingMail"]["providers"]:
                    try:
                        mail_server = {
                            "organization": provider.get("organization", "N/A"),
                            "domain": provider.get("domain", "N/A"),
                            "country": provider.get("country", "N/A"),
                            "asn": provider.get("asNumber", "N/A"),
                            "path": ' → '.join(provider.get("paths", [[]])[0]) if provider.get("paths") else "N/A"
                        }
                        incoming_mail_servers.append(mail_server)
                    except Exception as parse_error:
                        logger.warning(f"Error parsing incoming mail server entry: {parse_error}")
            
            outgoing_mail_servers = []
            if mail_server_data.get("outgoingMail", {}).get("providers"):
                for provider in mail_server_data["outgoingMail"]["providers"]:
                    try:
                        mail_server = {
                            "organization": provider.get("organization", "N/A"),
                            "domain": provider.get("domain", "N/A"),
                            "country": provider.get("country", "N/A"),
                            "asn": provider.get("asNumber", "N/A"),
                            "path": ' → '.join(provider.get("paths", [[]])[0]) if provider.get("paths") else "N/A"
                        }
                        outgoing_mail_servers.append(mail_server)
                    except Exception as parse_error:
                        logger.warning(f"Error parsing outgoing mail server entry: {parse_error}")
            
            return incoming_mail_servers, outgoing_mail_servers
        
        except ConnectionError as e:
            logger.error(f"Network connection error: {e}")
            if attempt == max_retries:
                logger.error("Max retries reached. Unable to complete request.")
                raise
            
        except Timeout as e:
            logger.error(f"Request timed out: {e}")
            if attempt == max_retries:
                logger.error("Max retries reached. Unable to complete request.")
                raise
        
        except HTTPError as e:
            logger.error(f"HTTP error occurred: {e}")
            if attempt == max_retries:
                logger.error("Max retries reached. Unable to complete request.")
                raise
        
        except requests.exceptions.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON response: {e}")
            if attempt == max_retries:
                logger.error("Max retries reached. Unable to complete request.")
                raise
        
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}")
            if attempt == max_retries:
                logger.error("Max retries reached. Unable to complete request.")
                raise
        
        if attempt < max_retries:
            wait_time = 2 ** attempt  
            time.sleep(wait_time)
    
    raise RuntimeError("Unexpected end of retry loop")


   
# domain = "amazon.com"
# incoming, outgoing = GetMaiServerData(domain)

# print("Incoming Mail Servers:")
# for server in incoming:
#     print(server)

# print("\nOutgoing Mail Servers:")
# for server in outgoing:
#     print(server)

