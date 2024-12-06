# from urllib.parse import urlparse
# import re

# def extract_domain(url):
#     parsed_url = urlparse(url)
#     domain = parsed_url.netloc or parsed_url.path

#     if domain.startswith('www.'):
#         domain = domain[4:]

#     domain = domain.rstrip('/')

#     if not re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', domain):
#         return None
    
#     return domain


# # Test cases
# urls = [
#     "https://chatgpt.com/c/",
#     "https://chatgpt.com/c/675110a6-634c-800e-8c02-7b1ae0542734",
#     "https://www.chatgpt.com/",
#     "https://chatgpt.com/",
#     "chatgpt.com/",
#     "https://www.htp.com/s//e/e//e/e/e",
#     "http:s/ads.cpm"
# ]

# # Apply the function to each URL
# results = [extract_domain(url) for url in urls]
# print(results)


from datetime import datetime

# Print the current timestamp in ISO 8601 format
timestamp = datetime.now().isoformat()
print("Current Timestamp:", timestamp)

# If managing a list of timestamps:
timestamps = [
    "2024-12-05T08:30:00",
    "2023-11-30T12:15:45",
    "2024-01-01T00:00:00",
    "2024-12-05T09:00:00"
]

# Sort timestamps (ISO 8601 format is naturally sortable)
sorted_timestamps = sorted(timestamps)
print("Sorted Timestamps:", sorted_timestamps)
