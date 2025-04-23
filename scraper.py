import re
from urllib.parse import urlparse
from lxml import etree
from bs4 import BeautifulSoup
import json

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

# Honor the politeness delay for each site
# Crawl all pages with high textual information content
# Detect and avoid infinite traps
# Detect and avoid sets of similar pages with no information
# Detect and avoid dead URLs that return a 200 status but no data

# main focus: extract links
def extract_next_links(url:str, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code. 200 is OK, page served. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page
    if resp.status == 200:
        soup = BeautifulSoup(resp.raw_response.content,'lxml')
        links = [link.get('href') for link in soup.find_all('a')]
        # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
        # only include links if they pass is_valid
        # DEBUG THINGS---------------------------------------------------------------------
        # print(f"Currently extracting links from {url}.")
        # print(f"Links found:")
        for link in links:
            print(f"\t{link}")
        for i in range(len(links) - 1, -1,-1):
            if not is_valid(links[i]):
                links.pop(i)
        # DEBUG THINGS---------------------------------------------------------------------
        # print(f"Valid links:")
        for link in links:
            print(f"\t{link}")
        return links
    return list()

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # Add things to it to help crawler avoid traps/loops/etc.
        # Only crawl these:
        # *.ics.uci.edu/* netloc
        # *.cs.uci.edu/* netloc
        # *.informatics.uci.edu/* netloc
        # *.stat.uci.edu/* netloc
        # today.uci.edu/department/information_computer_sciences/*
        # Ex. such as https://ics.uci.edu/academics/undergraduate-programs/
        # Ex. vision.ics.uci.edu/
    try:
        parsed = urlparse(url)
        # url parses into scheme://netloc/path;parameters?query#fragment
        # we want to ignore fragments when counting unique pages
        if parsed.scheme not in set(["http", "https"]):
            return False

        # add more specifications here? re.match(substring, string)
        if not re.match(
            # .* means any combination and number of characters
            # no $ sign because we want to allow a path
            r".*(ics.uci.edu|cs.uci.edu|informatics.uci.edu"
            + r"|stat.uci.edu|today.uci.edu/department/information_computer_sciences)"
            , (parsed.netloc + '/' + parsed.path).lower()):
            return False

        if re.match( # returns the first occurrence of a substring in the string and ignore others
            # .* means any combination and number of characters
            # \. means a dot
            # $ means end of string; so "jpeg" matches "me.jpeg" but not "me.jpeg2"
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()):
            return False

        # Add the url to a set
        with open("explored.json", "w+") as setfile:
            urls = json.load(setfile)
            urls.add(url)
            setfile.dump(urls)

        return True
    except TypeError:
        print ("TypeError for ", parsed)
        raise
