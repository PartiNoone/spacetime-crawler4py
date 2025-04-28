import re
from urllib.parse import urlparse
from lxml import etree
from bs4 import BeautifulSoup
import json
from tokenizewords import tokenize_string
import wordcount

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
    '''
    Takes a full URL and the web page response. Returns a full list of
    all href links on that page.
    '''
    # this should run after is_valid_current(url,resp)
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code. 200 is OK, page served. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page
    soup = BeautifulSoup(resp.raw_response.content,'lxml')
    links = [link.get('href') for link in soup.find_all('a')]
    return links

def is_valid(url):
    '''
    If you decide to crawl this URL, return True; otherwise False.
    Crawler should avoid traps/loops/etc. Only crawl and record unique
    URLs only (defragmented)
    '''
    try:
        parsed = urlparse(url)

        if is_banned(parsed):
            return False
        
        defrag = defragment(parsed)
        defrag2 = defragment2(parsed, defrag)
        # Add the url to explored dict if not in it already. If it is, then return False.
        try:
            with open("explored.json", "r") as setfile:
                urls = json.load(setfile)
                if defrag in urls or defrag2 in urls:
                    return False
                urls[defrag] = 0
            with open("explored.json", "w") as setfile:
                json.dump(urls, setfile)
        except FileNotFoundError: # triggered when explored.json is empty, so should only run the first time running
            urls = {"https://www.ics.uci.edu":0,"https://www.cs.uci.edu":0,"https://www.informatics.uci.edu":0,"https://www.stat.uci.edu":0}
            if defrag in urls or defrag2 in urls:
                return False
            with open("explored.json", "w") as setfile: # should only run the first time that a new URL is found
                urls[defrag] = 0
                json.dump(urls, setfile)
        # Passed all filters, link seems valid
        return True
    except TypeError:
        print ("TypeError for ", parsed)
        raise
    except ValueError: # when urlparse(url) gives error msg'YOUR_IP' does not appear to be an IPv4 or IPv6 address
        return False

