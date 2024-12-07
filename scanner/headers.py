import requests

def get_site_headers(url):
    try:
        response = requests.get(url)
        headers = response.headers
        return headers
    
    except requests.RequestException as e:
        print(f"An error occurred: {e}")

# url = "https://techmedok.com"
# site_headers = get_site_headers(url)
# print(site_headers)