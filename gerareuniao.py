import requests
from requests.auth import HTTPBasicAuth
from flask import Flask, jsonify, request
import datetime

# Variáveis Globais
access_token = None
token_expiration = None

client_id = "zjm3XiLSpSR9FSjn4ebqA"
client_secret = "MkQzk4nQUO8WjwGg4z8bN15u3uNCG5tB"
account_id = "JoFnTUNXSBacV9W36l3lZA"

# Inicializando Flask
app = Flask(__name__)

# Função para gerar o token de acesso ao Zoom
def gerar_token():
    global access_token
    global token_expiration

    url = "https://zoom.us/oauth/token"
    response = requests.post(
        url,
        params={'grant_type': 'account_credentials', 'account_id': account_id},
        auth=HTTPBasicAuth(client_id, client_secret)
    )

    if response.status_code == 200:
        data = response.json()
        access_token = data['access_token']
        token_expiration = datetime.datetime.now() + datetime.timedelta(seconds=data['expires_in'])
    else:
        raise Exception("Não foi possível gerar o token")

# Função para verificar se o token ainda é válido
def verificar_token():
    if access_token is None or token_expiration <= datetime.datetime.now():
        gerar_token()

# Função para criar a reunião no Zoom
def criar_reuniao_zoom(topic, start_time, duration, agenda):
    verificar_token()
    url = "https://api.zoom.us/v2/users/me/meetings"
    
    dados_reuniao = {
        "topic": topic,
        "type": 2,
        "start_time": start_time,
        "duration": duration,
        "timezone": "America/Sao_Paulo",
        "agenda": agenda
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=dados_reuniao, headers=headers)
    if response.status_code == 201:
        return response.json()['join_url']
    else:
        raise Exception(f"Erro ao criar reunião: {response.status_code} - {response.text}")

# Função chamada ao inicializar o servidor para criar uma reunião automaticamente
@app.before_first_request
def inicializar_reuniao():
    try:
        topic = "Reunião Automática"
        start_time = (datetime.datetime.now() + datetime.timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%S")
        duration = 30
        agenda = "Reunião criada automaticamente"

        join_url = criar_reuniao_zoom(topic, start_time, duration, agenda)
        print(f"Reunião criada automaticamente. Link: {join_url}")
    except Exception as e:
        print(f"Erro ao criar reunião automaticamente: {e}")

# Rota para criar uma reunião via URL
@app.route('/criar_reuniao', methods=['GET'])
def criar_reuniao():
    try:
        topic = "Reunião Automática"
        start_time = "2024-10-18T15:00:00"
        duration = 30
        agenda = "Agenda da reunião"
        
        join_url = criar_reuniao_zoom(topic, start_time, duration, agenda)
        return jsonify({"join_url": join_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Rodando o servidor Flask
if __name__ == '__main__':
    app.run(debug=True)
