import requests
from requests.auth import HTTPBasicAuth
from flask import Flask, jsonify
import datetime
import os

# Variáveis Globais
access_token = None
token_expiration = None

client_id = os.getenv("ZOOM_CLIENT_ID", "zjm3XiLSpSR9FSjn4ebqA")
client_secret = os.getenv("ZOOM_CLIENT_SECRET", "MkQzk4nQUO8WjwGg4z8bN15u3uNCG5tB")
account_id = os.getenv("ZOOM_ACCOUNT_ID", "JoFnTUNXSBacV9W36l3lZA")

# Inicializando Flask
app = Flask(__name__)

# Função para gerar o token de acesso ao Zoom
def gerar_token():
    global access_token
    global token_expiration

    print("Gerando novo token de acesso...")  # Log de geração do token
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
        token_expiration = datetime.datetime.now() + datetime.timedelta(seconds=data['expires_in'])
        print(f"Token gerado: {access_token}")  # Mostra o token gerado
    else:
        print(f"Erro {response.status_code}: {response.text}")
        raise Exception("Não foi possível gerar o token")

# Função para verificar se o token ainda é válido
def verificar_token():
    if access_token is None or token_expiration <= datetime.datetime.now():
        gerar_token()

# Função para criar a reunião no Zoom
def criar_reuniao_zoom(topic, start_time, duration, agenda):
    verificar_token()  # Garante que o token é válido
    url = "https://api.zoom.us/v2/users/me/meetings"
    
    dados_reuniao = {
        "topic": topic,
        "type": 2,
        "start_time": start_time,  # Data e hora fornecidas
        "duration": duration,
        "timezone": "America/Sao_Paulo",
        "agenda": agenda
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    print("Enviando requisição para criar a reunião...")  # Log para debug
    response = requests.post(url, json=dados_reuniao, headers=headers)

    if response.status_code == 201:
        print("Reunião criada com sucesso!")  # Log de sucesso
        return response.json()['join_url']
    else:
        print(f"Erro ao criar reunião: {response.status_code} - {response.text}")
        raise Exception(f"Erro ao criar reunião: {response.status_code} - {response.text}")

# Função para criar uma reunião automaticamente ao iniciar o app
@app.route('/')
def criar_reuniao_automatica():
    try:
        # Exemplos de parâmetros
        topic = "Reunião Automática"
        start_time = (datetime.datetime.now() + datetime.timedelta(minutes=5)).isoformat()
        duration = 30
        agenda = "Agenda da reunião automática"
        
        join_url = criar_reuniao_zoom(topic, start_time, duration, agenda)
        return jsonify({"join_url": join_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Rodando o servidor Flask
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # A Vercel usa a variável de ambiente "PORT"
    app.run(host='0.0.0.0', port=port)
