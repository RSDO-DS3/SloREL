import bz2
import json
from uuid import uuid4


if __name__ == "__main__":
    entities = []

    with open("settings.json", "r") as settings_file:
            settings = json.load(settings_file)
    with open(settings["elasticsearch_dump"], "w") as out_file:
        pass

    with bz2.open(settings["wikidata_dump_file"], "rt") as bzinput:
            for i, line in enumerate(bzinput):
                if line[0] == "{":
                    ln = line.strip()
                    if ln[-1] == ",":
                        ln = ln[:-1]
                    tmp = json.loads(ln)
                    _id = tmp["id"]
                    if _id[0] == "Q" and "sl" in tmp["labels"]:
                        out = dict()
                        out["_index"] = "wikidataentityindex"
                        out["_type"] = "doc"
                        out["_id"] = str(uuid4())
                        out["_score"] = 1
                        out["_source"] = {"uri":"<http://www.wikidata.org/entity/" + _id + ">", "label":tmp["labels"]["sl"]["value"]}
                        entities.append(json.dumps(out))
                    if i % 10000 == 2:
                        with open(settings["elasticsearch_dump"], "a") as out_file:
                            print(i)
                            out_file.write("\n".join(entities) + "\n")
                            entities = []

    if len(entities) > 0:
        with open(settings["elasticsearch_dump"], "a") as out_file:
            out_file.write("\n".join(entities) + "\n")
            entities = []
