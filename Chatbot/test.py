import requests

query = {'task_name': 'update2'}
new_query = {'category': 'jobs'}

url = "http://127.0.0.1:8000/update"

data = {
    "query": query,
    "new_query": new_query
}

response = requests.patch(url, json=data)
print(response.json())