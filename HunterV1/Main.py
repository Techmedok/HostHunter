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

from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

client = MongoClient("mongodb://HostHunterAdmin:2St7tHxcQJMHMsnDSJsXN7s1PxhnbHCR@161.97.70.226:27017/HostHunter")
db = client["HostHunter"]  

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

    # IP correlation among list of Censys IP's

    print(domain)
    print(ip)

    if not ip:
        return None
    
    ipdata = GetIPData(ip)
    print(ipdata)

    SiteIP = GetSiteIP(url, ip)
    print(SiteIP)

    whoisdata = GetWhois(domain)
    print(whoisdata)

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

    # ds = {
    #     "timestamp": datetime.now().isoformat(),
    #     "domain": whoisdata["domain"]["url"],
    #     "whois": whoisdata,
    #     "ipdata": ipdata,
    #     "dnsrecords": DNSRecords,
    #     "headers": Headers,
    #     "mailservers": {
    #         IncomingMails,
    #         OutgoingMails
    #     },
        # "siteanalysis": {

        # },

    # print(Metadata)
    # print(SocialLinks)
    # print(SiteTech)
    # print(SiteAnalysis)
    # print(OpenPorts)
    # print(SSLData)


    # }

    # db.reports.insert_one(ds)

    return True

Main("sih.gov.in")