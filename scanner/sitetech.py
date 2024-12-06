# https://github.com/nmmapper/wappalyzer

from webappalyzer.Wappalyzer import Wappalyzer
from webappalyzer.webpage._bs4 import WebPage

def SiteTech(url):
    webpage = WebPage.new_from_url(url)
    wappalyzer = Wappalyzer.latest() 
    tech = wappalyzer.analyze_with_categories(webpage) 
    return tech

# url = 'http://techmedok.com'
# print(SiteTech(url))