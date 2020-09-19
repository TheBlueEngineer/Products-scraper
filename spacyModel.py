import spacy
if( spacy.require_gpu()):
    print("GPU requirements met.")
import thinc_gpu_ops
if(thinc_gpu_ops.AVAILABLE):
    print("Thinc gpu ops is available.")
import random
import warnings
from spacy.util import minibatch, compounding
import plac
from pathlib import Path
import pickle
from bloo.fileMaster import getFiles
from bloo.preprocessingMaster import spacyTrainTestValidationSplitter
from bloo.mlMaster import spacyEvaluate, spacyLossPlot, spacyMetricsPlot, detectFailures

# ******************************
# *** TRAINING DATA GATHERER ***
# ******************************
def getTrainingData( paths, maxSamples = 0, maxFiles = 0, verbose = True):
    newList = []
    counterSamples = 0
    counterFiles = 0

    for path in paths:
        if(counterFiles == maxFiles and maxFiles != 0):
            break
        elif (counterSamples == maxSamples and maxSamples != 0):
            break
        else:
            f = open(path, "rb")
            data = pickle.load(f)
            for curr_data in data:
                newList.append(curr_data)
                counterSamples += 1

                if (counterSamples == maxSamples and maxSamples != 0):
                    break
        counterFiles += 1
    # Print a more verbose answer if the verbose variable is on
    if (verbose):
        print("Iterated through %i/%i files and retrieved %i/%i samples." % ( counterFiles, len(processed_w_paths), counterSamples, maxSamples))
    return newList

@plac.annotations(
    model=("Model name. Defaults to blank 'en' model.", "option", "m", str),
    new_model_name=("New model name for model meta.", "option", "nm", str),
    output_dir=("Optional output directory", "option", "o", Path),
    n_iter=("Number of training iterations", "option", "n", int),
)

def modelSpacy(model=None, new_model_name = "Product", output_dir=None, n_iter=40, training_data=None, validation_data = None, validation_plot=False, dropout=( 0.35, 0.35, 1), batch=( 1., 32., 1.001), verbose=1):
    # IMPORT LIBRARIES
    from bloo.mlMaster import spacyEvaluate
    from spacy.util import decaying

    # DECLARE VARIABLES
    lossesList = []
    lossesList.append( len(training_data))
    metricsLocal = {
        "precision": [0],
        "recall": [0],
        "f1score": [0]
    }

    # We want to reproduce the same random situation in each test
    random.seed(0)
    if model is not None:
        nlp = spacy.load(model)
    else:
        nlp = spacy.blank("en")
        if( verbose >= 1):
            print("Created a blank 'en' model")

    # Now we add the NER recognizer to the model
    if "ner" not in nlp.pipe_names:
        ner = nlp.create_pipe("ner")
        nlp.add_pipe(ner)
    else:
        ner = nlp.get_pipe("ner")

    # Add the new entity label to entity recognizer
    ner.add_label("PRODUCTS")

    # Decide whether to start or to resume training
    if model is None:
        optimizer = nlp.begin_training()
    else:
        optimizer = nlp.resume_training()
    move_names = list( ner.move_names)

    # Get names of other pipes to disable them during training
    pipe_executions = ["ner", "trf_wordpiercer", "trf_tok2vec"]
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_executions]

    # Only train the given NER
    with nlp.disable_pipes(*other_pipes), warnings.catch_warnings():
        warnings.filterwarnings("once", category=UserWarning, module='spacy')

        sizes = compounding( batch[0], batch[1], batch[2])
        dropout = decaying( dropout[0], dropout[1], dropout[2])
        # batch up the examples using spacy's mini batch
        for itn in range(n_iter+1):
            random.shuffle(training_data)
            batches = minibatch( training_data, size = sizes)
            losses = {}
            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update( texts, annotations, sgd=optimizer, drop=next(dropout), losses=losses)

            # Print information about the current iteration after it is finished so we can better visualize the progress
            if( verbose >= 1):
                print("Losses after iteration %i: %s" % (itn, str(losses)))
                print("Current dropout rate: %.2f" % ( next(dropout)))
            # Add the current loss to the list of losses, so we can plot it later
            lossesList.append( int( losses['ner']))

            # AFTER EACH ITERATION WE WANT TO VALIDATE THE DATA AND GET SOME RESULTS
            if validation_data is not None:
                random.shuffle(validation_data)
                metrics = spacyEvaluate( ner_model=nlp, examples=validation_data)
                print("Metrics after iteration %i: PRECISION: %.2f%% | RECALL: %.2f%% | F1SCORE: %.2f%% |" % (itn, metrics['precision'], metrics['recall'], metrics['f1score']))
                for key, value in metricsLocal.items():
                    metricsLocal[key].append( metrics[key])

    # SAVE THE MODEL
    if output_dir is not None:
        print("Spacy model: Saving the model in the output directory: \"%s\"" % (str(output_dir)))

        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.meta["name"] = new_model_name
        nlp.to_disk(output_dir)
        print("Spacy model: saved successfully.")
    return nlp, lossesList, metricsLocal

# *********************
# *** MAIN FUNCTION ***
# *********************
TRAINING_MODE = False

processed_w_paths = getFiles( rootPath="processed", directory="processed_w_entities", fn="data", extension="txt")
processed_wo_paths = getFiles( rootPath="processed", directory="processed_wo_entities", fn="data", extension="txt")

processed_w_data = getTrainingData( processed_w_paths, maxFiles=0, maxSamples = 5000)
processed_wo_data = getTrainingData( processed_wo_paths, maxFiles=0, maxSamples = 5000)

data = processed_w_data + processed_wo_data
training_data, testing_data, validation_data = spacyTrainTestValidationSplitter( data, 0.25, 0, True)

n_iter = 30
if(TRAINING_MODE):
    model, loss, metrics_validation = modelSpacy(
                                        output_dir="models/Product_v10_batch64",
                                        training_data=training_data,
                                        validation_data=None,
                                        n_iter=n_iter,
                                        dropout=( 0.6, 0.20, 3 * 1e-5),
                                        batch=(4.0, 64.0, 1.001),
                                        verbose=1)

    metrics = spacyEvaluate( model, testing_data)
    print("Precision: %.2f%% | Recall: %.2f%% | F1score: %.2f%%" % (metrics['precision'], metrics['recall'], metrics['f1score']))
    detectFailures( model, testing_data)
    spacyLossPlot( loss)
    spacyMetricsPlot( metrics_validation)
else:
    nlp = spacy.load("Product_v7_batch64")
    metrics = spacyEvaluate( nlp, testing_data)
    detectFailures( nlp, testing_data)
    print("Precision: %.2f%% | Recall: %.2f%% | F1score: %.2f%%" % ( metrics['precision'], metrics['recall'], metrics['f1score']))

