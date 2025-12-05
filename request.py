import requests
url = "https://v3.alapi.cn/api/zaobao"
querystring = {"token": "", "format": "json"}
headers = {"Content-Type": "application/json"}
response = requests.get(url, headers=headers, params=querystring)
print(response.json())
