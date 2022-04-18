import numpy as np
from core import keras_models, embeddings
from evaluation import metrics
from graph import io
import os
import ast
import json


module_location = os.path.abspath(__file__)
module_location = os.path.dirname(module_location)

with open(os.path.join(module_location, "model_params.json")) as f:
    model_params = json.load(f)

with open(os.path.join(module_location, model_params["property2idx"])) as f:
    property2idx = ast.literal_eval(f.read())

relations = list(property2idx)

def evaluate(model, data_input, gold_output):
    predictions = model.predict(data_input, batch_size=keras_models.model_params['batch_size'], verbose=1)
    print(predictions)
    if len(predictions.shape) == 3:
        predictions_classes = np.argmax(predictions, axis=2)
        train_batch_f1 = metrics.accuracy_per_sentence(predictions_classes, gold_output)
        #print("Results (per sentence): ", train_batch_f1)
        train_y_properties_stream = gold_output.reshape(gold_output.shape[0] * gold_output.shape[1])
        predictions_classes = predictions_classes.reshape(predictions_classes.shape[0] * predictions_classes.shape[1])
        class_mask = train_y_properties_stream != 0
        train_y_properties_stream = train_y_properties_stream[class_mask]
        predictions_classes = predictions_classes[class_mask]
    else:
        predictions_classes = np.argmax(predictions, axis=1)
        train_y_properties_stream = gold_output

    print(train_y_properties_stream)

    accuracy = metrics.accuracy(predictions_classes, train_y_properties_stream)
    micro_scores = metrics.compute_micro_PRF(predictions_classes, train_y_properties_stream, empty_label=keras_models.p0_index)
    macro_scores = metrics.compute_macro_PRF(predictions_classes, train_y_properties_stream,
                                             empty_label=keras_models.p0_index)

    #print("Results: Accuracy: ", accuracy)
    #print("Results: Micro-Average F1: ", micro_scores)
    print("Results: Accuracy: ", accuracy)
    print("Results: Micro-Average F1: ", micro_scores)
    print("Results: Macro-Average F1: ", macro_scores)
    return predictions_classes, predictions


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('test_set')

    args = parser.parse_args()

    to_one_hot = embeddings.timedistributed_to_one_hot
    graphs_to_indices = keras_models.to_indices_with_extracted_entities

    embedding_matrix, word2idx = embeddings.load(keras_models.model_params['wordembeddings'])

    model = getattr(keras_models, "model_ContextWeighted")(keras_models.model_params, embedding_matrix, 36, 32)
    model.load_weights("trainedmodels/model_ContextWeighted.kerasmodel")

    with open(args.test_set, "r") as test_json_file:
        test_json = json.load(test_json_file)

    test_data, _ = io.load_relation_graphs_from_file(args.test_set, load_vertices=True)

    test_json = keras_models.split_graphs(test_json)

    out = []
    cur_sentence = 0
    cur_rel = 0
    test_as_indices = list(graphs_to_indices(test_data, word2idx))
    predictions = model.predict(test_as_indices[:-1], batch_size=keras_models.model_params['batch_size'], verbose=1)
    correct_answers = test_as_indices[-1]
    count = 0
    for seven_relations_predicitions, seven_correct_answers in zip(predictions, correct_answers):
        for predicition, correct_answers in zip(seven_relations_predicitions, seven_correct_answers):
            if correct_answers == 0:
                break
            pred = np.argmax(predicition, axis=0)
            correct = "f"
            if pred == correct_answers:
                correct = "c"

            sentence = []
            for token_i, token in enumerate(test_json[cur_sentence]["tokens"]):
                if token_i == test_json[cur_sentence]["edgeSet"][cur_rel]["left"][0]:
                    sentence.append("<e1>")
                elif token_i == test_json[cur_sentence]["edgeSet"][cur_rel]["right"][0]:
                    sentence.append("<e2>")
                elif token_i == test_json[cur_sentence]["edgeSet"][cur_rel]["left"][-1]+1:
                    sentence.append("</e1>")
                elif token_i == test_json[cur_sentence]["edgeSet"][cur_rel]["right"][-1]+1:
                    sentence.append("</e2>")
                sentence.append(token)

            if len(test_json[cur_sentence]["tokens"]) == test_json[cur_sentence]["edgeSet"][cur_rel]["left"][-1] + 1:
                sentence.append("</e1>")
            elif len(test_json[cur_sentence]["tokens"]) == test_json[cur_sentence]["edgeSet"][cur_rel]["right"][-1] + 1:
                sentence.append("</e2>")

            cur_rel += 1
            if cur_rel == len(test_json[cur_sentence]["edgeSet"]):
                cur_rel = 0
                cur_sentence += 1

            out.append("\t".join([str(predicition[pred]), relations[pred], correct, " ".join(sentence)]))


    with open("results.txt", "w", encoding="utf-8") as result_file:
        result_file.write("\n".join(out))
