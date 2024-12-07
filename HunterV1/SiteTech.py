# https://github.com/nmmapper/wappalyzer

from webappalyzer.Wappalyzer import Wappalyzer
from webappalyzer.webpage._bs4 import WebPage

def GetSiteTech(domain):
    url = "http://" + domain
    webpage = WebPage.new_from_url(url, verify = False)
    wappalyzer = Wappalyzer.latest() 
    tech = wappalyzer.analyze_with_categories(webpage) 
    return tech