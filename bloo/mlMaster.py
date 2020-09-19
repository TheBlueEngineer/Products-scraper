# ***
# ***
def spacyEvaluate(ner_model, examples):
    from spacy.gold import GoldParse
    from spacy.scorer import Scorer

    scorer = Scorer()
    for input_, annotations in examples:
        doc_gold_text = ner_model.make_doc(input_)
        gold = GoldParse(doc_gold_text, entities=annotations['entities'])
        predicted_value = ner_model(input_)
        scorer.score(predicted_value, gold)

    metrics = {
        "precision": scorer.scores['ents_p'],
        "recall": scorer.scores['ents_r'],
        "f1score": scorer.scores['ents_f']
    }
    return metrics

# *********************************
# *** DETECT FAILED PREDICTIONS ***
# *********************************
def detectFailures( model, testing_data):
    list_failures = []
    f = open("failedTestingData.txt", 'w')

    for text, annotation in testing_data:
        predicted = model(text)
        entities = annotation['entities']

        for p_ent in predicted.ents:
            detected = False
            for i_ent in entities:
                if (p_ent.start_char == i_ent[0] and p_ent.end_char == i_ent[1] and p_ent.label_ == i_ent[2]):
                    detected = True
            if not detected:
                message = "Predicted entity \'%s\' but it is not found in testing data: \"%s\"\n" % ( str(p_ent), text)
                f.write(message)

        for i_ent in entities:
            detected = False
            for p_ent in predicted.ents:
                if (p_ent.start_char == i_ent[0] and p_ent.end_char == i_ent[1] and p_ent.label_ == i_ent[2]):
                    detected = True
            if not detected:
                sentence = text[i_ent[0]:i_ent[1]]
                message = "Failed to predict entity \'%s\' which was found in testing data: \"%s\"\n" % ( sentence, text)
                f.write(message)

# ********************************
# *** EVALUATE THE SPACY MODEL ***
# ********************************
def spacyEvaluateZE( model, testing_data, verbose=False, output_metrics=False):
    TP, TN, FP, FN = 0, 0, 0, 0

    for text, annotation in testing_data:
        emptyPrediction, emptyAnnotation = False, False

        if(verbose):
            print("Evaluating string \"%s\" with annotation: %s" % ( text, str( annotation['entities'])))
        # Get the prediction of the model for the current sentence and annotations
        predicted = model(text)
        # Get all the entities from the current prediction
        for ent in predicted.ents:
            if(verbose):
                print("Model predicted: %i %i %s %s" % ( ent.start_char, ent.end_char, ent.label_, ent.text))
        entities = annotation['entities']

        # We want to know how many unsolved annotations we have for both entities types
        annotations_initial = len( entities)
        annotations_predicted = len( predicted.ents)
        # Iterate through all the predictions of the model
        for p_ent in predicted.ents:
            # Iterate through all the initial annotations of the model
            predicted = False
            for i_ent in entities:
                if ( p_ent.start_char == i_ent[0] and p_ent.end_char == i_ent[1] and p_ent.label_ == i_ent[2]):
                    if (verbose):
                        print("Detected a TP with predicted entity: (%i, %i, %s) and initial entity: (%i,%i,%s)" % ( p_ent.start_char, p_ent.end_char, p_ent.label_,
                                                                                                                        i_ent[0], i_ent[1], i_ent[2]))
                    annotations_initial -= 1
                    annotations_predicted -= 1
                    predicted = True
            if not predicted:
                FP += 1
        FN += annotations_initial


    # Compute the final information
    if (TP+TN+FN+FP) != 0:
        accuracy = (TP + TN) / (TP + TN + FN + FP)
    else:
        accuracy = 0
    if (TP+FP) != 0:
        precision = TP / (TP + FP)
    else:
        precision = 0
    if (TP+FN) != 0:
        recall = TP / (TP + FN)
    else:
        recall = 0
    if (precision + recall) != 0:
        f1score = 2 * ( (precision * recall) / (precision + recall) )
    else:
        f1score = 0

    # Print the final results of the evaluation
    if(output_metrics):
        metrics = {
            "accuracy": accuracy,
            "precision": precision ,
            "recall": recall,
            "f1score": f1score,
            "TP": TP,
            "TN": TN,
            "FP": FP,
            "FN": FN
        }
        return metrics
    else:
        print("Accuracy of the model: %.2f%%" % ( accuracy * 100))
        print("Precision of the model: %.2f%%" % ( precision * 100))
        print("Recall of the model: %.2f%%" % ( recall * 100))
        print("f1score of the model: %.2f%%" % ( f1score * 100))
        print("TP: %i | TN: %i | FP: %i | FN: %i |" % ( TP, TN, FP, FN))

# ***********************
# *** PLOT THE LOSSES ***
# ***********************
def spacyLossPlot( lossesList):
    # IMPORT LIBRARIES
    import matplotlib.pyplot as plt
    import numpy as np

    iterations = np.arange(1, len(lossesList)+1, 1)
    plt.title("Loss function")
    plt.xlabel("Iterations")
    plt.ylabel("Loss")
    plt.plot( iterations, lossesList, marker=".", linestyle = "-")
    plt.show()

def spacyMetricsPlot(metrics):
    # IMPORT LIBRARIES
    import matplotlib.pyplot as plt
    import numpy as np
    # DECLARE VARIABLES
    colors_list = ['r', 'g', 'b', 'c']
    line_styles = [':', '--', '-.', '-']
    if isinstance( metrics, dict):
        f, ax = plt.subplots(1)
        for index, (key, value) in enumerate(metrics.items()):
            nr_iterations = np.arange(1, len(metrics[key]) + 1, 1)
            ax.plot(nr_iterations, metrics[key], color=colors_list[index], label=key, linestyle=line_styles[index])
        ax.legend()
        plt.title("Metrics evolution")
        plt.show()
    else:
        raise TypeError("Metrics variable must be <dict> type.")