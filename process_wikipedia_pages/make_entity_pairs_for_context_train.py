from os.path import isfile, join, exists
from os import listdir
import json
import os
import bz2


if __name__ == "__main__":
    with open("settings.json", "r") as settings_file:
        settings = json.load(settings_file)
    
    entity_can = set()
    try:
        with open(settings["knowledge_graph_entity_candidates"], "r") as file:
            for line in file:
                entity_can.add(line.strip())
    except:
        print("no candidate file found all entities will be used for knowledge graph")
        entity_can = None
    relation_can = set()
    try:
        with open(settings["knowledge_graph_relation_candidates"], "r") as file:
            for line in file:
                relation_can.add(line.strip().split(" ")[0])
    except:
        print("no candidate file found all entities will be used for knowledge graph")
        relation_can = None
    if settings["use_filtered_data"]:
        data_folder = settings["text_with_entities_and_filtered_relations_folder"]
    else:
        data_folder = settings["text_with_entities_and_relations_folder"]
        
    split = settings["entity_context"]["split"]
    split["test"] += split["train"]
    split["validation"] += split["test"]
    
    train_data = ""
    test_data = ""
    valid_data = ""
    
    with open(settings["entity_context"]["train_file"], "w", encoding='utf-8') as train_file:
        pass
    with open(settings["entity_context"]["test_file"], "w", encoding='utf-8') as test_file:
        pass
    with open(settings["entity_context"]["validation_file"], "w", encoding='utf-8') as validation_file:
        pass
    
    with bz2.open(settings["wikidata_dump_file"], "rt") as bzinput:
        i = 0
        all_entities = 0
        for line in bzinput:
            all_entities += 1
            if i % 2000 == 0:
                with open(settings["entity_context"]["train_file"], "a", encoding='utf-8') as train_file:
                    train_file.write(train_data)
                with open(settings["entity_context"]["test_file"], "a", encoding='utf-8') as test_file:
                    test_file.write(test_data)
                with open(settings["entity_context"]["validation_file"], "a", encoding='utf-8') as validation_file:
                    validation_file.write(valid_data)
                train_data = ""
                test_data = ""
                valid_data = ""
            if all_entities % 20000 == 0:
                print(all_entities, i)
            if line[0] == "{":
                if line.strip()[-1] == ",":
                    entity_data = json.loads(line.strip()[:-1])
                else:
                    entity_data = json.loads(line.strip())
                entity_id = entity_data["id"]
                if entity_can and entity_id not in entity_can:
                    continue
                i += 1
                claims = entity_data["claims"]
                for claim in claims:
                    for cl in claims[claim]:
                        try:
                            target_entity = cl.get("mainsnak").get("datavalue").get("value").get("id")
                            if target_entity and target_entity in entity_can and (not relation_can or claim in relation_can):
                                    if i % split["validation"] < split["train"]:
                                        train_data += entity_id + " " + claim + " " + target_entity + "\n"
                                    elif i % split["validation"] < split["test"]:
                                        test_data += entity_id + " " + claim + " " + target_entity + "\n"
                                    else:
                                        valid_data += entity_id + " " + claim + " " + target_entity + "\n"
                        except:
                            pass
    
    with open(settings["entity_context"]["train_file"], "a", encoding='utf-8') as train_file:
        train_file.write(train_data)
    with open(settings["entity_context"]["test_file"], "a", encoding='utf-8') as test_file:
        test_file.write(test_data)
    with open(settings["entity_context"]["validation_file"], "a", encoding='utf-8') as validation_file:
        validation_file.write(valid_data)
                
                    
                    
    
