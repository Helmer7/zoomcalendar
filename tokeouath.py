import requests
from requests.auth import HTTPBasicAuth

url = "https://zoom.us/oauth/token"
client_id = "zjm3XiLSpSR9FSjn4ebqA"
client_secret = "MkQzk4nQUO8WjwGg4z8bN15u3uNCG5tB"
account_id = "JoFnTUNXSBacV9W36l3lZA"


response = requests.post(
    url,
    params={
        'grant_type': 'account_credentials',
        'account_id': account_id
    },
    auth=HTTPBasicAuth(client_id, client_secret)
)


if response.status_code == 200:
    access_token = response.json()['access_token']
    print("Token de acesso gerado:", access_token)
else:
    print(f"Erro {response.status_code}: {response.text}")
