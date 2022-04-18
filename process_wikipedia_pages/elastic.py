from elasticsearch import Elasticsearch
import editdistance
from functools import lru_cache
from json import load


with open("settings.json", "r") as settings_file:
    settings = load(settings_file)

if settings['elastic_search_url']:
    es = Elasticsearch([settings['elastic_search_url']])
else:
    es = None
docType = "_doc"

@lru_cache(maxsize=2800)
def entitySearch(query):
    if not es:
        return None
        
    indexName = "wikidataentityindex"
    results = []
    ###################################################

    ###################################################
    elasticResults = es.search(index=indexName, doc_type=docType, body={
        "query": {
            "match": {
                "label": {
                    "query": query,
                    "fuzziness": "AUTO"

                }
            }
        }, "size": 100
    }
                               )
    for result in elasticResults['hits']['hits']:
        edit_distance = editdistance.eval(result["_source"]["label"].lower().replace('.', '').strip(),
                                          query.lower().strip())
        if edit_distance == 0:
            results.append([result["_source"]["label"], result["_source"]["uri"], result["_score"] * 50, 30])

    if len(results) == 0:
        return None

    results = sorted(results, key=lambda x: (int(x[1][x[1].rfind("/") + 2:-1]), -x[3], -x[2]))
    seen = set()
    results = [x for x in results if x[1] not in seen and not seen.add(x[1])]
    results = results[:15]
    results = sorted(results, key=lambda x: (-x[3], int(x[1][x[1].rfind("/") + 2:-1])))
    return results[0][1][32:-1]
