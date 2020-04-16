import re
from urllib.parse import urlparse
from lxml import html
import requests

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation requred.
    lst = []

    request = requests.get(url)
    pages = html.fromstring(request.content)
    if (resp.status ==200 and resp.raw_response.content == None):
        print("THIS IS A 200 AND NONE ERROR")
    elif (resp.status == 200 and resp.raw_response.content != None) or (resp.status != 200):
        for link in pages.xpath('//a/@href'):
            lst.append(link)



    return lst

def is_valid(url):
    
    try:
        
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        
        if not re.match(r"^((?!ics.uci.edu|stat.uci.edu|cs.uci.edu|informatics.uci.edu).)*$", parsed.netloc.lower()) or (not re.match(r"^((?!today.uci.edu).)*$", parsed.netloc.lower()) and re.match(r'^/department/information_computer_sciences$', parsed.path.lower())):
        

        
        
            return not re.match(
                r".*\.(css|js|bmp|gif|jpe?g|ico"
                + r"|png|tiff?|mid|mp2|mp3|mp4"
                + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
                + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
                + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
                + r"|epub|dll|cnf|tgz|sha1"
                + r"|thmx|mso|arff|rtf|jar|csv"
                + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())
            
        return False
    
    except TypeError:
        print ("TypeError for ", parsed)
        raise

