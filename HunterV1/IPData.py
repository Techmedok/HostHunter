import requests
import ipaddress
import logging
import sys
import time

def GetIPData(ip, max_retries=2, retry_delay=1):
    """
    Retrieve detailed geolocation and network information for a given IP address.
   
    Args:
        ip (str): IP address to lookup
        verbose (bool, optional): Enable detailed error logging. Defaults to False.
        max_retries (int, optional): Number of retry attempts for network errors. Defaults to 2.
        retry_delay (int/float, optional): Delay between retry attempts in seconds. Defaults to 1.
   
    Returns:
        dict: Detailed IP information or empty dict if lookup fails
    """

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log'),
            logging.StreamHandler()
        ]
    )

    logger = logging.getLogger(__name__)

    try:
        ipaddress.ip_address(ip)
    except ValueError:
        logger.error(f"Invalid IP address format: {ip}")
        return {}

    for attempt in range(max_retries + 1):
        try:
            requesturl = f"http://ip-api.com/json/{ip}"
            
            try:
                response = requests.get(requesturl, timeout=10)
                response.raise_for_status()
            except requests.RequestException as e:
                logger.error(f"Network error during IP lookup (Attempt {attempt + 1}/{max_retries + 1}): {e}")
                
                if attempt == max_retries:
                    return {}
                
                time.sleep(retry_delay)
                continue

            try:
                ipdata = response.json()
            except ValueError:
                logger.error("Failed to parse JSON response")
                return {}

            if ipdata.get("status") != "success":
                logger.warning(f"IP lookup failed: {ipdata.get('message', 'Unknown error')}")
                return {}

            ipdetails = {
                'country': ipdata.get("country", "N/A"),
                'countrycode': ipdata.get("countryCode", "N/A"),
                'region': ipdata.get("regionName", "N/A"),
                'city': ipdata.get("city", "N/A"),
                'zip': ipdata.get("zip", "N/A"),
                'lat': ipdata.get("lat", None),
                'lon': ipdata.get("lon", None),
                'timezone': ipdata.get("timezone", "N/A"),
                'isp': ipdata.get("isp", "N/A"),
                'organization': ipdata.get("org", "N/A"),
                'asn': ipdata.get("as", "N/A"),
                'query': ipdata.get("query", ip)
            }

            try:
                ipdetails['lat'] = float(ipdetails['lat']) if ipdetails['lat'] is not None else None
                ipdetails['lon'] = float(ipdetails['lon']) if ipdetails['lon'] is not None else None
            except (TypeError, ValueError):
                logger.warning("Could not convert latitude/longitude to float")
                ipdetails['lat'] = None
                ipdetails['lon'] = None

            return ipdetails

        except Exception as e:
            logger.error(f"Unexpected error in IP data retrieval (Attempt {attempt + 1}/{max_retries + 1}): {e}")
            
            if attempt == max_retries:
                return {}
            
            time.sleep(retry_delay)

    return {}