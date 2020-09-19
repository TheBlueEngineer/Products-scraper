# ********************
# *** WORD COUNTER ***
# ********************
def wordCounter( text, minWords = 1):
    no_words = len( text.split())
    if no_words >= minWords:
        return no_words
    else:
        return 0

# *********************************
# *** CHARACTER COUNTER COUNTER ***
# *********************************
def characterCounter( text, minCharacters = None, whitespaceIgnore = True):
    counter = 0
    for char in text:
        if char != " " and whitespaceIgnore:
            counter += 1
        else:
            counter += 1
    return counter

# ****************************
# *** ADD TWO DICTIONARIES ***
# ****************************
def addDict(dict1, dict2):
    for key, value in dict1.items():
        dict1[key] += dict2[key]
    return dict1

# ****************************************************
# *** GET ALL THE WORD COMBINATIONS FOR OUR SEARCH ***
# ****************************************************
def getNgrams( words, minWords = 2, maxWords = 0, debug = False):
    list_ngrams = []
    if maxWords != 0:
        if maxWords > len(words):
            noWords = maxWords
        else:
            noWords = len(words)
    else:
        noWords = len(words)

    # Iterate through all the possible lengths that the ngrams can  take
    for currentLength in range( noWords, minWords - 1, -1):
        if(debug):
            print("Current length: %i" % (currentLength))

        for currentIndex in range( noWords - currentLength, -1, -1):
            if(debug):
                print("Current index: %i" % (currentIndex))
            subList = words[ currentIndex: currentIndex + currentLength]
            ngram_dummy = " ".join(map(str, subList))
            if(debug):
                print("Current NGRAM: %s" % (ngram_dummy))
            list_ngrams.append( ngram_dummy)

    if (debug):
        print("The list of combinations: %s" % ( list_ngrams))
    if not list_ngrams:
        return 0
    else:
        return list_ngrams