import requests
from requests.auth import HTTPBasicAuth
import time

# Suas credenciais da API Zoom
client_id = "zjm3XiLSpSR9FSjn4ebqA"
client_secret = "MkQzk4nQUO8WjwGg4z8bN15u3uNCG5tB"
account_id = "JoFnTUNXSBacV9W36l3lZA"

# Armazena o token e o tempo de expiração
access_token = None
token_expiration = None

def gerar_token():
    global access_token
    global token_expiration

    # Verifica se o token já existe e se não está expirado
    if access_token and token_expiration and time.time() < token_expiration:
        return access_token

    # Se o token estiver expirado ou inexistente, gerar um novo
    url = "https://zoom.us/oauth/token"

    response = requests.post(
        url,
        params={
            'grant_type': 'account_credentials',
            'account_id': account_id
        },
        auth=HTTPBasicAuth(client_id, client_secret)
    )

    if response.status_code == 200:
        data = response.json()
        access_token = data['access_token']
        token_expiration = time.time() + data['expires_in']  # Expires_in é o tempo em segundos

        print("Novo token gerado:", access_token)
        return access_token
    else:
        raise Exception(f"Erro {response.status_code}: {response.text}")
def gerar_token():
    global access_token
    global token_expiration

    print("Gerando token...")  # Para verificar se a função é chamada
    # O restante do código
