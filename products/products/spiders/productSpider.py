# ************************
# *** IMPORT LIBRARIES ***
# ************************
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urlparse
import os
import re
import json

# **********************************
# *** BUILD CLASS PRODUCT SPIDER ***
# **********************************
class ProductSpider(CrawlSpider):
    # VARIABLES
    no_pages = 0
    locationURL = ""
    locationURL_current = ""
    locationDomain_current = ""
    locationText_current = ""
    name = "product_spider"     # Unique identifier for the spider
    start_urls = []             # An empty list for the starting URLs, we will control this variable from the constructor
    allowed_domains = []

    # CONSTRUCTOR
    def __init__(self, locationURL=None, urls=None, domains=None, *args, **kwargs):
        self.locationURL = locationURL                      # The directory in which we will save the URLs
        self.start_urls.extend(urls)                        # Update the list of start_urls
        self.allowed_domains.extend( domains)               # Update the list of domains
        super().__init__(*args, **kwargs)                   # Inherit the args and kwargs

    # Establish the rules that must be followed by the Spider
    rules = [
        Rule(LinkExtractor( allow=['products/', 'product/', 'global/'],
                            deny=['\?', '/page', r'\/\d+']),
                            callback='parse_item',
                            follow=True)
    ]

    # METHODS
    @classmethod
    def getCurrentDomain(self, response, removeHTTP = True):# Get the current domain that is being processed
        uri = urlparse(response.url)
        if removeHTTP:
            domain = f"{uri.netloc}"
        else:
            domain = f"{uri.scheme}://{uri.netloc}"
        return domain

    @classmethod
    def cleanItem(self, text):
        text = re.sub(r"\\n", " ", text)
        text = re.sub(r"[^\x00-\x7f]", " ", text)
        text = text.strip()
        return text

    # Decide what we are going to do with the response from the crawler
    def parse_item(self, response):
        domain = self.getCurrentDomain(response, True)                      # Get the domain of the currently iterated page

        self.locationDomain_current = os.path.join( self.locationURL, domain)

        if not os.path.exists(self.locationDomain_current):     # Build the domain folder if it doesn't exist
            os.mkdir( self.locationDomain_current)

        # We need to create custom folders for all the websites, so we better visualize the data
        currentFolder = os.path.join( self.locationDomain_current, "page"+ str(self.no_pages))
        self.no_pages += 1
        if not os.path.exists( currentFolder):
            os.mkdir( currentFolder)

        # Open the text.txt file and start to write the page
        file_text = currentFolder+"/text.json"                          # get the name of the file where we will write the text
        with open(file_text, 'a', encoding="utf-8") as ft:              # Open the file for the currently iterated website
            data = response.text                                        # Get the response of the page
            headers1 = response.xpath("//body//h1//text()").extract()
            headers2 = response.xpath("//body//h2//text()").extract()
            headers3 = response.xpath("//body//h3//text()").extract()
            paragraph = response.xpath("//body//p//text()").extract()
            spans = response.xpath("//body//span//text()").extract()

            newList = headers1 + headers2 + headers3 + paragraph + spans
            processedList = []

            for item in newList:
                if item.strip():
                    processedList.append( self.cleanItem(item))

            data = {
                "url": response.url,
                "sentences": processedList
            }
            data = {"data": data}
            json.dump( data, ft)

        # Open the URL.txt file and start to write the URLs
        file_url = self.locationDomain_current+"/url.txt"       # get the name of the file where we will write the URLs
        with open(file_url, 'a') as fu:                         # Open the file where we write the URLs
            fu.write(response.url+"\n")

