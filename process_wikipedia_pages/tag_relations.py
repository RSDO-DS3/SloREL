import classla
from os.path import isfile, join, exists
from os import listdir
import json
import os
import requests
from xml.dom.minidom import parseString
from time import time, sleep
from functools import lru_cache

timer = time()

@lru_cache(maxsize=300)
def open_dict(name):
    global TRIPLETS_FOLDER
    with open(TRIPLETS_FOLDER + name + ".json", "r") as f:
        out = json.load(f)
    return out


def check_if_relation(entity1, entitiy2):
    tmp = entity1 + "000"
    dct = open_dict(tmp[1:5])
    if entity1 in dct and entitiy2 in dct[entity1]:
        return dct[entity1][entitiy2]
    return None
    

def sort_and_remove_duplicates(entities):
    entities = sorted(entities, key=lambda x: x["entity_start"])
    cur_pos = 0
    while cur_pos < len(entities):
        if cur_pos == len(entities) - 1:
            cur_pos += 1
        elif entities[cur_pos]["entity_end"] > entities[cur_pos+1]["entity_start"]:
            if "title" in entities[cur_pos] or (entities[cur_pos]["wikidata_tag"] and "title" not in entities[cur_pos+1]):
                del entities[cur_pos+1]
            else:
                del entities[cur_pos]
        else:
            cur_pos += 1
    return entities


if __name__ == "__main__":
    global TRIPLETS_FOLDER
    with open("settings.json", "r") as settings_file:
        settings = json.load(settings_file)
    TRIPLETS_FOLDER = settings["relation_triplets_folder"]
    onlyfiles = [f for f in listdir(settings["text_with_entities_folder"]) if isfile(join(settings["text_with_entities_folder"], f))]
    nlp = classla.Pipeline('sl', processors='tokenize', use_gpu=True)

    relation_appears = dict()

    if not exists(settings["text_with_entities_and_relations_folder"]):
        os.makedirs(settings["text_with_entities_and_relations_folder"])

    for file in onlyfiles:
        if not exists(settings["text_with_entities_and_relations_folder"] + file):
            print("working on:" + file)
            with open(settings["text_with_entities_folder"] + file, "r", encoding="utf-8") as f:
                out_txt = ""
                for line in f:
                    sentence = json.loads(line.strip())
                    entities = sort_and_remove_duplicates(sentence["entities"])
                    sentence["entities"] = entities
                    sentence["relations"] = []
                    for e1 in range(len(entities)):
                        for e2 in range(e1+1, len(entities)):
                            if entities[e1]["wikidata_tag"] and entities[e2]["wikidata_tag"]:
                                rel = check_if_relation(entities[e1]["wikidata_tag"], entities[e2]["wikidata_tag"])
                                if rel:
                                    sentence["relations"].append({"entity1": e1, "entity2": e2, "relation": rel})
                                rel = check_if_relation(entities[e2]["wikidata_tag"], entities[e1]["wikidata_tag"])
                                if rel:
                                    sentence["relations"].append({"entity1": e2, "entity2": e1, "relation": rel})
                    if len(sentence["relations"]) > 0:
                        out_txt += json.dumps(sentence) + "\n"

                if out_txt != "":
                    with open(settings["text_with_entities_and_relations_folder"] + file, "w", encoding="utf-8") as f_out:
                        f_out.write(out_txt)
                print("end " + file)

    print(sorted(list(relation_appears.items()), key=lambda x: x[1], reverse=True))
