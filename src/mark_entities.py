from json import dumps
import logging
import classla
from copy import deepcopy
from os import getenv
logging.basicConfig()

classla.download('sl')
nlp = classla.Pipeline('sl', processors='tokenize,pos,ner', use_gpu=getenv("useGPU", False))
MENTION_MSD = {"N", "R", "P"} 

def mark_entities_in_text(text, call_id):
    global nlp
    global MENTION_MSD
    marked_doc = nlp(text).to_dict()
    logging.info(f"call: {call_id} classla output :\n{dumps(marked_doc, indent = 4)}")
    input_for_prediction = []
    for sentence in marked_doc:
        mention_set = []
        tokens = []
        last_msd = ""
        token_pos = 0
        sentence_text = sentence[1][sentence[1].find("# text = ") + 9:].strip()
        for index, word in enumerate(sentence[0]):
            tokens.append(word["text"])
            if sentence_text.find(word["text"], token_pos) != -1:
                token_pos = sentence_text.find(word["text"], token_pos)
            if not "misc" in word or "SpaceAfter=No" not in word["misc"]:
                tokens[-1] += " "
            if word["ner"][0] == "B":
                mention_set.append({
                    "tokenpositions": [
                        index
                    ],
                    "ner_type": word["ner"][2:],
                    "begin": token_pos,
                    "end": token_pos + len(word["text"])
                })
                last_msd = ""
            elif word["ner"][0] == "I":
                if len(mention_set) > 0:
                    mention_set[-1]["tokenpositions"].append(index)
                    mention_set[-1]["end"] += token_pos + len(word["text"])
            elif word["xpos"][0] in MENTION_MSD:
                if last_msd == word["xpos"][0]:
                    mention_set[-1]["tokenpositions"].append(index)
                    mention_set[-1]["end"] += token_pos + len(word["text"])
                else:
                    mention_set.append({
                        "tokenpositions": [
                            index
                        ],
                        "ner_type": "0",
                        "begin": token_pos,
                        "end": token_pos + len(word["text"])
                    })
                    last_msd = word["xpos"][0]
            
        input_for_prediction_sentence = []
        for i in range(len(mention_set)):
            mention_set[i]["id"] = i + 1
            for j in range(i+1, len(mention_set)):
                sentence_begin = "".join(tokens[0:mention_set[i]["tokenpositions"][0]])
                sentence_middle = "".join(tokens[mention_set[i]["tokenpositions"][-1]+1:mention_set[j]["tokenpositions"][0]])
                sentence_end = "".join(tokens[mention_set[j]["tokenpositions"][-1]+1:])
                first_entity = "".join(tokens[mention_set[i]["tokenpositions"][0]:mention_set[i]["tokenpositions"][-1]+1])
                second_entity = "".join(tokens[mention_set[j]["tokenpositions"][0]:mention_set[j]["tokenpositions"][-1]+1])
                input_for_prediction_sentence.append({"BERT_input" : "".join([sentence_begin," <e1> ", first_entity, " </e1> ", sentence_middle, 
                                           " <e2> ", second_entity, " </e2> ", sentence_end]).replace("  <", " <").replace(">  ", "> "),
                            "entity1_id": i+1,
                            "entity2_id": j+1
                    })
                
                input_for_prediction_sentence.append({"BERT_input" : "".join([sentence_begin," <e2> ", first_entity, " </e2> ", sentence_middle, 
                                           " <e1> ", second_entity, " </e1> ", sentence_end]).replace("  <", " <").replace(">  ", "> "),
                            "entity1_id": j+1,
                            "entity2_id": i+1
                    })
        for mention in mention_set:
            mention["text"] = sentence_text[mention["begin"]:mention["end"]]
            mention.pop("begin")
            mention.pop("end")
            mention.pop("tokenpositions")
        input_for_prediction.append({"relation_candidates": deepcopy(input_for_prediction_sentence), 
            "mention_set": deepcopy(mention_set), "sentence_text": sentence_text})
    logging.info(f"call {call_id} input for BERT prediction :\n{dumps(input_for_prediction, indent = 4)}")
    return input_for_prediction