from os.path import isfile, join, exists
from os import listdir, mkdir
from json import load, loads


if __name__ == "__main__":
    
    validation_str = ""
    train_str = ""
    test_input = ""
    test_correct_rel = ""
    with open("settings.json", "r") as settings_file:
        settings = load(settings_file)

    with open(settings["bert"]["train_file"], "w", encoding='utf-8') as train_file:
        pass
    with open(settings["bert"]["test_input"], "w", encoding='utf-8') as test_file:
        pass
    with open(settings["bert"]["test_correct_rel"], "w", encoding='utf-8') as test_file:
        pass
    with open(settings["bert"]["validation_file"], "w", encoding='utf-8') as validation_file:
        pass
       
    split = settings["bert"]["split"]
    split["test"] += split["train"]
    split["validation"] += split["test"]
    
    if settings["use_filtered_data"]:
        data_folder = settings["text_with_entities_and_filtered_relations_folder"]
    else:
        data_folder = settings["text_with_entities_and_relations_folder"]
    
    relation_files = [f for f in listdir(data_folder) if isfile(join(data_folder, f))]
    
    sentence_count = 0
    
    for file in relation_files:
        with open(data_folder + file, "r") as relation_file:
            for line in relation_file:
                sentence = loads(line.strip())
                for relation in sentence["relations"]:
                    text = sentence["text"]
                    e1 = relation["entity1"]
                    e2 = relation["entity2"]
                    
                    if e1 > e2:
                        if sentence["entities"][e2]["entity_end"] > sentence["entities"][e1]["entity_start"]:
                            continue
                        text = text[:sentence["entities"][e1]["entity_end"]] + " </e1> " + text[sentence["entities"][e1]["entity_end"]:]
                        text = text[:sentence["entities"][e1]["entity_start"]] + " <e1> " + text[sentence["entities"][e1]["entity_start"]:]
                        
                        text = text[:sentence["entities"][e2]["entity_end"]] + " </e2> " + text[sentence["entities"][e2]["entity_end"]:]
                        text = text[:sentence["entities"][e2]["entity_start"]] + " <e2> " + text[sentence["entities"][e2]["entity_start"]:]
                        
                    else:
                        if sentence["entities"][e1]["entity_end"] > sentence["entities"][e2]["entity_start"]:
                            continue
                        text = text[:sentence["entities"][e2]["entity_end"]] + " </e2> " + text[sentence["entities"][e2]["entity_end"]:]
                        text = text[:sentence["entities"][e2]["entity_start"]] + " <e2> " + text[sentence["entities"][e2]["entity_start"]:]
                        
                        text = text[:sentence["entities"][e1]["entity_end"]] + " </e1> " + text[sentence["entities"][e1]["entity_end"]:]
                        text = text[:sentence["entities"][e1]["entity_start"]] + " <e1> " + text[sentence["entities"][e1]["entity_start"]:]

                    text = text.replace("  ", " ")
                    
                    if sentence_count % split["validation"] < split["train"]:
                        train_str += relation["relation"] + "\t" + text + "\n"
                    elif sentence_count % split["validation"] < split["test"]:
                        test_input += text + "\n"
                        test_correct_rel += relation["relation"] + "\n"
                    else:
                        validation_str += relation["relation"] + "\t" + text + "\n"
                    
                    sentence_count += 1
                    if sentence_count % 10000 == 0:
                    
                        with open(settings["bert"]["train_file"], "a", encoding='utf-8') as train_file:
                            train_file.write(train_str)
                            train_str = ""
                        with open(settings["bert"]["test_input"], "a", encoding='utf-8') as test_file:
                            test_file.write(test_input)
                            test_input = ""
                        with open(settings["bert"]["test_correct_rel"], "a", encoding='utf-8') as test_file:
                            test_file.write(test_correct_rel)
                            test_correct_rel = ""
                        with open(settings["bert"]["validation_file"], "a", encoding='utf-8') as validation_file:
                            validation_file.write(validation_str)
                            validation_str = ""
    
    with open(settings["bert"]["train_file"], "a", encoding='utf-8') as train_file:
        train_file.write(train_str)
        train_str = ""
    with open(settings["bert"]["test_input"], "a", encoding='utf-8') as test_file:
        test_file.write(test_input)
        test_input = ""
    with open(settings["bert"]["test_correct_rel"], "a", encoding='utf-8') as test_file:
        test_file.write(test_correct_rel)
        test_correct_rel = ""
    with open(settings["bert"]["validation_file"], "a", encoding='utf-8') as validation_file:
        validation_file.write(validation_str)
        validation_str = ""
                
    
