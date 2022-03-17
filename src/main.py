from fastapi import FastAPI
from typing import List
from pydantic import BaseModel
from predict import predict
from mark_entities import mark_entities_in_text
from uuid import uuid4


app = FastAPI()

class Mention(BaseModel):
    text: str
    id: int
    ner_type: str
    
class Relation(BaseModel):
    subject_id: int
    object_id: int
    wikidata_tag: str
    description: str
    score: float

class MarkedRelation(BaseModel):
    sentence: str
    mentions: List[Mention]
    relationships: List[Relation]
    

def get_relations_from_text(text, call_id):
    marked_sentences = mark_entities_in_text(text, call_id)
    output = []
    for sentence in marked_sentences:
        relations = predict(sentence["relation_candidates"], call_id)
        output.append({"sentence": sentence["sentence_text"], "mentions": sentence["mention_set"],
                "relationships": predict(sentence["relation_candidates"], call_id)})
    return output
    
    

@app.get("/find_relations/{text}", response_model=List[MarkedRelation])
async def find_relations(text: str):
    call_id = uuid4() # used to differentiate different calls in logs
    return get_relations_from_text(text, call_id)


@app.get("/find_relations", response_model=List[MarkedRelation])
async def find_relations2(text: str= "Slovenija je članica EU."):
    call_id = uuid4() # used to differentiate different calls in logs
    return get_relations_from_text(text, call_id)
