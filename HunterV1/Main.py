import socket
from HunterV1.IPData import GetIPData
from HunterV1.WhoIsData import GetWhois
from HunterV1.IPFinder import GetSiteIP
from HunterV1.DNSData import GetDNSRecords
from HunterV1.SiteData import GetSiteDataAndHeaders
from HunterV1.MailServerData import GetMaiServerData
from HunterV1.MetaData import GetMetaData
from HunterV1.SocialLinks import ExtractSocialLinks
from HunterV1.SiteTech import GetSiteTech
from HunterV1.SiteAnalysis import GetSiteAnalysis
from HunterV1.PortScanning import GetOpenPorts
from HunterV1.SSLData import GetSSLData

def DomainCheck(domain):
    try:
        ip = socket.gethostbyname(domain)
        return ip
    except socket.gaierror:
        return None
 
def Main(domain, RandomID, timestamp, mongo):
    ip = DomainCheck(domain)

    # IP correlation among list of Censys IP's

    print(domain)
    print(ip)

    if not ip:
        return None
    
    ipdata = GetIPData(ip)
    print(ipdata)

    SiteIP = GetSiteIP(domain, ip)
    print(SiteIP)

    whoisdata = GetWhois(domain)
    print(whoisdata)

    DNSRecords = GetDNSRecords(domain)
    print(DNSRecords)

    Headers, Content = GetSiteDataAndHeaders(domain)
    print(Headers)
    # print(Content[:200])

    IncomingMails, OutgoingMails = GetMaiServerData(domain)
    print(IncomingMails)
    print(OutgoingMails)
    
    if Content:
        Metadata = GetMetaData(Content)
        print(Metadata)

        SocialLinks = ExtractSocialLinks(Content)
        print(SocialLinks)

        SiteTech = GetSiteTech(domain)
        print(SiteTech)

        SiteAnalysis = GetSiteAnalysis(Content)
        print(SiteAnalysis)
    else:
        Metadata = None
        SocialLinks = None
        SiteTech = None
        SiteAnalysis = None

    OpenPorts = GetOpenPorts(ip)
    print(OpenPorts)

    SSLData = GetSSLData(domain)
    print(SSLData)

    ds = {
        "id": RandomID,
        "timestamp": timestamp,
        "url": whoisdata["domain"]["url"],
        "status": "completed",
        "ip": ip,
        "whois": whoisdata,
        "ipdata": ipdata,
        "dnsrecords": DNSRecords,
        "mailservers": {
            "incoming": IncomingMails,
            "outgoing": OutgoingMails
        },
        "ssl": SSLData,
        "metadata": Metadata,
        "headers": Headers,
        "siteanalysis": {
            "sociallinks": SocialLinks,
            "sitetech": SiteTech,
            "summary": SiteAnalysis["summary"] if SiteAnalysis else None,
            "description": SiteAnalysis["description"] if SiteAnalysis else None,
            "keywords": SiteAnalysis["keywords"] if SiteAnalysis else None,
            "category": SiteAnalysis["site_category"] if SiteAnalysis else None,
        },
        "openports": OpenPorts,
    }

    mongo.db.reports.update_one({"id": RandomID}, {"$set": ds})

    return True