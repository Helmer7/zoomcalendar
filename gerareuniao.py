import pytz
import requests
from requests.auth import HTTPBasicAuth
from flask import Flask, jsonify, request, render_template, redirect, url_for
import datetime
import os
from flask_sqlalchemy import SQLAlchemy
from models import Reuniao, db
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


access_token = None
token_expiration = None
client_id = os.getenv("ZOOM_CLIENT_ID", "zjm3XiLSpSR9FSjn4ebqA")
client_secret = os.getenv("ZOOM_CLIENT_SECRET", "MkQzk4nQUO8WjwGg4z8bN15u3uNCG5tB")
account_id = os.getenv("ZOOM_ACCOUNT_ID", "JoFnTUNXSBacV9W36l3lZA")


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:KKnSFofUTdzryLUGzOcTSbuswOjDCyoJ@autorack.proxy.rlwy.net:36990/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


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
    
    
    try:
        
        local_time = datetime.datetime.strptime(start_time, "%Y-%m-%dT%H:%M")
        local_time = pytz.timezone("America/Sao_Paulo").localize(local_time)
        utc_time = local_time.astimezone(pytz.utc)
        start_time_iso = utc_time.strftime("%Y-%m-%dT%H:%M:%SZ")  
    except ValueError as e:
        print(f"Erro ao processar o horário: {e}")
        raise Exception("Formato de data e hora inválido.")

    url = "https://api.zoom.us/v2/users/me/meetings"
    
    dados_reuniao = {
        "topic": topic,
        "type": 2,
        "start_time": start_time_iso,  
        "duration": duration,
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
def index():
    return redirect(url_for('form_reuniao'))


@app.route('/form')
def form_reuniao():
    return render_template('index.html')


@app.route('/criar-reuniao', methods=['POST'])
def criar_reuniao():
    try:
        
        topic = request.form.get('topic')
        start_time = request.form.get('start_time')
        duration = int(request.form.get('duration'))
        agenda = request.form.get('agenda')

        
        reuniao_existente = verificar_reuniao_existente(topic, start_time, duration)
        if reuniao_existente:
            return jsonify({"join_url": reuniao_existente.join_url})

        
        join_url = criar_reuniao_zoom(topic, start_time, duration, agenda)

        

        return jsonify({"join_url": join_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)