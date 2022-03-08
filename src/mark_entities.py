from json import dumps
import logging
import classla
from copy import deepcopy

logging.basicConfig()

classla.download('sl')
nlp1 = classla.Pipeline('sl', processors='tokenize,pos,ner', use_gpu=False)

def mark_entities_in_text(text, call_id):
    marked_doc = nlp1(text).to_dict()
    logging.info(f"call: {call_id} classla output :\n{dumps(marked_doc, indent = 4)}")
    input_for_prediction = []
    for sentence in marked_doc:
        ner_set = []
        tokens = []
        for index, word in enumerate(sentence[0]):
            tokens.append(word["text"])
            if not "misc" in word or "SpaceAfter=No" not in word["misc"]:
                tokens[-1] += " "
            if word["ner"][0] == "B":
                ner_set.append({
                    "kbID": "None",
                    "tokenpositions": [
                        index
                    ],
                })
            elif word["ner"][0] == "I":
                try:
                    ner_set[-1]["tokenpositions"].append(index)
                except:
                    pass
        for i in range(len(ner_set)):
            for j in range(i+1, len(ner_set)):
                sentence_begin = "".join(tokens[0:ner_set[i]["tokenpositions"][0]])
                sentence_middle = "".join(tokens[ner_set[i]["tokenpositions"][-1]+1:ner_set[j]["tokenpositions"][0]])
                sentence_end = "".join(tokens[ner_set[j]["tokenpositions"][-1]+1:])
                first_entity = "".join(tokens[ner_set[i]["tokenpositions"][0]:ner_set[i]["tokenpositions"][-1]+1])
                second_entity = "".join(tokens[ner_set[j]["tokenpositions"][0]:ner_set[j]["tokenpositions"][-1]+1])
                sentence = "".join(tokens)
                input_for_prediction.append({"BERT_input" : "".join([sentence_begin," <e1> ", first_entity, " </e1> ", sentence_middle, 
                                           " <e2> ", second_entity, " </e2> ", sentence_end]).replace("  <", " <").replace(">  ", "> "),
                            "sentence_text" : sentence.strip(),
                            "entity1_text": first_entity.strip(),
                            "entity2_text": second_entity.strip(),
                            "entity1_sentence_position": len(sentence_begin),
                            "entity2_sentence_position": len(sentence_begin) + len(sentence_middle) + len(first_entity)
                    })
                
                input_for_prediction.append({"BERT_input" : "".join([sentence_begin," <e2> ", first_entity, " </e2> ", sentence_middle, 
                                           " <e1> ", second_entity, " </e1> ", sentence_end]).replace("  <", " <").replace(">  ", "> "),
                            "sentence_text" : input_for_prediction[-1]["sentence_text"],
                            "entity1_text": input_for_prediction[-1]["entity2_text"],
                            "entity2_text": input_for_prediction[-1]["entity1_text"],
                            "entity1_sentence_position": input_for_prediction[-1]["entity2_sentence_position"],
                            "entity2_sentence_position": input_for_prediction[-1]["entity1_sentence_position"]
                    })
    logging.info(f"call {call_id} input for BERT prediction :\n{dumps(input_for_prediction, indent = 4)}")
    return input_for_prediction