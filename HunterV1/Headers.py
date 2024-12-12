import requests

def GetHeaders(domain):
    try:
        url = f"https://{domain}"
        response = requests.get(url, timeout=5)
    except requests.exceptions.RequestException:
        url = f"http://{domain}"
        response = requests.get(url, timeout=5)

    return response.headers

# domain = "anukampa.mp.gov.in"
# headers = GetHeaders(domain)
# print(headers)
