#!/bin/bash

docker run --rm -it --name bert_relation_extraction \
   --platform linux/amd64 \
       --mount type=bind,source="$(pwd)"/BERT_data,target=/BERT_data,ro \
       -p:8000:8000 \
       bert_relation_extraction