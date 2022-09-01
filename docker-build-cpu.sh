#!/bin/bash

docker buildx build --platform linux/amd64 . -t bert_relation_extraction -f Dockerfile