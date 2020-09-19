import json
import re
import os
from dictionaryFurniture import furniture1W, furniture2W, furniture3W
from bloo.webMaster import getPathEndURL, getDomain
from bloo.utilityMaster import wordCounter, addDict, getNgrams
from bloo.fileMaster import getFiles, output

# ************************
# *** GLOBAL VARIABLES ***
# ************************
template = {
    "no_sentences_with_entities": 0,
    "no_sentences_without_entities": 0,
    "no_entities_possibility": 0,
    "no_entities_dictionary": 0,
    "ignored_ngrams": 0,
    "accepted_ngrams": 0,
}

# ***********************
# *** FILTER THE TEXT ***
# ***********************
def filter( sentences, debug=False):
    filteredList = []       # Declare the list with the filtered sentences
    filteredText = ""       # Declare an empty string as dummy variable for the filteredText
    for sentence in sentences:
        filteredText = sentence.lower()                             # Set the textual data to lower form
        filteredText = re.sub(r"\\n|\\r\\n", " ", filteredText)     # Remove all the newlines
        filteredText = re.sub(r"[^\w\s]" , " ", filteredText)       # Filter the punctuation
        filteredText = re.sub(r" [a-zA-Z] ", " ", filteredText)     # Filter the alone letters from the text
        filteredText = re.sub(r"\w*\d\w*", " ", filteredText)
        if not wordCounter( filteredText, minWords=2):
            continue
        else:
            if filteredText != "" and not filteredText.isspace():   # Check if the text is empty now
                filteredText = re.sub(r"\s\s+", " ", filteredText)  # Filter the whitespace in excess
                filteredList.append( filteredText)                  # Filtered list that must be returned
                filteredText = " ".join(filteredText.split())       # Rebuild the filteredText
                if(debug):
                    print("\""+filteredText+"\"")
    return filteredList

# *******************************
# *** SEARCH FOR THE ENTITIES ***
# *******************************
def searchEntities( ngrams_list, sentence, LABEL, debug = False, dictionaries=None, metadata_template=None, dictionary_search=True):
    # DECLARE VARIABLES
    tagList = [0] * len(sentence)
    occurrenceList = []
    entities = []
    dictionaryThreshold = 0
    possibilities = []
    metadata = {}

    # START THE FUNCTION
    # We want to retrieve as many information as possible from the process so we better understand our data
    if metadata_template is not None:
        metadata.update( metadata_template)
    # Perform a search through the set() dictionary in order to confirm that the ngrams that were computed are good
    for dictionary in dictionaries:
        for ngram in ngrams_list:
            detectedFurniture = False
            # Iterate through all the words of the current ngram
            wordsInNgram = ngram.split()
            for word in wordsInNgram:
                # Search in the dictionary set() for the given word in order to ensure that it is related to furniture
                if word in dictionary:
                    detectedFurniture = True
                    break
            # If we detected a furniture related word then we can accept the ngram, otherwise we ignore it
            if detectedFurniture:
                possibilities.append(ngram)
                if 'accepted_ngrams' in metadata:
                    metadata['accepted_ngrams'] += 1
            else:
                if 'ignored_ngrams' in metadata:
                    metadata['ignored_ngrams'] += 1

    # We want to reorder the list of ngrams from the longest in terms of words, to the shortest
    possibilities.sort(key = lambda x: len( x.split()), reverse=True)
    if(debug):
        print("Resorted list of ngrams after guarding: ", possibilities)
    # Iterate through all the remaining ngram possibilities
    for possibility in possibilities:
        for match in re.finditer( r'\b({0})\b'.format(possibility), str( sentence)) :
            start = match.start()
            end = match.end()
            # We want to avoid using the same part of the sentence that we have already tagged
            if sum(tagList[start:end]) > 0:
                continue
            else:
                # We want to mark with 1 the character positions that have been already checked
                for i in range( start, end):
                    tagList[i] = 1
                # Save the information regarding the entities detection
                with open("additional_information/entitiesDetected.txt", "a") as log:
                    print("String \"%s\" matched in sentence \"%s\" at %d:%d" % ( sentence[start:end], sentence, start, end), file=log)
                # The occurrence list will help us understand if we tagged the right products with our algorithm
                occurrenceList.append( str(sentence[start:end]))
                # Add the new tuple of entities to the entities list
                entities.append(( start, end, LABEL))
                # Increase the counters based on the result type
                metadata['no_entities_possibility'] += 1

    # Iterate through all the words of the dictionary and search for matches in the sentence
    if(dictionary_search):
        for dictionary in dictionaries:
            for wordDictNgram in dictionary:
                for match in re.finditer(r'\b({0})\b'.format(wordDictNgram), str(sentence)):
                    start = match.start()
                    end = match.end()
                    # We want to avoid using the same part of the sentence that we have already tagged
                    if sum(tagList[start:end]) > 0:
                        continue
                    else:
                        # We want to mark with 1 the character positions that have been already checked
                        for i in range( start, end):
                            tagList[i] = 1
                        # Save the information regarding the entities detection
                        with open("additional_information/entitiesDetectedDictionary.txt", "a") as log:
                            print("String \"%s\" matched in sentence \"%s\" at %d:%d using dictionary." % ( sentence[start:end], sentence, start, end), file=log)
                        # The occurrence list will help us understand if we tagged the right products with our algorithm
                        occurrenceList.append( str(sentence[start:end]))
                        # Add the new tuple of entities to the entities list
                        entities.append(( start, end, LABEL))
                        # Increase the counters based on the result type
                        metadata['no_entities_dictionary'] += 1

    # Determine how many empty sentences we retrieved and how many sentences contain entities
    if not entities:
        metadata['no_sentences_without_entities'] += 1
    else:
        metadata['no_sentences_with_entities'] += 1
    # Format the data as a tuple so we can pass on to the future list
    tupleFormatted = (sentence, {"entities": entities})

    return tupleFormatted, occurrenceList, metadata

