import requests
import json
import os

print(os.getcwd())

url = "http://0.0.0.0:8090/receipt"

req_json = {
            "filename": '/home/ubuntu/policy/AI-Policy/Data/Google_Play/Restricted Content-Child Endangerment/Restricted Content-Child Endangerment.docx',
            "transaction_id": "India_1358"
        }

response = requests.post(url, json=req_json)
print(response.json())