def is_banned(parsed):
    '''
    Helper for is_valid and can_be_frontier.
    Takes in a urlparsed URL and runs it through some filters.
    Returns True if it got caught by the filters.
    '''
    # url parses into scheme://netloc/path;params?query#fragment
    if parsed.scheme not in set(["http", "https"]):
        return True

    # add more specifications here? re.match(substring, string)
    if not re.match(
        # filter out non uci/ics sites
        # .* means any combination and number of characters
        # no $ sign because we want to allow a path
        r".*(ics.uci.edu|cs.uci.edu|informatics.uci.edu"
        + r"|stat.uci.edu|today.uci.edu/department/information_computer_sciences)"
        , (parsed.netloc + parsed.path).lower()):
        return True

    if re.match(
        # filter out unwanted pages, based on netloc+path
        r".*([0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]"          # any specific date
        + r"|ics\.uci\.edu/events/20[0-9][0-9]"                   # individual calendar days
        + r"|ics\.uci\.edu/events/week/20[0-9][0-9]"              # individual calendar days
        + r"|events/category/.*/20[0-9][0-9]"                     # individual calendar months
        + r"|events/category/.*/day"                              # individual calendar days
        + r"|isg\.ics\.uci\.edu/events/tag/talk/day"              # individual calendar days
        + r"|isg\.ics\.uci\.edu/events/tag/talks/day"             # individual calendar days
        + r"|isg\.ics\.uci\.edu/events/tag/talk/20[0-9][0-9]"     # individual calendar months
        + r"|isg\.ics\.uci\.edu/events/tag/talks/20[0-9][0-9]"    # individual calendar days
        + r"|isg\.ics\.uci\.edu/events/tag/talk/month"            # individual calendar months
        + r"|isg\.ics\.uci\.edu/events/tag/talks/month"           # individual calendar months
        + r"|isg\.ics\.uci\.edu/events/tag/talk/list"             # individual calendar days
        + r"|isg\.ics\.uci\.edu/events/tag/talks/list"            # individual calendar days
        + r"|ics\.uci\.edu/events/20[0-9][0-9]"                   # individual calandar days
        + r"|ics\.uci\.edu/events/month/20[0-9][0-9]"             # individual calendar months
        + r"|wics\.ics\.uci\.edu/events/20[0-9][0-9]"             # individual calendar days
        + r"|wics\.ics\.uci\.edu/events/month/20[0-9][0-9]"       # individual calendar months
        + r"|intranet\.ics\.uci\.edu/doku\.php$"                  # requires login
        + r"|intranet\.ics\.uci\.edu/doku\.php/personnel:start"   # requires login
        + r"|wp-login\.php"                                       # requires login
        + r"|sli\.ics\.uci\.edu"                                  # pages don't work
        + r")"
        , (parsed.netloc + parsed.path).lower()):
        return True

    if re.match(
        # filter out more unwanted pages, based on query
        r".*(ical=1"                      # downloads an outlook file and serves blank page
        + r"|date="                       # don't want individual dates
        + r"|[1-2][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]"
        + r"|share="                      # please don't take the bot to twitter or facebook
        + r")"
        , (parsed.query).lower()):
        return True

    if re.match(
        # filter out unwanted page formats
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
        + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", (parsed.path).lower()):
        return True
    return False

def defragment(parsed):
    '''
    Takes in a urlparsed url and returns the defragmented URL string.
    Removes the trailing slash (/) because sometimes two URLs that are
    the same except for a slash get double counted
    '''
    if type(parsed.scheme) is str:
        defrag = (parsed.scheme + '://' + parsed.netloc + parsed.path if (parsed.query == '')
                    else parsed.scheme + '://' + parsed.netloc + parsed.path + '?' + parsed.query)
        # Remove trailing /
        defrag = (defrag[0: -1] if (defrag[-1] == '/') else defrag)
    else: # for when the url is in bytes instead of string
        defrag = (parsed.scheme + b'://' + parsed.netloc + parsed.path if (parsed.query == b'')
                  else parsed.scheme + b'://' + parsed.netloc + parsed.path + b'?' + parsed.query)
        # Remove trailing /
        defrag = (defrag[0, -1] if (defrag[-1] == '/') else defrag)
    return defrag

def defragment2(parsed, defrag):
    '''
    Takes in a urlparsed url and defragmented url and returns
    the defragmented URL string using the other scheme.
    Sometimes two urls that are the same except for http vs. 
    https get double counted, so we'll try to minimize that
    with defrag2.
    '''
    if type(parsed.scheme) is str:
        defrag2 = 'http' + defrag[5:] if (parsed.scheme == 'https') else 'https' + defrag[4:]
    else: # for when the url is in bytes instead of string
        defrag2 = b'http' + defrag[5:] if (parsed.scheme == 'https') else b'https' + defrag[4:]
    return defrag2

def is_valid_current(url, resp):
    '''
    Takes in current url and response, returns True if we want to scrape it for links.
    
    Also processes current and adds it to subdomains, and counts words for explored.json
    and wordtotals.py.
    '''
    try:
        parsed = urlparse(url)
    except ValueError: # when urlparse(url) gives error msg'YOUR_IP' does not appear to be an IPv4 or IPv6 address
        return False

    defrag = defragment(parsed) # Won't need defrag2, since only defragmented1 is ever added to explored.json

    # Status != 200
    if (resp.status != 200):
        invalidate_in_explored(defrag)
        msg = f"Did not scrape {url} because status = {resp.status}"
        return (False, msg)
    soup = BeautifulSoup(resp.raw_response.content,'lxml')
    tokens = tokenize_string(soup.get_text(" ", strip=True)) # long list of words
    
    # Has < 100 words
    numwords = len(tokens)
    if numwords < 100:
        invalidate_in_explored(defrag)
        msg = f"Did not scrape {url} because number of words {numwords} < 100"
        return (False, msg)

    # look for textual similarity
    # look at tokens[10-31]; if their checksum is same, return false
    checksum = 0
    for i in range(10, 31):
        word = tokens[i]
        for c in word:
            checksum += ord(c)
    try:
        with open("sumhash.json", "r") as setfile:
            sums = json.load(setfile)
        if checksum in sums:
            invalidate_in_explored(defrag)
            msg = f"Did not scrape {url} because checksum {checksum} already exists"
            return (False, msg)
        sums[checksum] = 0
        with open("sumhash.json", "w") as setfile:
            json.dump(sums, setfile)
    except FileNotFoundError: # triggered when sumhash.json is empty, so should only run the first time running
        sums = {checksum:0}
        with open("sumhash.json", "w") as setfile:
            json.dump(sums, setfile)

    # Seems valid: add to subdomains
    subdom = parsed.netloc
    try:
        with open("subdomains.json", "r") as setfile:
            subs = json.load(setfile)
        subs[subdom] = subs[subdom] + 1 if (subdom in subs) else 1
        with open("subdomains.json", "w") as setfile:
            json.dump(subs, setfile)
    except FileNotFoundError: # triggered when subdomains.json is empty, so should only run the first time running
        subs = {"www.ics.uci.edu":0,"www.cs.uci.edu":0,"www.informatics.uci.edu":0,"www.stat.uci.edu":0}
        subs[subdom] = subs[subdom] + 1 if (subdom in subs) else 1
        with open("subdomains.json", "w") as setfile: # should only run the first time that a new URL is found
            json.dump(subs, setfile)

    # Count the number of words in the URL for explored.json and the word frequencies for wordtotals.json
    count_words(defrag, numwords, tokens)
    return (True, 'pass')

def count_words(defrag, numwords, token_list):
    '''
    Takes defragmented URL, number of words, and token list.
    Adds file's number of words to the explored.json dict's values
    and word frequencies to wordtotals.json.
    
    '''
    # updating explored.json values with numwords
    try:
        # explored.json might not exist, but defrag will be in it if it does
        with open("explored.json", "r") as setfile:
            urls = json.load(setfile)
        urls[defrag] = numwords
        with open("explored.json", "w") as setfile:
            json.dump(urls, setfile)
    except FileNotFoundError: # will only trigger the first time a seed url is processed and nothing is removed
        # urls = {"https://www.ics.uci.edu":0,"https://www.cs.uci.edu":0,"https://www.informatics.uci.edu":0,"https://www.stat.uci.edu":0}
        urls = {}
        urls[defrag] = numwords
        with open("explored.json", "w") as setfile: # should only run the first time that a new URL is found
            json.dump(urls, setfile)

    # updating wordtotals.json with word frequencies
    try:
        # wordtotals.json might not exist, but defrag will be in it if it does
        with open("wordtotals.json", "r") as setfile:
            token_map = json.load(setfile)
        update_token_map(token_map, token_list)
        with open("wordtotals.json", "w") as setfile:
            json.dump(token_map, setfile)
    except FileNotFoundError: # will only trigger the first time a seed url is processed and nothing is removed
        token_map = {}
        update_token_map(token_map, token_list)
        with open("wordtotals.json", "w") as setfile: # should only run the first time that a new URL is found
            json.dump(token_map, setfile)

def update_token_map(token_map, token_list):
    '''
    Takes a token dict and a token list and adds all the
    tokens from the list into the dict.
    '''
    # Code from tracy's Assignment 1 Part A
    token_list = [token.lower() for token in token_list]
    for token in token_list:
        if token.isnumeric():
            continue # the report asks for 50 most common WORDS! AND A NUMBER ISN'T A WORD
        if token in token_map:
            token_map[token] += 1
        else:
            token_map[token] = 1

def invalidate_in_explored(defrag):
    '''
    Set the given defragmented URL value in file explored.json to -1.
    If no file exists, create one with the seed URLs and set that
    to -1. -1 means invalid and will not be counted at the very end
    of scraped unique URLs.
    '''
    try:
        with open("explored.json", "r") as setfile:
            urls = json.load(setfile)
        urls[defrag] = -1
        with open("explored.json", "w") as setfile:
            json.dump(urls, setfile)
    except FileNotFoundError: # will only trigger the first time a seed url is processed and removed
        # urls = {"https://www.ics.uci.edu":0,"https://www.cs.uci.edu":0,"https://www.informatics.uci.edu":0,"https://www.stat.uci.edu":0}
        urls = {}
        urls[defrag] = -1
        with open("explored.json", "w") as setfile: # should only run the first time that a new URL is found
            json.dump(urls, setfile)

def can_be_frontier(url):
    '''
    For use in Frontier.py. Meant to be used to see if a URL (which will be present in explored.json)
    is allowed to be in the frontier. Return True if it can stay in the frontier,
    return False if we don't want it.
    Generally, this will run when explored.json has things in it.
    '''
    try:
        parsed = urlparse(url)
        if (is_banned(parsed)):
            return False
        defrag = defragment(parsed)
        defrag2 = defragment2(parsed, defrag)
        try:
            with open("explored.json", "r") as setfile:
                urls = json.load(setfile)
            # If a URL was added to explored.py (discovered) but not processed, then
            # its dict value should still be 0. Therefore val == 0 means it was on the
            # frontier
            if defrag in urls:
                return (False if urls[defrag] != 0 else True)
            if defrag2 in urls:
                return (False if urls[defrag2] != 0 else True)
        except FileNotFoundError: # generally explored.json will always exist so this shouldn't activate but let's be safe
            return True
        return True
    except TypeError:
        print ("TypeError for ", parsed)
        raise
