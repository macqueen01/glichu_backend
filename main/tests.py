from rest_framework.test import APIClient

client = APIClient()
res = client.get('http://localhost:8000/scrolls/browse?id=1')
print(res.json())


