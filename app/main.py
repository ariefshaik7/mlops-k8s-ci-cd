from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np

app = FastAPI()
model = joblib.load("model/model.pkl")

class IrisSpeciesInput(BaseModel):
    Id: int
    SepalLengthCm: float
    SepalWidthCm: float
    PetalLengthCm: float
    PetalWidthCm: float

@app.get("/")
def read_root():
    return {"Messsage" : "Iris Species API is Live!"}

@app.post("/predict")
def predict(data: IrisSpeciesInput):
    input_data = np.array([[
        data.Id, 
        data.SepalLengthCm, 
        data.SepalWidthCm, 
        data.PetalLengthCm, 
        data.PetalWidthCm
    ]])

    
    prediction = model.predict(input_data)
    predicted_species = prediction[0]
    return {"predicted_species" : predicted_species}