# *****************************
# *** TRAINING DATA BUILDER ***
# *****************************
def trainingDataBuilder( URL, sentences, debug = False, metadata_template=None):
    training_data_w_entities = []
    training_data_wo_entities = []
    totalOccurrences = []
    metadata, metadataLocal = {}, {}
    if metadata_template is not None:
        metadata.update( metadata_template)
        metadataLocal.update( metadata_template)

    lastPath = getPathEndURL(URL)
    if(debug):
        print("Last path from URL: %s is: %s." % (URL, lastPath))   # Print the last part of the path

    lastPathList = lastPath.split("-")                          # Split the last path into tokens
    if len( lastPath) == 0:
        print("The URL: \"%s\" couldn't be solved by the algorithm.")
        return 0, 0, 0, 0
    else:
        if(debug):
            print("The decomposed last Path: %s" % (lastPathList))      # Print the decomposed last path
        # Get all the possible combinations of words that are relevant for our search
        possibilities = getNgrams(lastPathList)
        if not possibilities:
            return 0, 0, 0, 0
        # Filter the sentences
        sentences = filter(sentences)
        # If we ended up with no sentences then we abandon the ship
        if not sentences:
            return 0, 0, 0, metadata
        # Iterate through all the possible sentences
        for sentence in sentences:
            # Search the current sentence for entities and their position
            tuple, occurrences, metadata = searchEntities( ngrams_list=possibilities,
                                                           sentence=sentence,
                                                           LABEL="PRODUCTS",
                                                           metadata_template=template,
                                                           dictionaries=[furniture3W, furniture2W, furniture1W],
                                                           debug=False)
            if metadata:
                metadataLocal = addDict( metadataLocal, metadata)
            # Add to the training data a new tuple formed from the sentence and the dictionary of entities
            if occurrences:
                totalOccurrences += occurrences
            if not tuple[1]['entities']:
                training_data_wo_entities.append(tuple)
            else:
                training_data_w_entities.append(tuple)
        return training_data_w_entities, training_data_wo_entities, totalOccurrences, metadataLocal

