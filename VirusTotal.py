# pip install virustotal-python
from virustotal_python import Virustotal
from pprint import pprint
from base64 import urlsafe_b64encode

# Replace 'YOUR_API_KEY' with your actual VirusTotal API key
api_key = '63a0c69cdf7935b23facb55d41cc94b6660507f9980a3d2bc1cc6b4a093a5d95'
vtotal = Virustotal(API_KEY=api_key)

url = "techmedok.com"

# v3 example: Send URL to VirusTotal for analysis
try:
    # URL safe encode the URL in base64 format
    url_id = urlsafe_b64encode(url.encode()).decode().strip("=")
    
    # Obtain the analysis results for the URL using the url_id
    analysis_resp = vtotal.request(f"urls/{url_id}")
    
    # Print results
    pprint(analysis_resp.data)

except Exception as err:
    print(f"An error occurred: {err}")
