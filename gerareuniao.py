import requests
from requests.auth import HTTPBasicAuth
from flask import Flask, jsonify
import datetime
import os
from models import Reuniao, db

access_token = None
token_expiration = None

client_id = os.getenv("ZOOM_CLIENT_ID", "zjm3XiLSpSR9FSjn4ebqA")
client_secret = os.getenv("ZOOM_CLIENT_SECRET", "MkQzk4nQUO8WjwGg4z8bN15u3uNCG5tB")
account_id = os.getenv("ZOOM_ACCOUNT_ID", "JoFnTUNXSBacV9W36l3lZA")

app = Flask(__name__)


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


def verificar_token():
    if access_token is None or token_expiration <= datetime.datetime.now():
        gerar_token()


def verificar_reuniao_existente(topic, start_time, duration):
    reuniao_existente = Reuniao.query.filter_by(topic=topic, start_time=start_time, duration=duration).first()
    return reuniao_existente


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


@app.route('/')
def criar_reuniao_automatica():
    try:
        
        topic = "Reunião Automática"
        start_time = (datetime.datetime.now() + datetime.timedelta(minutes=5)).isoformat()
        duration = 30
        agenda = "Agenda da reunião automática"
        
        
        reuniao_existente = verificar_reuniao_existente(topic, start_time, duration)
        if reuniao_existente:
            return jsonify({"join_url": reuniao_existente.join_url})
        
        
        join_url = criar_reuniao_zoom(topic, start_time, duration, agenda)
        
        
        nova_reuniao = Reuniao(topic=topic, start_time=start_time, duration=duration, join_url=join_url)
        db.session.add(nova_reuniao)
        db.session.commit()

        return jsonify({"join_url": join_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  
    app.run(host='0.0.0.0', port=port)