from fastapi import FastAPI, Body
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
    
    
class PredictRelationRequestBody(BaseModel):
    text: str
    only_ne_as_mentions: bool
    relationship_threshold: float
    

def get_relations_from_text(text, relationship_threshold, only_ne_as_mentions, call_id):
    marked_sentences = mark_entities_in_text(text, only_ne_as_mentions, call_id)
    output = []
    for sentence in marked_sentences:
        output.append({"sentence": sentence["sentence_text"], "mentions": sentence["mention_set"],
                "relationships": predict(sentence["relation_candidates"], relationship_threshold, call_id)})
    return output
    
    

@app.post("/predict/rel", response_model=List[MarkedRelation])
async def find_relations_post(req_body: PredictRelationRequestBody = Body(
            example=PredictRelationRequestBody(
                relationship_threshold=60.0,
                only_ne_as_mentions=False,
                text='Slovenija je članica EU.'
            ),
            default=None,
            media_type='application/json'
        )):
    call_id = uuid4() # used to differentiate different calls in logs
    return get_relations_from_text(req_body.text, req_body.relationship_threshold, req_body.only_ne_as_mentions, call_id)


@app.get("/predict/rel", response_model=List[MarkedRelation])
async def find_relations_get(text: str= "Slovenija je članica EU.", relationship_threshold: float=60.0, only_ne_as_mentions: bool=False):
    call_id = uuid4() # used to differentiate different calls in logs
    return get_relations_from_text(text, relationship_threshold, only_ne_as_mentions, call_id)
