import re
from urllib.parse import urlparse
from lxml import etree
from bs4 import BeautifulSoup
import json

def scraper(url, resp):
    # return list of urls to add to the frontier
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
        # TODO: MAYBE CALL A FUNCTION THAT TAKES SOUP AND URL, COUNTS ALL THE WORDS, AND THEN SAVES THAT TO A FILE (for 50 most common words in space and longest page)
        return links
    return list()

def is_valid(url): # TODO: MAYBE CHANGE THE SIGNATURE TO TAKE IN A RESPONSE OR TO CALL A RESPONSE TO CHECK IF IT'S A DEAD PAGE
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # Add things to it to help crawler avoid traps/loops/etc.
    # For this, I am deciding to only crawl and record unique URLs only (defragmented)
    try:
        parsed = urlparse(url)
        if type(parsed.scheme) is str:
            defrag = (parsed.scheme + '://' + parsed.netloc + parsed.path if (parsed.query == '')
                      else parsed.scheme + '://' + parsed.netloc + parsed.path + '?' + parsed.query)
        else: # for when the url is in bytes instead of string
            defrag = (parsed.scheme + b'://' + parsed.netloc + parsed.path if (parsed.query == b'')
                      else parsed.scheme + b'://' + parsed.netloc + parsed.path + b'?' + parsed.query)
        # y = 0 if (x < 100) else x
        # url parses into scheme://netloc/path;params?query#fragment
        # path does include the first slash after netloc
        # we want to ignore fragments when counting unique pages
        if parsed.scheme not in set(["http", "https"]):
            return False

        # add more specifications here? re.match(substring, string)
        if not re.match(
            # filter out non uci/ics sites
            # .* means any combination and number of characters
            # no $ sign because we want to allow a path
            r".*(ics.uci.edu|cs.uci.edu|informatics.uci.edu"
            + r"|stat.uci.edu|today.uci.edu/department/information_computer_sciences)"
            , (parsed.netloc + parsed.path).lower()):
            return False

        if re.match(
            # filter out unwanted pages
            r".*(isg.ics.uci.edu/events/tag/talk/day"              # individual calendar days
            + r"|isg.ics.uci.edu/events/tag/talks/day"             # individual calendar days
            + r"|isg.ics.uci.edu/events/tag/talk/20"               # individual calendar months
            + r"|isg.ics.uci.edu/events/tag/talks/20"              # individual calendar days
            + r"|isg.ics.uci.edu/events/tag/talk/month"            # individual calendar months
            + r"|isg.ics.uci.edu/events/tag/talks/month"           # individual calendar months
            + r"|isg.ics.uci.edu/events/tag/talk/list"             # individual calendar days
            + r"|isg.ics.uci.edu/events/tag/talks/list"            # individual calendar days
            + r"|intranet.ics.uci.edu/doku.php$"                   # requires login
            + r"|intranet.ics.uci.edu/doku.php/personnel:start"    # requires login
            + r"|sli.ics.uci.edu"                                  # pages don't work
            + r").*"
            , (parsed.netloc + parsed.path).lower()):
            return False

        if re.match(
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
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", (parsed.path).lower()): # TODO: SHOULD I CHANGE PARSED.PATH TO THE WHOLE URL ENDING?
            return False

        # Add the url to explored dict if not in it already. If it is, then return False.
        try:
            with open("explored.json", "r") as setfile:
                urls = json.load(setfile)
                if defrag in urls:
                    return False
                urls[defrag] = 0
            with open("explored.json", "w") as setfile:
                json.dump(urls, setfile)
        except FileNotFoundError: # triggered when explored.json is empty, so should only run the first time running
            urls = {"https://www.ics.uci.edu":0,"https://www.cs.uci.edu":0,"https://www.informatics.uci.edu":0,"https://www.stat.uci.edu":0,
                    "http://www.ics.uci.edu":0,"http://www.cs.uci.edu":0,"http://www.informatics.uci.edu":0,"http://www.stat.uci.edu":0}
            if defrag in urls:
                return False
            with open("explored.json", "w") as setfile: # should only run the first time that a new URL is found
                urls[defrag] = 0
                json.dump(urls, setfile)
        # Passed all filters, link seems valid
        print(f"Passed: {parsed.netloc}{parsed.path}")
        return True
    except TypeError:
        print ("TypeError for ", parsed)
        raise
