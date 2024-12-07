
import requests

def GetIPData(ip):
    requesturl = f"http://ip-api.com/json/{ip}"
    response = requests.get(requesturl)
    ipdata = response.json()
    ipdetails = {
        'country': ipdata["country"], 
        'countrycode': ipdata["countryCode"], 
        'region': ipdata["regionName"], 
        'city': ipdata["city"], 
        'zip': ipdata["zip"], 
        'lat': ipdata["lat"], 
        'lon': ipdata["lon"], 
        'timezone': ipdata["timezone"], 
        'isp': ipdata["isp"], 
        'organization': ipdata["org"], 
        'asn': ipdata["as"]
    }
    return ipdetails

# ip="20.204.13.165"
# print(GetIPData(ip))