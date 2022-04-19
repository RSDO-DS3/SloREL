# SloREL


This folder contains scripts for extracting text from Wikipedia HTML pages and marking this text with entities and relations.

## Setup

To use scripts in this folder you will need to install dependancies with `pip install -r requirements.txt -f https://download.pytorch.org/whl/cpu/torch_stable.html`
for CPU pytorch or `pip install -r requirements.txt -f https://download.pytorch.org/whl/cu101/torch_stable.html` for GPU accelerated pytorch.

## Converting HTML pages to text with marked entities

#### Setting up the Elasticsearch

For entity linking we use local elasticsearch database and WikiData API. To use elasticsearch database you will need to setup the 
[Elasticsearch 7.15.2](https://www.elastic.co/downloads/past-releases/elasticsearch-7-15-2). You will also need to download the 
[WikiData bz2 JSON dump](https://dumps.wikimedia.org/wikidatawiki/entities). In `settings.json` file set `wikidata_dump_file` parameter
to the location of WikiData dump and `elasticsearch_dump` to the location of the file which will be generated to dump to the Elasticsearch.
Run `make_wiki_entity_dump.py` to generate this dump file. You can than dump this file on the Elasticsearch with [elasticdump](https://www.npmjs.com/package/elasticdump)
with `elasticdump  --output={address of your Elasticsearch}/wikidataentityindex/  --input={name of generated dump file}  --type=data`.
Set the `elastic_search_url` in `settings.json` to the address of your Elasticsearch. You can also skip this part and just set the value null to the `elastic_search_url` 
parameter. In this case the Elasticsearch will not be used for entity linking.

#### Running the script

In `settings.json` set the `page_folder` parameter to the location of the folder containing the HTML pages of Wikipedia and `text_with_entities_folder` to the
folder where you want to save txt files containing text with marked entities. Then run `extract_text_and_entities.py` to start the process. This part takes the longest
time to execute and can be stopped and resumed without losing the progress of pages which had their text already extracted and marked with entities.

## Marking relations

To mark relations you will first need to download the [WikiData bz2 JSON dump](https://dumps.wikimedia.org/wikidatawiki/entities). You will need to download this dump
and set `wikidata_dump_file` parameter in `settings.json` to the location of this dump. You will also need to set `relation_triplets_folder` parameter to the folder which will
contain files with extracted relations. Run `make_relation_triplets.py` to extract these triplets. 

Set `text_with_entities_and_relations_folder` to the folder which will contain text files with marked relations and then run `tag_relations.py`. If you have a lot of RAM you can 
set the lru_cache maxsize in this script up to 1000. Larger number will result in smaller disc load but requires more RAM.

#### Filtering the relations

Script `filter_relations.py` contains some rules for filtering the relations which are less likely to be correct. If you want to filter the relations in this dataset you 
set the `text_with_entities_and_filtered_relations_folder` parameter in `settings.json` to the location where filtered relations will be saved and run this script. 
This sript will also add empty relatons to the dataset if `add_empty_relations` parameter in `settings.json` is set to true. If you filtered the dataset you should
also set `use_filtered_data parameter` to true so the next steps use the data from folder with filtered relations.

## Make dataset for LSTM and RECON method

In `settings.json` set the parameters from `json` value to the desired values. Then run `make_json_dataset.py`

## Make dataset for BERT method

In `settings.json` set the parameters from `bert` value to the desired values. Then run `make_bert_dataset.py`


## Make dataset for training the entity embeddings and knowledge graph for RECON method

`methods\RECON\entity_context\entity_context.rar` already contains example of a knowledge graph and a dataset for entity embeddings training. 

To make knowledge graph you will need to download the [WikiData bz2 JSON dump](https://dumps.wikimedia.org/wikidatawiki/entities)
and set `wikidata_dump_file` parameter in `settings.json` to the location of this dump. You can also cut the size of the graph
by using only certain entities. Parameter `knowledge_graph_entity_candidates` in `settings.json` contains the file with a list of
entities which will be used for knowledge graph. Example of such file is `entity_candidates.txt` in this folder. If you set `knowledge_graph_entity_candidates`
to null all entities will be used. Set the parameter `knowledge_graph` to the location of the generated knowledge_graph and `run make_knowledge_graph.py`.

To make dataset for training the entity embeddings you will need `knowledge_graph_entity_candidates` and `knowledge_graph_relation_candidates`
files set in `settings.json`. We have examples for both in this repository. Set the parameters under `entity_context` in `settings.json` for split
and file locations and then run `make_entity_pairs_for_context_train.py`