import socket
import re
from IPData import GetIPData
from WhoIs import GetWhois
from IPFinder import GetSiteIP

def ExtractDomain(url):
    domain = re.sub(r'^https?://', '', url)
    domain = re.sub(r'^www\.', '', domain)
    domain = domain.split('/')[0]
    return domain

def DomainCheck(domain):
    try:
        ip = socket.gethostbyname(domain)
        return ip
    except socket.gaierror:
        return None
    
def Main(url):
    domain = ExtractDomain(url)
    ip = DomainCheck(domain)

    print(domain)
    print(ip)

    if not ip:
        return None
    
    ipdata = GetIPData(ip)
    whoisdata = GetWhois(domain)

    print(ipdata)
    print(whoisdata)

    SiteIP = GetSiteIP(url, ip)
    print(SiteIP)

    return True

Main("1tamilblasters.fit")