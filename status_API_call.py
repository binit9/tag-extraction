import requests
import json
import os

print(os.getcwd())

url = "http://100.27.43.61:8090/status"

status_json = {
               "transaction_id": "India_1358"
           }

response = requests.post(url, json=status_json)
print(response.json())