# *******************************
# *** GET THE DATA FROM FILES ***
# *******************************
def getData( paths, minWords, outputPath, maxFiles = 0, verbose=0, metadata_template=None):
    limit = maxFiles if maxFiles > 0 else 0                 #
    counterReal = 0                                         #
    counterIterations = 0
    counter_w_entities = 0
    counter_wo_entities = 0

    no_links = len(paths)
    totalOccurrences = []

    metadataLocal, metadata = {}, {}
    if metadata_template is not None:
        metadataLocal.update( metadata_template)
        metadata.update( metadata_template)
    # Iterate through all the FILES available
    for file in paths:                                      # Iterate through all the FILES
        with open(file) as f:                               # Open the current file
            counterReal += 1                                # The real number of files explored
            print("Processing links: ( %i / %i )" % (counterReal, no_links))
            if(limit == counterIterations and counterIterations != 0):                 # If we reached the maximum number of desired files we stop
                break
            else:                                           # If the limit is not reached, we continue with the analysis
                data = json.loads(f.read())['data']         # Get the data from the file
                url = data['url']                           # Get the URL part from the data
                sentences = data['sentences']               # Get the sentences from the data
                # Build the training data for the current file
                training_data_w_entities, training_data_wo_entities, occurrences, metadata = trainingDataBuilder( URL=url,
                                                                                                                  sentences=sentences,
                                                                                                                  metadata_template=template,
                                                                                                                  debug=False)

                if not training_data_w_entities:
                    if(verbose >= 2):
                        print("Training data with entities returned empty, next iteration will start soon.")
                else:
                    sub_folder = "page"+str( counter_w_entities)
                    url_local = getDomain(url)
                    newPath = os.path.join( outputPath, "processed_w_entities")
                    output( data=training_data_w_entities, rootPath=newPath, folder_name=url_local, fn="data.txt", subfolder_name=sub_folder)
                    totalOccurrences += occurrences
                    counter_w_entities += 1

                if not training_data_wo_entities:
                    if(verbose >= 2):
                        print("Training data without entities returned empty, next iteration will start soon.")
                else:
                    sub_folder = "page"+str( counter_wo_entities)
                    url_local = getDomain(url)
                    newPath = os.path.join( outputPath, "processed_wo_entities")
                    output( data=training_data_wo_entities, rootPath=newPath, folder_name=url_local, fn="data.txt", subfolder_name=sub_folder)
                    counter_wo_entities += 1

                if training_data_w_entities != 0 and training_data_wo_entities != 0:
                    metadataLocal = addDict( metadataLocal, metadata)
                    counterIterations += 1

    output( data=totalOccurrences, rootPath=outputPath, folder_name="Occurrences", fn="Occurrences.txt")

    if(verbose >= 1 and metadata_template is not None):
        sent_w_ent = metadataLocal['no_sentences_with_entities']
        sent_wo_ent = metadataLocal['no_sentences_without_entities']
        ent_dict = metadataLocal['no_entities_dictionary']
        ent_poss = metadataLocal['no_entities_possibility']
        ngrams_accept = metadataLocal['accepted_ngrams']
        ngrams_refused = metadataLocal['ignored_ngrams']
        print("Detected %i samples for PRODUCTS in the training data." % ( len( totalOccurrences)))
        print("Detected %i sentences with entities in them." % ( sent_w_ent))
        print("Detected %i sentences without entities in them." % ( sent_wo_ent))
        ratio_entities = sent_w_ent / ( sent_w_ent + sent_wo_ent)
        print("Ratio between sentences with entities/total: %.2f%%" % (ratio_entities * 100))

        print("Detected %i entities based on possibilities from URL." % ( ent_poss))
        print("Detected %i entities based on the dictionary." % ( ent_dict))

        ratio_ngrams = ngrams_accept / ( ngrams_refused + ngrams_accept)
        print("Accepted %i ngrams during the search for entities." % ( ngrams_accept))
        print("Refused %i ngrams during the search for entities." % ( ngrams_refused))
        print("Ratio between accepted and total ngrams: %.2f%%" % ( ratio_ngrams * 100))
    return counterIterations, counterReal

# *********************
# *** MAIN FUNCTION ***
# *********************
dir = "extracted"
out_path = "processed"

DEV_MODE = 0
if(DEV_MODE):
    print("DEV MODE ENABLED")
else:
    print("Gathering the paths.")
    paths = getFiles( rootPath="",
                      directory=dir,
                      extension="json")
    print("Processing the paths.")
    good, real = getData( paths=paths,
                          maxFiles=0,
                          minWords=0,
                          verbose=1,
                          outputPath=out_path,
                          metadata_template=template)
    print("Solved URLs: %i" % ( good))
    print("Unsolved URLs: %i" % ( real-good))
    print("Total URLs iterated: %i, with efficiency rate of %.2f%%" % ( real, good/real * 100))
