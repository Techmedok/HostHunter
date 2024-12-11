import logging
from bs4 import BeautifulSoup

logging.basicConfig(filename='app.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def GetMetaData(contents):
    try:
        soup = BeautifulSoup(contents, 'html.parser')

        metadata = {
            "title": soup.title.string if soup.title else "No title",
            "description": soup.find("meta", attrs={"name": "description"}).get("content", "No description") 
                            if soup.find("meta", attrs={"name": "description"}) else "No description",
            "keywords": soup.find("meta", attrs={"name": "keywords"}).get("content", "No keywords")
                            if soup.find("meta", attrs={"name": "keywords"}) else "No keywords",
            "author": soup.find("meta", attrs={"name": "author"}).get("content", "No author")
                            if soup.find("meta", attrs={"name": "author"}) else "No author",
            "viewport": soup.find("meta", attrs={"name": "viewport"}).get("content", "No viewport")
                            if soup.find("meta", attrs={"name": "viewport"}) else "No viewport",
            "charset": soup.meta.get("charset", "No charset") if soup.meta else "No charset",
            "robots": soup.find("meta", attrs={"name": "robots"}).get("content", "No robots")
                            if soup.find("meta", attrs={"name": "robots"}) else "No robots",
            "canonical": soup.find("link", attrs={"rel": "canonical"}).get("href", "No canonical")
                            if soup.find("link", attrs={"rel": "canonical"}) else "No canonical",
            "favicon": soup.find("link", attrs={"rel": "icon"}).get("href", "No favicon")
                            if soup.find("link", attrs={"rel": "icon"}) else "No favicon",
            "language": soup.html.get("lang", "No language") if soup.html else "No language",
        }

        og_tags = soup.find_all("meta", attrs={"property": lambda x: x and x.startswith("og:")})
        metadata["open_graph"] = {tag["property"]: tag["content"] for tag in og_tags if "content" in tag.attrs}

        twitter_tags = soup.find_all("meta", attrs={"name": lambda x: x and x.startswith("twitter:")})
        metadata["twitter"] = {tag["name"]: tag["content"] for tag in twitter_tags if "content" in tag.attrs}

        return metadata

    except Exception as e:
        logging.error(f"Error extracting metadata: {e}")
        return {}