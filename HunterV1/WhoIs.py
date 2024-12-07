import requests
import logging
import sys
import time

def GetWhois(domain, verbose=False, max_retries=2, retry_delay=1):
    """
    Retrieve WHOIS information for a given domain with comprehensive error handling and retry mechanism.
    
    Args:
        domain (str): The domain name to look up
        verbose (bool, optional): Enable detailed error logging. Defaults to False.
        max_retries (int, optional): Number of retry attempts for network errors. Defaults to 2.
        retry_delay (int/float, optional): Delay between retry attempts in seconds. Defaults to 1.
    
    Returns:
        dict: Dictionary containing all WHOIS information or empty dictionaries if lookup fails
    """
    # # Configure logging based on verbose flag
    # logging.basicConfig(
    #     level=logging.INFO if verbose else logging.ERROR, 
    #     format='%(asctime)s - %(levelname)s: %(message)s',
    #     stream=sys.stderr
    # )
        # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)

    # Validate domain input
    if not domain or not isinstance(domain, str):
        logger.error(f"Invalid domain input: {domain}")
        return {
            'domain': {},
            'registrar': {},
            'registrant': {},
            'administrative': {},
            'technical': {}
        }

    for attempt in range(max_retries + 1):
        try:
            # Construct request URL
            requesturl = f"https://who-dat.as93.net/{domain}"
            
            # Send request with error handling
            try:
                response = requests.get(requesturl, timeout=10)
                response.raise_for_status()
            except requests.RequestException as e:
                logger.error(f"Network error during WHOIS lookup (Attempt {attempt + 1}/{max_retries + 1}): {e}")
                
                # If this is the last attempt, return empty dictionaries
                if attempt == max_retries:
                    return {
                        'domain': {},
                        'registrar': {},
                        'registrant': {},
                        'administrative': {},
                        'technical': {}
                    }
                
                # Wait before retrying
                time.sleep(retry_delay)
                continue
            
            # Parse JSON response
            try:
                whoisdata = response.json()
            except ValueError:
                logger.error("Failed to parse JSON response")
                return {
                    'domain': {},
                    'registrar': {},
                    'registrant': {},
                    'administrative': {},
                    'technical': {}
                }
            
            # Safe nested dictionary value retrieval
            def safe_get(dictionary, *keys, default=None):
                for key in keys:
                    try:
                        dictionary = dictionary[key]
                    except (KeyError, TypeError):
                        return default
                return dictionary or default
            
            # Comprehensive WHOIS data extraction
            whois_result = {
                'domain': {
                    "url": safe_get(whoisdata, "domain", "domain", default=""),
                    "domainname": safe_get(whoisdata, "domain", "name", default=""),
                    "domainextension": safe_get(whoisdata, "domain", "extension", default=""),
                    "domainid": safe_get(whoisdata, "domain", "id", default=""),
                    "status": safe_get(whoisdata, "domain", "status", default="Unknown"),
                    "domaincreated": safe_get(whoisdata, "domain", "created_date_in_time", default="N/A"),
                    "domainupdated": safe_get(whoisdata, "domain", "updated_date_in_time", default="N/A"),
                    "domainexpiration": safe_get(whoisdata, "domain", "expiration_date_in_time", default="N/A")
                },
                'registrar': {
                    "registrarid": safe_get(whoisdata, "registrar", "id", default=""),
                    "registrarname": safe_get(whoisdata, "registrar", "name", default=""),
                    "registrarphone": safe_get(whoisdata, "registrar", "phone", default="N/A"),
                    "registraremail": safe_get(whoisdata, "registrar", "email", default="N/A"),
                    "registrarsite": safe_get(whoisdata, "registrar", "referral_url", default="")
                },
                'registrant': {
                    'registrantname': safe_get(whoisdata, "registrant", "name", default=""),
                    'registrantorganization': safe_get(whoisdata, "registrant", "organization", default=""),
                    'registrantstreet': safe_get(whoisdata, "registrant", "street", default=""),
                    'registrantcity': safe_get(whoisdata, "registrant", "city", default=""),
                    'registrantprovince': safe_get(whoisdata, "registrant", "province", default=""),
                    'registrantpostalcode': safe_get(whoisdata, "registrant", "postal_code", default=""),
                    'registrantcountry': safe_get(whoisdata, "registrant", "country", default=""),
                    'registrantphone': safe_get(whoisdata, "registrant", "phone", default="N/A"),
                    'registrantemail': safe_get(whoisdata, "registrant", "email", default="N/A")
                },
                'administrative': {
                    'administrativename': safe_get(whoisdata, "administrative", "name", default=""),
                    'administrativeorganization': safe_get(whoisdata, "administrative", "organization", default=""),
                    'administrativestreet': safe_get(whoisdata, "administrative", "street", default=""),
                    'administrativecity': safe_get(whoisdata, "administrative", "city", default=""),
                    'administrativeprovince': safe_get(whoisdata, "administrative", "province", default=""),
                    'administrativepostalcode': safe_get(whoisdata, "administrative", "postal_code", default=""),
                    'administrativecountry': safe_get(whoisdata, "administrative", "country", default=""),
                    'administrativephone': safe_get(whoisdata, "administrative", "phone", default="N/A"),
                    'administrativeemail': safe_get(whoisdata, "administrative", "email", default="N/A")
                },
                'technical': {
                    'technicalname': safe_get(whoisdata, "technical", "name", default=""),
                    'technicalorganization': safe_get(whoisdata, "technical", "organization", default=""),
                    'technicalstreet': safe_get(whoisdata, "technical", "street", default=""),
                    'technicalcity': safe_get(whoisdata, "technical", "city", default=""),
                    'technicalprovince': safe_get(whoisdata, "technical", "province", default=""),
                    'technicalpostalcode': safe_get(whoisdata, "technical", "postal_code", default=""),
                    'technicalcountry': safe_get(whoisdata, "technical", "country", default=""),
                    'technicalphone': safe_get(whoisdata, "technical", "phone", default="N/A"),
                    'technicalemail': safe_get(whoisdata, "technical", "email", default="N/A")
                }
            }
            
            return whois_result

        except Exception as e:
            logger.error(f"Unexpected error in WHOIS data retrieval (Attempt {attempt + 1}/{max_retries + 1}): {e}")
            
            # If this is the last attempt, return empty dictionaries
            if attempt == max_retries:
                return {
                    'domain': {},
                    'registrar': {},
                    'registrant': {},
                    'administrative': {},
                    'technical': {}
                }
            
            # Wait before retrying
            time.sleep(retry_delay)

    # This line should never be reached, but included for completeness
    return {
        'domain': {},
        'registrar': {},
        'registrant': {},
        'administrative': {},
        'technical': {}
    }