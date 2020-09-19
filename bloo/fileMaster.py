# *****************
# *** GET FILES ***
# *****************
#----------------------------------------------------------------------------------------------------------------------
# DESCRIPTION: Retrieve all files from a directory and its subdirectories with a certain name, extension
#----------------------------------------------------------------------------------------------------------------------
def getFiles( rootPath, directory, extension, fn="", verbose=True):
    # IMPORT ALL THE REQUIRED LIBRARIES
    import os
    # DECLARE VARIABLES
    pathList = []
    # START THE FUNCTION
    directory = os.path.join(rootPath, directory)
    for root, dirs, files in os.walk(directory):                # Iterate through roots, dirs and files recursively
        for file in files:                                      # For every file in files
            if fn in file and fn != "":
                    if file.endswith('.%s' % (extension)):      # If the searched file ends in the parameter
                        path = os.path.join(root, file)         # Join together the root path and file
                        pathList.append(path)                   # Append the new path to the list
            else:
                if file.endswith('.%s' % (extension)):          # If the searched file ends in the parameter
                    path = os.path.join(root, file)             # Join together the root path and file
                    pathList.append(path)                       # Append the new path to the list

    if( verbose):
        print("Retrieved %i data files from main directory \"%s\"." % ( len(pathList), directory))
    return pathList

# **************************
# *** READ FILE FUNCTION ***
# **************************
def readFile( filePath, startLine = 0, endLine = 0, maxLines = 0, debug = False):
    listLines = []
    count = 0
    listFiles = []

    if isinstance( filePath, str):
        listFiles.append(filePath)
    elif isinstance( filePath, list):
        for path in filePath:
            listFiles.append(path)
    else:
        TypeError("Variable 'filePath' must be <str> or <list>")

    for file in listFiles:
        with open( file, "r") as f:
            # Strip the "\n" from the lines
            lines = [line.rstrip() for line in f]
            # Iterate through all the lines
            for line in lines:
                # Check if the function should ignore the first start rows
                if count < startLine and startLine != 0:
                    pass
                elif count > endLine and endLine !=0:
                    pass
                else:
                    # Append the new link to the list
                    listLines.append(line)
                # Check if the current link's index is not over the maximum desired
                if( count >= maxLines and maxLines != 0):
                    break
                count += 1
        return listLines

# ***********************
# *** OUTPUT FUNCTION ***
# ***********************
def output( data, rootPath, folder_name, fn, subfolder_name=None):
    # IMPORT LIBRARIES
    import os
    import pickle

    # DECLARE VARIABLES
    list_filenames = []
    list_base_folder = []
    DATA_MODE = 0
    FILE_MODE = 0
    curr_filename = ""

    # START FUNCTION
    # If the full path doesn't exist, then create it
    if not os.path.exists( rootPath):
        os.makedirs( rootPath)

    # Separation for the filenames based on datatype
    if isinstance( folder_name, str):
        FILE_MODE = "str"
    else:
        raise TypeError( "Variable 'filenames' must be <str> or <list>.")

    # Separation for the data based on datatype
    if isinstance( data, list):
        DATA_MODE = "list"
    else:
        raise TypeError("Variable 'data' must be <str> or <list>.")

    curr_filename = os.path.join( rootPath, folder_name)
    if not os.path.exists( curr_filename):
        os.mkdir( curr_filename)

    # Build all the paths for the output files
    if subfolder_name is not None:
        curr_filename = os.path.join( curr_filename, subfolder_name)
        if not os.path.exists( curr_filename):
            os.mkdir( curr_filename)

    # Output the training data in the desired path
    output_path = os.path.join( curr_filename, fn)
    f = open(output_path, "wb")
    pickle.dump(data, f)