import json

results = dict()

with open("out_24_ur.txt", "r") as out_file:
    for line in out_file:
        score, rel, cor = line.strip().split("\t")
        if rel not in results:
            results[rel] = dict()
            results[rel]["correct"] = []
            results[rel]["false"] = []
        if cor == "f":
            results[rel]["false"].append(score)
        elif cor == "c":
            results[rel]["correct"].append(score)

for rel in results:
    results[rel]["false"] = sorted(results[rel]["false"], reverse=True)
    results[rel]["false_len"] = len(results[rel]["false"])
    results[rel]["correct"] = sorted(results[rel]["correct"], reverse=True)
    results[rel]["correct_len"] = len(results[rel]["correct"])


with open("sorted_out_24_ur.txt", "w") as sorted_out:
    json.dump(results, sorted_out)
