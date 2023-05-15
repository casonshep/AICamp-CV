import requests
import json

API_URL = "https://api-inference.huggingface.co/models/casonshep/Turtle-Species-Classification"
headers = {"Authorization": "Bearer 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"}


def query(filename):
    with open(filename, "rb") as f:
        data = f.read()
        j = {"wait_for_model":True}
    response = requests.post(API_URL, headers=headers, data=data, json=j)
    return response.json() 
