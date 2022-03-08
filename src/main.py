from fastapi import FastAPI
from typing import List
from pydantic import BaseModel
from predict import predict
from mark_entities import mark_entities_in_text
from uuid import uuid4


app = FastAPI()

class Entity(BaseModel):
    text: str
    sentence_position: int
    
class Relation(BaseModel):
    WikiData_tag: str
    description: str

class MarkedRelation(BaseModel):
    sentence: str
    entity1: Entity
    entity2: Entity
    relation: Relation
    score: float

@app.get("/find_relations/{text}", response_model=List[MarkedRelation])
async def find_relations(text: str):
    call_id = uuid4() # used to differentiate different calls in logs
    return predict(mark_entities_in_text(text, call_id), call_id)


@app.get("/find_relations", response_model=List[MarkedRelation])
async def find_relations2(text: str= "Slovenija je članica EU."):
    call_id = uuid4() # used to differentiate different calls in logs
    return predict(mark_entities_in_text(text, call_id), call_id)
