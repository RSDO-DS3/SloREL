from os.path import isfile, join, exists
from os import listdir, mkdir
from collections import Counter, defaultdict
import json
from random import randint



def filter_relations(relation, sent, all_relations, entities):
    global used
    rel = relation["relation"]

    if rel in {"P17", "P279"}:
        e1, e2 = entities[relation["entity1"]]["wikidata_tag"], entities[relation["entity2"]]["wikidata_tag"]
        triplet = rel+e1+e2
        if e1 != e2 and triplet not in used[rel]:
            used[rel].add(triplet)
            return True
    elif rel in {"P131", "P150", "P31", "P106", "P527", "P361", "P3450", "P138", "P641", "P172", "P276",
                 "P607", "P1001", "P140", "P136", "P50", "P39", "P463"}:
        return True
    elif rel in {"P156", "P155"}:
        col = Counter(all_relations)
        if col[rel] < 3:
            return True
    elif rel == "P19":
        if "†" in sent or "*" in sent or "rodil" in sent or "rojen" in sent:
            return True
    elif rel == "P27":
        if not("†" in sent or "*" in sent or "rodil" in sent or "rojen" in sent or "ubil" in sent or "umor" in sent or "umrl" in sent):
            return True
    elif rel == "P20":
        if "†" in sent or "*" in sent or "ubil" in sent or "umor" in sent or "umrl" in sent:
            return True
    elif rel == "P3373":
        if "sorojen" in sent or "brat" in sent or "sestr":
            return True
    elif rel in {"P40", "P22", "P25"}:
        if "oče" in sent or "mat" in sent or "mam" in sent or "sin" in sent or "hčer" in sent or "starš" in sent or "hči" in sent:
            return True
    return False


if __name__ == "__main__":
    global used
    used = defaultdict(lambda: set())

    with open("settings.json", "r") as settings_file:
        settings = json.load(settings_file)

    onlyfiles = [f for f in listdir(settings["text_with_entities_and_relations_folder"]) if isfile(join(settings["text_with_entities_and_relations_folder"], f))]

    k = 0
    
    if not exists(settings["text_with_entities_and_filtered_relations_folder"]):
        mkdir(settings["text_with_entities_and_filtered_relations_folder"])

    for file in onlyfiles:
        k += 1
        if k % 1000 == 0:
            print(k)
        with open(settings["text_with_entities_and_relations_folder"] + file, "r", encoding="utf-8") as in_file:
            out_string = ""
            for line in in_file:
                sentence = json.loads(line.strip())
                relations = sentence["relations"]
                for relation in relations:
                    if relation["relation"] == "P36":
                        relation["relation"] = "P131"
                    if relation["relation"] == "P800":
                        relation["relation"] = "P50"
                        tmp = relation["entity1"]
                        relation["entity1"] = relation["entity2"]
                        relation["entity2"] = tmp

                all_relations = [r["relation"] for r in relations]
                sentence["relations"] = [r for r in relations if filter_relations(r, sentence["text"], all_relations, sentence["entities"])]
                if len(sentence["relations"]) > 0:
                    if settings["add_empty_relations"]:
                        for count12345 in range(5):
                            e1 = randint(0, len(sentence["entities"])-1)
                            e2 = randint(0, len(sentence["entities"])-1)
                            while e1 == e2:
                                e2 = randint(0, len(sentence["entities"])-1)
                            found_empty = True
                            for relation in sentence["relations"]:
                                if (e1 == relation["entity1"] and e2 == relation["entity2"]) or (e1 == relation["entity2"] and e2 == relation["entity1"]):
                                    found_empty = False
                                    break
                            if found_empty:
                                sentence["relations"].append({"entity1": e1, "entity2": e2, "relation": "P0"})
                                break
                    out_string += json.dumps(sentence) + "\n"
                    out_rel = ""
            if out_string:
                with open(settings["text_with_entities_and_filtered_relations_folder"] + file, "w", encoding="utf-8") as out_file:
                    out_file.write(out_string)

