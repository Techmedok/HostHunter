import socket
import re
from IPData import GetIPData
from WhoIsData import GetWhois
from IPFinder import GetSiteIP
from DNSData import GetDNSRecords
from SiteData import GetSiteDataAndHeaders
from MailServerData import GetMaiServerData
from MetaData import GetMetaData
from SocialLinks import ExtractSocialLinks
from SiteTech import GetSiteTech
from SiteAnalysis import GetSiteAnalysis
from PortScanning import GetOpenPorts
from SSLData import GetSSLData

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
    print(ipdata)

    whoisdata = GetWhois(domain)
    print(whoisdata)

    SiteIP = GetSiteIP(url, ip)
    print(SiteIP)

    DNSRecords = GetDNSRecords(domain)
    print(DNSRecords)

    Headers, Content = GetSiteDataAndHeaders(domain)
    print(Headers)
    print(Content[:200])

    IncomingMails, OutgoingMails = GetMaiServerData(domain)
    print(IncomingMails)
    print(OutgoingMails)
    
    Metadata = GetMetaData(Content)
    print(Metadata)

    SocialLinks = ExtractSocialLinks(Content)
    print(SocialLinks)

    SiteTech = GetSiteTech(domain)
    print(SiteTech)

    SiteAnalysis = GetSiteAnalysis(Content)
    print(SiteAnalysis)

    OpenPorts = GetOpenPorts(ip)
    print(OpenPorts)

    SSLData = GetSSLData(domain)
    print(SSLData)

    return True

Main("sih.gov.in")