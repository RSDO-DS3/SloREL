import json

import classla
from copy import deepcopy


classla.download('sl')
nlp1 = classla.Pipeline('sl', processors='tokenize,pos,ner', use_gpu=False)

def mark_entities_in_text(text):
    marked_doc = nlp1(text).to_dict()
    print(json.dumps(marked_doc))
    out = []
    for sentence in marked_doc:
        vertex_set = []
        edge_set = []
        tokens = []
        for index, word in enumerate(sentence[0]):
            tokens.append(word["text"])
            if word["ner"][0] == "B":
                vertex_set.append({
                    "kbID": "None",
                    "tokenpositions": [
                        index
                    ],
                })
            elif word["ner"][0] == "I":
                try:
                    vertex_set[-1]["tokenpositions"].append(index)
                except:
                    pass
        for i in range(len(vertex_set)):
            for j in range(i+1, len(vertex_set)):
                out.append(" ".join(tokens[0:vertex_set[i]["tokenpositions"][0]] + ["<e1>"] + tokens[vertex_set[i]["tokenpositions"][0]:vertex_set[i]["tokenpositions"][-1]+1] + ["</e1>"] + tokens[vertex_set[i]["tokenpositions"][-1]+1:vertex_set[j]["tokenpositions"][0]] + ["<e2>"] +
                    tokens[vertex_set[j]["tokenpositions"][0]:vertex_set[j]["tokenpositions"][-1]+1] + ["</e2>"] + tokens[vertex_set[j]["tokenpositions"][-1]+1:-1]))
                out.append(" ".join(tokens[0:vertex_set[i]["tokenpositions"][0]] + ["<e2>"] + tokens[vertex_set[i]["tokenpositions"][0]:vertex_set[i]["tokenpositions"][-1]+1] + ["</e2>"] + tokens[vertex_set[i]["tokenpositions"][-1]+1:vertex_set[j]["tokenpositions"][0]] + ["<e1>"] +
                    tokens[vertex_set[j]["tokenpositions"][0]:vertex_set[j]["tokenpositions"][-1]+1] + ["</e1>"] + tokens[vertex_set[j]["tokenpositions"][-1]+1:-1]))
    return out