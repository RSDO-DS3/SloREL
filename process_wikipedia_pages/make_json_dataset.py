from os.path import isfile, join, exists
from os import listdir, mkdir
from json import load, loads, dump
import classla


if __name__ == "__main__":

    classla.download('sl')
    nlp = classla.Pipeline('sl', processors='tokenize', use_gpu=True)
    
    validation_str = ""
    train_str = ""
    test_str = ""
    with open("settings.json", "r") as settings_file:
        settings = load(settings_file)

       
    split = settings["json"]["split"]
    split["test"] += split["train"]
    split["validation"] += split["test"]
    
    if settings["use_filtered_data"]:
        data_folder = settings["text_with_entities_and_filtered_relations_folder"]
    else:
        data_folder = settings["text_with_entities_and_relations_folder"]
    
    relation_files = [f for f in listdir(data_folder) if isfile(join(data_folder, f))]
    
    sentence_count = 0
    
    train_json = []
    test_json = []
    validation_json = []
    
    for file in relation_files:
        with open(data_folder + file, "r") as relation_file:
            for line in relation_file:
                sentence = loads(line.strip())
                tokenized_sentence = nlp(sentence["text"]).to_dict()
                tokens = [word["text"] for sentence_tokens in tokenized_sentence for word in sentence_tokens[0]]
                positions = []
                cur_pos = 0
                cur_entity = 0
                entity_positions = []
                cur_entity_positions = []
                empty_entities = set()
                for i, token in enumerate(tokens):
                    token_pos = sentence["text"].find(token, cur_pos)
                    if token_pos == -1:
                        print("failed to find token", token)
                    else:
                        cur_pos = token_pos
                    
                    if cur_entity == len(sentence["entities"]):
                        break
                    
                    while token_pos >= sentence["entities"][cur_entity]["entity_end"]:
                        entity_positions.append(cur_entity_positions)
                        if cur_entity_positions == []:
                            empty_entities.add(cur_entity)
                        cur_entity_positions = []
                        cur_entity += 1
                        
                        if cur_entity == len(sentence["entities"]):
                            break
                    if cur_entity == len(sentence["entities"]):
                            break

                    if token_pos == sentence["entities"][cur_entity]["entity_start"] or len(cur_entity_positions) > 0:
                        cur_entity_positions.append(i)
                while cur_entity < len(sentence["entities"]):
                    entity_positions.append(cur_entity_positions)
                    if cur_entity_positions == []:
                            empty_entities.add(cur_entity)
                    cur_entity_positions = []
                    cur_entity += 1
                
                entities = [{
                        "kbID": entity["wikidata_tag"],
                        "type": "LEXICAL",
                        "tokenpositions": entity_positions[i]
                    } for i, entity in enumerate(sentence["entities"])]
                relations = [{
                        "kbID": relation["relation"],
                        "left": entity_positions[relation["entity1"]],
                        "right": entity_positions[relation["entity2"]]
                    } for relation in sentence["relations"] if not relation["entity1"] in empty_entities and not relation["entity2"] in empty_entities]
                
                        
                
                if sentence_count % split["validation"] < split["train"]:
                    train_json.append({"vertexSet": entities, "edgeSet": relations, "tokens": tokens})
                elif sentence_count % split["validation"] < split["test"]:
                    test_json.append({"vertexSet": entities, "edgeSet": relations, "tokens": tokens})
                else:
                    validation_json.append({"vertexSet": entities, "edgeSet": relations, "tokens": tokens})
                    
                sentence_count += 1
    
    with open(settings["json"]["train_file"], "w", encoding='utf-8') as train_file:
        dump(train_json, train_file, indent=4)
    with open(settings["json"]["test_file"], "w", encoding='utf-8') as test_file:
        dump(test_json, test_file, indent=4)
    with open(settings["json"]["validation_file"], "w", encoding='utf-8') as validation_file:
        dump(validation_json, validation_file, indent=4)
                
    
