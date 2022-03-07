docker run --name bert_relation_extraction --mount type=bind,source="$(pwd)"/BERT_data,target=/BERT_data -p:8000:8000 bert_relation_extraction
