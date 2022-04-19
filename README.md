# SloREL

V tem repozitoriju se nahaja rezultat aktivnosti A3.2 - R3.2.3 Orodje za ekstrakcijo povezav, ki je nastalo v okviru projekta Razvoj slovenščine v digitalnem okolju.

---

This repository contains a model for relation extraction in the Slovenian language and a docker service which uses this model to extract relations. Repository 
for the method which was used for training the model can be found on https://github.com/monologg/R-BERT. We used the
[CroSloEngual](https://huggingface.co/EMBEDDIA/crosloengual-bert) BERT model to fine-tune the model for our task.

## Project structure

- `src/` contains the script for predicting the relations and contains the source code of our work. fastapi service.
- `BERT_data.zip` contains our fine-tuned BERT model.
- `methods` contains scripts for training and testing models with three different relation extraction methods.
- `process_wikipedia_pages` contains scripts for converting HTML pages from Slovenian Wikipedia to text with marked relations and entities.



## Run with docker

To run this service we first need to extract the folder contained in BERT_data.zip into the root of this project.

#### Run GPU accelerated container 

 To run GPU accelerated docker containers you need to have an Nvidia GPU and [CUDA for WSL](https://docs.nvidia.com/cuda/wsl-user-guide/index.html) on Windows 10 or 11
 or [The NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) for Linux. 

 To build the docker image run:

 `docker build . -t bert_relation_extraction_gpu -f DockerfileGPU`

 To run the image in a GPU accelerated container use:
 
 ```
 docker run --rm -it --name bert_relation_extraction \
        --gpus=all \
        -e useGPU=True \
        --mount type=bind,source="$(pwd)"/BERT_data,target=/BERT_data,ro \
        -p:8000:8000 \
        bert_relation_extraction_gpu
  ```
 
#### Run normal container 


 To build the docker image run:

 `docker build . -t bert_relation_extraction -f Dockerfile`

 To run the image in a normal container use:

 ```
 docker run --rm -it --name bert_relation_extraction \
        --mount type=bind,source="$(pwd)"/BERT_data,target=/BERT_data,ro \
        -p:8000:8000 \
        bert_relation_extraction
  ```

 ## Run locally
 
 To run this project we recommend  python 3.8.
 
 First, we need to extract the folder contained in BERT_data.zip into the folder `src`.
 
 To install dependencies run `pip install -r requirements.txt -f https://download.pytorch.org/whl/cpu/torch_stable.html` in the root folder of this project.
 
 Run `uvicorn main:app --host 0.0.0.0 --port 8000` in the folder `src` to run the aplication on http://0.0.0.0:8000.

 #### Run with Nvidia CUDA

 For GPU acceleration you need to have the [CUDA toolkit](https://developer.nvidia.com/cuda-toolkit).

 To enable the GPU acceleration you will need to manually change the `use_gpu` parameter in `src/mark_entities.py` `classla.Pipeline` to `True`
 and string `device` in `src/predict.py` to `"cuda"`.
 
 ## Use
 
 Rest API is provided by FastAPI/uvicorn.
 
 After starting up the API, the OpenAPI/Swagger documentation will become accessible at http://localhost:8000/docs and http://localhost:8000/openapi.json.
 
 Service has a GET and POST endpoint at http://localhost:8000/predict/rel. Both endpoints require three parameters. 
 
 - String `text`  Text on which relation extraction will be performed.
 - Boolean `only_ne_as_mentions` Service will only use mentions in the text which are recognized as named entities if set to true.
 - Float `relationship_threshold` Each relation prediction has a confidence score between 0.0 and 1.0. This parameter can be used to prune prediction with a score below the threshold.
 
 To test the service, try sending a request with curl:
 
 ```
 curl -X POST -H 'Content-Type: application/json' \
	-H 'Accept: application/json' \
	-d '{"text": "France Prešeren je rojen v Vrbi.",  "only_ne_as_mentions": false,  "relationship_threshold": 0.4}' \
	'http://localhost:8000/predict/rel'
```
 
 
 ## Use with your own BERT model

This service can be used with BERT models fine-tuned by method [R-BERT](https://github.com/monologg/R-BERT). To use this service with your model
you need to create your own `BERT_data` folder in the root of this project for docker use or in the folder `src` for local use. This folder
needs to have `pytorch_model.bin`, `training_args.bin` and `config.json` that you get from fine-tuning the BERT model with [R-BERT](https://github.com/monologg/R-BERT).
You also need to add the `vocab.txt` file from the BERT model and `properties-with-labels.txt` which has relation labels and descriptions. 
Examples for these files can be found in the `BERT_data.zip` file

**Note** This project uses NER tagger for the Slovenian language. If you want to use this project for another language you will need to change 
`src/change mark_entities_in_text.py` and perhaps dependencies in `requirements.txt`.


**Note** This project uses `transformers.AutoTokenizer.from_pretrained` function for BERT tokenization. If you use a BERT model with a different recommended tokenization
method you can change it in the `load_auto_tokenizer` function in `src/utils.py`.

**Note** Relations in `properties-with-labels.txt` should have the same order as in `labels.txt` in project [R-BERT](https://github.com/monologg/R-BERT)
 when you fine-tuned BERT model.
 
 ---

> Operacijo Razvoj slovenščine v digitalnem okolju sofinancirata Republika Slovenija in Evropska unija iz Evropskega sklada za regionalni razvoj. Operacija se izvaja v okviru Operativnega programa za izvajanje evropske kohezijske politike v obdobju 2014-2020.

![](Logo_EKP_sklad_za_regionalni_razvoj_SLO_slogan.jpg)


