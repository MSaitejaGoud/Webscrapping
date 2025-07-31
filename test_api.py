import requests
import json

# Test the API
url = "http://localhost:8000/analyze"

# Test data
test_data = {
    "url": "https://www.google.com"
}

try:
    response = requests.post(url, json=test_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
    print(f"Response text: {response.text if 'response' in locals() else 'No response'}")