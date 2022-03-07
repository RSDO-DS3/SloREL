# relation_extraction_BERT_cpu
Fastapi relation extraction service in docker which uses BERT embeddings.

---

In this repository contains model for relation extraction in the Slovenian language. Repository for the method which was used for training the model
can be found on https://github.com/monologg/R-BERT. We used the [CroSloEngual](https://huggingface.co/EMBEDDIA/crosloengual-bert) BERT model to fine-tune the
model for our task.

## Project structure

- `project/` contains the script for predicting the relations and contains the source code of our work. fastapi service.
- `BERT_data.zip` contains our fine-tuned BERT model.


## Run with docker

First we need to extract the folder contained in BERT_data.zip into the root of this project.

This project can be run with docker-compose with command `docker-compose up` in the root of the project.

You can also run it by building the docker image with command 

`docker build . -t bert_relation_extraction`

 in the root of the project and then running the image with
 
 ```
 docker run --rm -it --name bert_relation_extraction \
        --mount type=bind,source="$(pwd)"/BERT_data,target=/BERT_data,ro \
        -p:8000:8000 \
        bert_relation_extraction
  ```
 
 
 ## Run locally
 
 To run this project we recomend python 3.8.
 
 First we need to extract the folder contained in BERT_data.zip into the project folder.
 
 To install dependecies run `pip install -r requirements.txt -f https://download.pytorch.org/whl/cpu/torch_stable.html` in the root folder of this project.
 
 Run `uvicorn", "main:app --host 0.0.0.0 --port 8000` in the project folder to run the aplication on http://0.0.0.0:8000.
 
 ## Use
 
 Rest API is is provided by FastAPI/uvicorn.
 
 After starting up the API, the OpenAPI/Swagger documentation will become accessible at http://0.0.0.0:8000/docs and http://0.0.0.0:8000/openapi.json.
 
 For extracting the relations in a sentence you can send get request to http://0.0.0.0:8000/find_relations/{text} where {text} represents the sentence.


 
