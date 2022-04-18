import json
import bz2
from os.path import exists
from os import mkdir
from collections import defaultdict


if __name__ == "__main__":
    with open("settings.json", "r") as settings_file:
            settings = json.load(settings_file)
    i = 0

    if not exists(settings["relation_triplets_folder"]):
        mkdir(settings["relation_triplets_folder"])

    out_dict = defaultdict(lambda : dict())
    with bz2.open(settings["wikidata_dump_file"], "rt") as bzinput:
        i = 0
        for line in bzinput:
            i += 1
            if i % 20000 == 0:
                print(i)
                for numb in out_dict:
                    tmp_string = ""
                    first = False
                    if not exists(settings["relation_triplets_folder"] + numb + ".json"):
                        first = True
                        tmp_string = "{\n"
                    for entity_id in out_dict[numb]:
                        if first:
                           first = False
                        else:
                            tmp_string += ",\n"
                        tmp_string += '"' + entity_id + '":' + json.dumps(out_dict[numb][entity_id])
                    with open(settings["relation_triplets_folder"] + numb + ".json", "a") as out_file:
                        out_file.write(tmp_string)
                out_dict = defaultdict(lambda : dict())
            if line[0] == "{":
                if line.strip()[-1] == ",":
                    entity_data = json.loads(line.strip()[:-1])
                else:
                    entity_data = json.loads(line.strip())
                entity_id = entity_data["id"]
                tmp = entity_id + "000"
                dict_numb = tmp[1:5]
                out_dict[dict_numb][entity_id] = dict()
                claims = entity_data["claims"]
                for claim in claims:
                    for cl in claims[claim]:
                        try:
                            target_entity = cl.get("mainsnak").get("datavalue").get("value").get("id")
                            if target_entity:
                                    out_dict[dict_numb][entity_id][target_entity] = claim
                        except:
                            pass


        for numb in out_dict:
            tmp_string = ""
            first = False
            if not exists(settings["relation_triplets_folder"] + numb + ".json"):
                first = True
                tmp_string = "{\n"
            for entity_id in out_dict[numb]:
                if first:
                    first = False
                else:
                    tmp_string += ",\n"
                tmp_string += '"' + entity_id + '":' + json.dumps(out_dict[numb][entity_id])
            with open(settings["relation_triplets_folder"] + numb + ".json", "a") as out_file:
                out_file.write(tmp_string)

        for numb in range(1000,10000):
            if exists(settings["relation_triplets_folder"] + str(numb) + ".json"):
                with open(settings["relation_triplets_folder"] + str(numb) + ".json", "a") as out_file:
                    out_file.write("\n}")
            else:
                with open(settings["relation_triplets_folder"] + str(numb) + ".json", "a") as out_file:
                    json.dump({}, out_file)
