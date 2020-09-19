# **********************************
# *** GET THE DOMAIN FROM AN URL ***
# **********************************
def getDomain( links, removeHTTP = True, debug = False):
    # Import the required libraries for this function
    from urllib.parse import urlparse
    domains = []

    # If the link is a string
    if isinstance( links, str):
        link_parsed = urlparse(links)
        if removeHTTP:
            domains.append(f"{link_parsed.netloc}")
        else:
            domains.append(f"{link_parsed.scheme}://{link_parsed.netloc}")
        return domains[0]

    # IF WE PASS A LIST WE WANT TO ITERATE THROUGH IT
    elif isinstance( links, list):
        # Iterate through all the links list to get the domains
        for link in links:
            link_parsed = urlparse(link)
            if removeHTTP:
                domains.append(f"{link_parsed.netloc}")
            else:
                domains.append(f"{link_parsed.scheme}://{link_parsed.netloc}")
            if(debug):
                print("Got domain: %s" % ( domains[-1]))
        return domains
    else:
        raise TypeError("Link(s) must be of type <str> or <list>")

# *******************************
# *** GET THE BASE OF THE URL ***
# *******************************
def getBaseURL( originalURL, debug = False):
    # IMPORT THE LIBRARIES
    from urllib.parse import urlsplit

    # DECLARE THE VARIABLES
    listInitialURLs = []
    listFinalURLS = []

    # SEPARATION BASED ON DATATYPE
    if isinstance( originalURL, str):
        listInitialURLs.append(originalURL)
    elif isinstance( originalURL, list):
        for URL in originalURL:
            listInitialURLs.append(URL)
    else:
        raise TypeError("Variable 'filePath' must be <str> or <list>")

    # START THE FUNCTION
    for curr_URL in listInitialURLs:
        if (debug):
            print("Original URL: %s" % ( str(curr_URL)))

        splitURL = urlsplit( curr_URL)
        reformedURL = f"{splitURL.scheme}://{splitURL.netloc}/"

        if(debug):
            print("Reformed URL: %s" % ( reformedURL))
        listFinalURLS.append( reformedURL)

    # RETURN TYPES BASED ON THE DATATYPE
    if isinstance( originalURL, str) and len( listInitialURLs) == 1:
        return listFinalURLS[0]
    elif isinstance( originalURL, list) and len(listInitialURLs) > 1:
        return listFinalURLS
    else:
        ValueError("The function could not return a <str> or <list> type variable.")

# *************************************
# *** GET THE LAST PART FROM AN URL ***
# *************************************
def getPathEndURL( URL, debug=False):
    lastCharacter = "/"
    if URL[-1] == "/":
        if(debug):
            print("Found last character \"%s\" in URL: %s" % ( lastCharacter, URL))
        URL = URL[:-1]
    # Get the last part of the URL path
    return URL.split("/")[-1]