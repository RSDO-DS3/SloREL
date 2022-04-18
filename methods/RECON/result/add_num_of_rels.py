import json


with open("sorted_out_24_ur.txt", "r") as sorted_out:
    results = json.load(sorted_out)

num_rels = dict()

with open("../../train_data/test_filt_with_empty_rel_and_empty_reverse.json", "r", encoding="utf-8") as in_file:
    data = json.load(in_file)
    for sentence in data:
        for relation in sentence["edgeSet"]:
            rel = relation["kbID"]
            if not rel in num_rels:
                num_rels[rel] = 0
            num_rels[rel] += 1

for rel in results:
    results[rel]["all_correct"] = len(results[rel]["correct"]) #num_rels[rel]


with open("sorted_out_24_ur.txt", "w") as sorted_out:
    json.dump(results, sorted_out)

