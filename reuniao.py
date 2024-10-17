import requests
import json
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Zoom Webhook!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


url = "https://api.zoom.us/v2/users/me/meetings"


access_token = 'eyJzdiI6IjAwMDAwMSIsImFsZyI6IkhTNTEyIiwidiI6IjIuMCIsImtpZCI6ImUwNGI2MjgwLWE5NjYtNGMzNy05MGE4LTM4ZWRlZmExZjFmOCJ9.eyJhdWQiOiJodHRwczovL29hdXRoLnpvb20udXMiLCJ1aWQiOiJhaFBxRy1nU1F2Q3BIWUd0UnljVF9RIiwidmVyIjoxMCwiYXVpZCI6ImQ1OTM3NGY0M2JiMzJmM2RjMGRlYzFkMjhiNWFhYzkzNmEyYjQ1Yjk5NGIyMDU2OWY2ZTZlNzJhZGRlNzM4MGUiLCJuYmYiOjE3MjkxODcxODMsImNvZGUiOiJZYWViZlJ2c1IycVFwbVlBVWFkN0xncEZaTWczMnNyQmwiLCJpc3MiOiJ6bTpjaWQ6emptM1hpTFNwU1I5RlNqbjRlYnFBIiwiZ25vIjowLCJleHAiOjE3MjkxOTA3ODMsInR5cGUiOjMsImlhdCI6MTcyOTE4NzE4MywiYWlkIjoiSm9GblRVTlhTQmFjVjlXMzZsM2xaQSJ9.CV9lQrQb4Pl2bd0oEoXTOXiDhm6gsPoUL48UJQRtiKqAQqoBFHwY1jx7UtW5vl8Ut2fx2ndyYYmyvb22E-PHsg'

headers = {
    'authorization': f'Bearer {access_token}',
    'content-type': 'application/json'
}

# Definições da reunião
data = {
    "topic": "Aula de inglês",
    "type": 2,  # Reunião agendada
    "start_time": "2024-10-16T10:00:00",  # Exemplo de data
    "duration": 2,  # Duração em minutos
    "timezone": "America/Sao_Paulo",
    "agenda": "Descrição da aula"
}


response = requests.post(url, headers=headers, data=json.dumps(data))

if response.status_code == 201:
    print("Reunião criada com sucesso")
    print("Link da reunião:", response.json()['join_url'])
else:
    print(f"Erro {response.status_code}: {response.text}")
