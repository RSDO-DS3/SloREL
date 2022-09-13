#!/bin/bash

docker run \
    -d \
    -it \
    --restart always \
    --name bert_relation_extraction \
    --platform linux/amd64 \
    --mount type=bind,source="$(pwd)"/BERT_data,target=/BERT_data,ro \
    -p:5001:8000 \
    bert_relation_extraction