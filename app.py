from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

PANDASCORE_TOKEN = os.getenv("PANDASCORE_TOKEN")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message'].lower()

    if 'jogadores' in user_message:
        reply = get_furia_players()
    elif 'proxima partida' in user_message or 'jogo' in user_message:
        reply = get_next_furia_match()
    else:
        reply = 'Fala FURIA fanático! Pergunte sobre "jogadores" ou "próxima partida"!'

    return jsonify({'reply': reply})

def get_furia_players():
    try:
        res = requests.get(
            'https://api.pandascore.co/csgo/teams?search[name]=FURIA',
            headers={"Authorization": f"Bearer {PANDASCORE_TOKEN}"}
        )
        data = res.json()
        players = data[0]['players']
        return 'Jogadores da FURIA:\n' + '\n'.join(f"• {p['first_name'] or p['name']}" for p in players)
    except Exception as e:
        print(e)
        return "Erro ao buscar jogadores!"

def get_next_furia_match():
    try:
        res = requests.get(
            'https://api.pandascore.co/csgo/matches/upcoming?filter[team_id]=2227',
            headers={"Authorization": f"Bearer {PANDASCORE_TOKEN}"}
        )
        matches = res.json()
        if not matches:
            return 'Nenhum jogo próximo encontrado.'
        next_match = matches[0]
        return f"Próxima partida: {' vs '.join(o['opponent']['name'] for o in next_match['opponents'])} em {next_match['begin_at']}"
    except Exception as e:
        print(e)
        return "Erro ao buscar partidas!"

if __name__ == '__main__':
    app.run(debug=True)
