import json
import bz2


if __name__ == "__main__":
    can = set()
    
    with open("settings.json", "r") as settings_file:
        settings = json.load(settings_file)
    try:
        with open(settings["knowledge_graph_candidates"], "r") as file:
            for line in file:
                can.add(line.strip())
    except:
        print("no candidate file found all entities will be used for knowledge graph")
        can = None

    print("number of entities for knowledge graph:", len(can))
    out = dict()
    done = 0
    all = len(can)
    with bz2.open(settings["wikidata_dump_file"], "rt") as file:
        i = 0
        for line in file:
            i += 1
            if i % 1000 == 0:
                print(str(i) + " " + str(done))
            if line[0] == "{":
                if line.strip()[-1] == ",":
                    tmp = json.loads(line.strip()[:-1])
                else:
                    tmp = json.loads(line.strip())
                if not can or tmp["id"] in can:
                    done += 1
                    out[tmp["id"]] = dict()
                    if "sl" in tmp["labels"]:
                        out[tmp["id"]]["label"] = tmp["labels"]["sl"]["value"]
                    else:
                        try:
                            out[tmp["id"]]["label"] = tmp["labels"]["en"]["value"]
                        except:
                            out[tmp["id"]]["label"] = ""
                    out[tmp["id"]]["aliases"] = []
                    if "sl" in tmp["aliases"]:
                        out[tmp["id"]]["aliases"] = [i["value"] for i in tmp["aliases"]["sl"]]
                    out[tmp["id"]]["desc"] = ""
                    if "sl" in tmp["descriptions"]:
                        out[tmp["id"]]["desc"] = tmp["descriptions"]["sl"]["value"]
                    out[tmp["id"]]["instances"] = []
                    if "P31" in tmp["claims"]:
                        for cl in tmp["claims"]["P31"]:
                            try:
                                target_entity = cl.get("mainsnak").get("datavalue").get("value").get("id")
                                if target_entity:
                                    out[tmp["id"]]["instances"].append(target_entity)
                            except:
                                pass

    for id in out:
        new_instance_list = []
        for instance in out[id]["instances"]:
            if instance in out:
                label = out[instance]["label"]
                new_instance_list.append({"kbID": out[id]["instances"], "label": label})
        out[id]["instances"] = new_instance_list
        if len(new_instance_list) > 0:
            for instance in out[id]["instances"][0]["kbID"]:
                if instance in out:
                    label = out[instance]["label"]
                    new_instance_list.append({"kbID": instance, "label": label})
        out[id]["instances"] = new_instance_list

    with open(settings["knowledge_graph"], "w") as out_file:
        json.dump(out, out_file, indent=4)
