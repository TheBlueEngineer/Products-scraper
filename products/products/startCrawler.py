from scrapy.crawler import CrawlerProcess                           # Import the Crawler Process from scrapy
from products.products.spiders.productSpider import ProductSpider
import os
from bloo.fileMaster import readFile
from bloo.webMaster import getBaseURL, getDomain

# ************************
# *** GLOBAL VARIABLES ***
# ************************
# The spider's folder is considered the root when the execution take place
filenames = 'furniture_links.txt'
# Location where we will download all the content
location_URL = '../../extracted_dummy'
# How many lines from the links txt file is the program supposed to ignore
ignore_links = 1
# Number of retrieved links
no_links = 0
URLs = []
domains = []

# *********************
# *** MAIN FUNCTION ***
# *********************
DEV_MODE = 0
# Build the folder where you want to extract the data
if not os.path.exists(location_URL):
    os.makedirs(location_URL)

URLs = readFile( filenames, startLine=1, endLine=0, maxLines=no_links, debug=False)
baseURLs = getBaseURL( originalURL=URLs, debug=False)
domains = getDomain( baseURLs)

# Start the scraping process
if(DEV_MODE):
    pass
else:
    process = CrawlerProcess()
    process.crawl(ProductSpider, locationURL=location_URL, urls=baseURLs, domains=domains)
    process.start()
