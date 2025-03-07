from fastapi import FastAPI
from pymongo import MongoClient


app = FastAPI()

client = MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]
collection = db["mycollection"]

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/add")
def add_data(data: dict):
    collection.insert_one(data)
    return {"message": "Data added successfully", "data": data}

@app.get("/get")
def get_data():
    data = list(collection.find({}, {"_id": 0}))
    return {"data": data}

