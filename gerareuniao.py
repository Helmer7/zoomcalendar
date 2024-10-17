import requests
from requests.auth import HTTPBasicAuth
from flask import Flask, jsonify
import datetime
import os
from models import Reuniao, db

# Variáveis Globais
access_token = None
token_expiration = None

client_id = os.getenv("ZOOM_CLIENT_ID", "zjm3XiLSpSR9FSjn4ebqA")
client_secret = os.getenv("ZOOM_CLIENT_SECRET", "MkQzk4nQUO8WjwGg4z8bN15u3uNCG5tB")
account_id = os.getenv("ZOOM_ACCOUNT_ID", "JoFnTUNXSBacV9W36l3lZA")

app = Flask(__name__)

# Função para gerar o token de acesso ao Zoom
def gerar_token():
    global access_token
    global token_expiration

    print("Gerando novo token de acesso...")  
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
        print(f"Token gerado: {access_token}") 
    else:
        print(f"Erro {response.status_code}: {response.text}")
        raise Exception("Não foi possível gerar o token")

# Função para verificar se o token ainda é válido
def verificar_token():
    if access_token is None or token_expiration <= datetime.datetime.now():
        gerar_token()

# Função para verificar se a reunião já existe (verifica se há reunião com o mesmo nome e horário dentro de um intervalo de 1 hora)
def verificar_reuniao_existente(topic, start_time, duration):
    # Procurar reuniões com o mesmo tópico e que comecem na mesma data
    start_time_obj = datetime.datetime.fromisoformat(start_time)
    uma_hora_antes = start_time_obj - datetime.timedelta(hours=1)
    uma_hora_depois = start_time_obj + datetime.timedelta(hours=1)

    reuniao_existente = Reuniao.query.filter(
        Reuniao.topic == topic,
        Reuniao.start_time.between(uma_hora_antes, uma_hora_depois),
        Reuniao.duration == duration
    ).first()

    return reuniao_existente

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

    print("Enviando requisição para criar a reunião...")  
    response = requests.post(url, json=dados_reuniao, headers=headers)

    if response.status_code == 201:
        print("Reunião criada com sucesso!") 
        return response.json()['join_url']
    else:
        print(f"Erro ao criar reunião: {response.status_code} - {response.text}")
        raise Exception(f"Erro ao criar reunião: {response.status_code} - {response.text}")

# Função para criar uma reunião automaticamente
@app.route('/')
def criar_reuniao_automatica():
    try:
        # Parâmetros da reunião
        topic = "Reunião Automática"
        start_time = (datetime.datetime.now() + datetime.timedelta(minutes=5)).isoformat()
        duration = 30
        agenda = "Agenda da reunião automática"
        
        # Verificar se a reunião já existe
        reuniao_existente = verificar_reuniao_existente(topic, start_time, duration)
        if reuniao_existente:
            print(f"Reunião já existe: {reuniao_existente.join_url}")
            return jsonify({"join_url": reuniao_existente.join_url})
        
        # Criar uma nova reunião se não existir
        join_url = criar_reuniao_zoom(topic, start_time, duration, agenda)
        
        # Salvar reunião no banco de dados
        nova_reuniao = Reuniao(topic=topic, start_time=start_time, duration=duration, join_url=join_url)
        db.session.add(nova_reuniao)
        db.session.commit()

        return jsonify({"join_url": join_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  
    app.run(host='0.0.0.0', port=port)
