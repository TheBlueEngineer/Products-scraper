# ***************************
# *** SPACY DATA SPLITTER ***
# ***************************
def spacyTrainTestValidationSplitter( data, test_ratio, validation_ratio, verbose=False):
    import random
    random.seed(0)
    random.shuffle(data)

    training_ratio = 1 - (test_ratio + validation_ratio)

    training_size = training_ratio * len(data)
    training_size = int( training_size)

    testing_size = test_ratio * len(data)
    testing_size = int( testing_size)

    validation_size = validation_ratio * len(data)
    validation_size = int( validation_size)

    training_data = data[0:training_size]
    testing_data = data[training_size:testing_size+training_size]
    validation_data = data[:validation_size]
    if( verbose):
        print("Train: %i, Test: %i, Validation: %i." % ( len( training_data), len( testing_data), len( validation_data)))
    return training_data, testing_data, validation_data

# ***************************************
# *** FILTER CLASS FOR DATA CLEANSING ***
# ***************************************
class Filter:
    # STATIC VARIABLES

    # CONSTRUCTOR
    def __init__(self):
        # INSTANCE VARIABLES
        self.list_layers = []

    def add(self, layer):
        if not isinstance( layer, FilterLayer):
            print("The \"layer\" variable must be a Filter Layer type.")
        self.list_layers.append( layer)

    def compute(self, text):
        layers = self.list_layers
        filterText = text
        # Iterate through all the layers of the Filter
        for layer in layers:
            if isinstance( text, str):
                filterText = layer.compute(filterText)
            elif isinstance( text, list):
                for index, textData in enumerate(filterText):
                    filterText[index] = layer.compute(filterText[index])
            else:
                raise TypeError("Text data passed to the filter must be <str> or <list> of strings.")
        return filterText

    def printLayers(self):
        print( self.list_layers)

# *****************************************
# *** FILTER LAYER FOR THE FILTER ABOVE ***
# *****************************************
# PARENT CLASS for the filter layers
class FilterLayer:
    def __init__(self):
        pass

    def compute(self, text):
        pass

# Punctuation class: removes all the punctuations from the text
class Punctuation(FilterLayer):
    def __init__(self):
        super().__init__()

    def compute(self, text):
        import re
        return re.sub(r"\\n|\\r\\n", " ", text)

# Lower class: sets all the characters to lower
class Lower(FilterLayer):
    def __int__(self):
        super().__init__()

    def compute(self, text):
        return text.lower()

# Newlines class: Delete all the newlines from text
class Newlines(FilterLayer):
    def __int__(self):
        super().__init__()

    def compute(self, text):
        import re
        return re.sub(r"\\n|\\r\\n", " ", text)

# Whitespace Class: remove the excess of whitespace
class Whitespace(FilterLayer):
    def __int__(self):
        super().__init__()

    def compute(self, text):
        import re
        return re.sub(r"\s\s+", " ", text)

# Lone letters Class: remove the alone letters from the text
class AloneLetters(FilterLayer):
    def __int__(self):
        super().__init__()

    def compute(self, text):
        import re
        return re.sub(r" [a-zA-Z] ", " ", text)

# Words with numbers Class: Remove every word that contains numbers or a decimal
class WordsWithNumbers(FilterLayer):
    def __init__(self):
        super().__init__()

    def compute(self, text):
        import re
        return re.sub(r"\w*\d\w*", " ", text)