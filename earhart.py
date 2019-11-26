# python -m pip install -U pip
# python -m pip install -U google

# TODO:
#   Regex pattern matching blacklist
#   Regex pattern mathcing search
#   Multiple search querries
#   More tunable options (maxSites) on run time

import requests
import os
import sys
import re
import operator
from html.parser import HTMLParser

from googlesearch import search

class DataParser(HTMLParser):
    def __init__(self):
        self.uniqueWords = {}
        return super().__init__()

    def handle_data(self, data):
        words = re.sub("\W", " ", data.lower()).split(" ")
        for word in words:
            try:
                int(word, 16)
                continue
            except:
                pass
            if len(word) < 3 or len(word) > 16 or word in blacklist: continue
            if word not in self.uniqueWords:
                self.uniqueWords[word] = 0
            self.uniqueWords[word] += 1

def parseSite(currSite):
    global searchedSites, parser
    searchedSites.add(currSite)
    print("Searching site {}/{}: {}".format(len(searchedSites), maxSites, currSite))
    response = requests.get(currSite)
    try:
        htmlData = response.content.decode("utf-8")
        parser.feed(htmlData)
    except:
        print("Error decoding response")
    

# Globals
searchedSites = set()
siteDepth = 1
searchDepth = 1
maxLinksPerSite = 1000
maxSites = 25
blacklist = tuple()
predefSites = ["http://www.facebook.com/{}",
               "http://www.twitter.com/{}",
               "http://www.rabb.it/{}",
               "http://www.github.com/{}",
               "http://www.instagram.com/{}",
               "http://www.imgur.com/user/{}/posts",
               "http://www.twitch.tv/{}",
               "http://www.reddit.com/u/{}",
               "http://www.voat.co/u/{}",
               "http://www.photobucket.com/user/{}/profile",
               "http://www.myspace.com/{}",
               "http://www.pinterest.com/{}",
               "http://www.steamcommunity.com/id/{}",
               "http://www.last.fm/user/{}",
               "http://www.soundcloud.com/{}",
               "http://www.myanimelist.net/profile/{}"]

# Get user input
queryString = input("Query string: ")
usePredefSites = input("Use predefined sites [Y/n]: ")
useBlacklist = input("Use blacklist [Y/n]: ")
try:
    minWordFreq = int(input("Minimum word frequency [1]: "))
except:
    minWordFreq = 1
    
# Load blacklist
if not useBlacklist == "n":
    try:
        with open("blacklist.txt", "r") as blFile:
            blacklist = tuple(blFile.read().split("\n"))
        print("Blacklist successfully loaded")
    except:
        print("Could not load blacklist")

# Collect data from predef sites
parser = DataParser()
if not usePredefSites.lower() == "n":
    for site in predefSites:
        currentSite = site.format(queryString)
        parseSite(currentSite)

# Collect data from search engine results
remainCount = maxSites-len(searchedSites)
for currentSite in search(queryString, tld="com", num=remainCount, stop=remainCount, pause=2):
    parseSite(currentSite)
    
print("No more sites to search")

# Process and sort data
sortedWords = sorted(parser.uniqueWords.items(), key=operator.itemgetter(1), reverse=True)

# Save output
saveName = "earhart-results-" + queryString + ".txt"
saveNumber = 1
while(os.path.isfile(saveName)):
    saveNumber += 1
    saveName = "earhart-results-" + queryString + "-" + str(saveNumber) + ".txt"
with open(saveName, "wb") as file:
    for wordData in sortedWords:
        if wordData[1] < minWordFreq: break
        file.write("{} {}\n".format(wordData[0], wordData[1]).encode("utf-8"))
print("Results successfully saved as:", saveName)
