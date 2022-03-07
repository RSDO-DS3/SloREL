from fastapi import FastAPI
from typing import List
from pydantic import BaseModel
from predict import predict
from mark_entities import mark_entities_in_text

app = FastAPI()

class MarkedRelation(BaseModel):
    sentence: str
    relation: str
    score: float

@app.get("/find_relations/{text}", response_model=List[MarkedRelation])
async def root(text: str):
    return predict(mark_entities_in_text(text))
