import requests

# Make a simple GET request with a 5-second timeout
response = requests.get("https://api.github.com/user", timeout=5)

print("Status code:", response.status_code)
print("Response body:", response.text)
