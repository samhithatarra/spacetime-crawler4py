import re
from urllib.parse import urlparse
from lxml import html, etree
import requests
from utils.download import download
from bs4 import BeautifulSoup

master_lst = [] # contains list of every valid URL that is passed to the frontier
count_unique_url = 0 # tracks the number of total unique URLs
longest_page = "" # stores the URL of the longest page
num_words_longest_page = 0 # tracks number of tokens on the longest url
master_freq_dict = {} # stores all the tokens and tracks their frequency of appearance across all pages
master_subdomain_dict = {} # stores the subdomains of ics.uci.edu and the frequency of each


def scraper(url, resp):
    global num_words_longest_page
    global longest_page
    global count_unique_url
    global master_freq_dict
    global master_subdomain_dict

    find_lst=[]
    token_list = []
    lst = []
    
    # filters to only accept URLs from the frontier that have a webpage status of 200 (high quality)
    # adds to a list all the relevant webpage text (p,h1,h2) and tokenizes it
    # tokenizer removes non alphabetical characters and stopwords from webpage text

    if resp.status == 200:
        page = resp.raw_response.text
        soup = BeautifulSoup(page, "lxml")
        total_count = 0
        find_lst.extend([s for s in soup.findAll('p')])
        find_lst.extend([s for s in soup.findAll('h1')])
        find_lst.extend([s for s in soup.findAll('h2')])
        for s in find_lst:
            fin_text = ''.join(s.findAll(text=True))
            fin_text = fin_text.lower()
            fin_text = re.sub('[^a-zA-Z]+', ' ', fin_text)
            
            fin_text = re.sub(r"\b(a|about|above|after|again|against|all|am|an|and|any|are|aren't|as|"
                                + r"at|be|because|been|before|being|below|between|both|but|"
                                + r"by|can't|cannot|could|couldn't|did|didn't|do|"
                                + r"does|doesn't|doing|don't|down|during|each|few|for|from|further|had|hadn't|"
                                + r"has|hasn't|have|haven't|having|he|he'd|he'll|he's|her|here|here's|hers|"
                                + r"herself|him|himself|his|how|how's|i|i'd|i'll|i'm|i've|if|in|into|is|"
                                + r"isn't|it|it's|its|itself|let's|me|more|most|mustn't|my|myself|no|nor|not|of|off|on|"
                                + r"once|only|or|other|ought|our|ours|ourselves|out|over|own|"
                                + r"same|shan't|she|she'd|she'll|she's|should|shouldn't|so|some|such|than|that|"
                                + r"that's|the|their|theirs|them|themselves|then|there|there's|these|they|they'd|they'll|they're|"
                                + r"they've|this|those|through|to|too|under|until|up|very|was|wasn't|we|we'd|we'll|we're|we've|were|weren't|"
                                + r"what|what's|when|when's|where|where's|which|while|who|who's|whom|why|why's|with|won't|would|wouldn't|"
                                + r"you|you'd|you'll|you're|you've|your|yours|yourself|yourselves)\b", ' ', fin_text)
            
            for token in fin_text.split():
                if len(token) > 2:
                    token_list.append(token)
                    if token not in master_freq_dict.keys():
                        master_freq_dict[token] = 1
                    else:
                        master_freq_dict[token] += 1
            total_count += len(token_list)
            token_list = []
        
        # updates the respective global variable information for feedback report
        if total_count > num_words_longest_page:
            num_words_longest_page = total_count
            longest_page = url

        # ignores webpages that have low quality content (less than 100 tokens)
        # calls extract next links and adds to the frontier
        if total_count > 100 or url == "https://www.ics.uci.edu" or url == "https://www.cs.uci.edu" or url == "https://www.informatics.uci.edu" or url == "https://www.stat.uci.edu":
            master_lst.append(url)
            count_unique_url += 1
            
            # tracking subdomains of ics.uci.edu and frequency by adding to global dictionary
            parsed = urlparse(url)
            if(re.match(r"^.*\.ics.uci.edu$", parsed.netloc)):
                subdomain_tup = (parsed.netloc.split(".")[0], parsed.scheme)
                if subdomain_tup in master_subdomain_dict.keys():
                    master_subdomain_dict[subdomain_tup] += 1
                else:
                    master_subdomain_dict[subdomain_tup] = 1

     
            links = extract_next_links(url, resp)
            for link in links:
                if is_valid(link) and link not in master_lst:
                    lst.append(link)
    
    return lst

# converts 200 status webpages to html and extracts links that are connected
# returns the list of connected webpages
def extract_next_links(url, resp):
    lst = []
    
    if (resp.status == 200): #only want high quality content
        pages = resp.raw_response.content
        
        soup = BeautifulSoup(pages, 'lxml')
        
        
        for link in soup.findAll('a', href = True):
            lst.append(link['href'])
    
    return lst

# determines which URLs are valid
# only accepts valid domains and paths
# defragments URLs and deems certain extensions invalid
# recognizes wics is a crawler trap, and handles it explicitly
def is_valid(url):
    try:
        
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False


        if re.match(r"^.*\wics.ics.uci.edu$", parsed.netloc.lower()) and re.match(r"^(/event(s)?).*$", parsed.path.lower()):
            return False
        if parsed.query != '' and re.match(r"^.*\wics.ics.uci.edu$", parsed.netloc.lower()):
            if re.match(r"^share.*$", parsed.query.lower()):
                return False
        if re.match(r"^today.uci.edu$", parsed.netloc.lower()):
            if not re.match(r'^/department/information_computer_sciences/.*$', parsed.path.lower()):
                return False
        if re.match(r"^.*/pdf/.*$", parsed.path.lower()):
            return False
        
        if not re.match(r"^((?!ics.uci.edu|stat.uci.edu|cs.uci.edu|informatics.uci.edu|today.uci.edu).)*$", parsed.netloc.lower()):
            if parsed.fragment == '':
                return not re.match(
                    r".*\.(css|js|bmp|gif|jpe?g|ico"
                    + r"|png|tiff?|mid|mp2|mp3|mp4"
                    + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
                    + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
                    + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
                    + r"|epub|dll|cnf|tgz|sha1|ppsx"
                    + r"|thmx|mso|arff|rtf|jar|csv|in|java|py"
                    + r"|rm|smil|wmv|swf|wma|zip|rar|gz|r|c|txt|m|Z)$", parsed.path.lower())
            
           
        return False
    
    except TypeError:
        print ("TypeError for ", parsed)
        raise
