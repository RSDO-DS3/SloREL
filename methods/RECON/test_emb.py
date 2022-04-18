import json

with open('final_entity_embeddings.json', 'r') as f:
    gat_embeddings = json.load(f)

print(type(gat_embeddings["559181"]))
print(gat_embeddings["559181"])
print(gat_embeddings["559181"] + gat_embeddings["559182"])