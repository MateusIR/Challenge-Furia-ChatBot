from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
import pytz

load_dotenv()

app = Flask(__name__)

PANDASCORE_TOKEN = os.getenv("PANDASCORE_TOKEN")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message'].lower()
    if '1' in user_message or 'historia' in user_message:
        reply = furia_historia()
    elif '2' in user_message or 'jogadores' in user_message:
        reply = get_furia_players()
    elif '3' in user_message or 'proximo jogo' in user_message:
        reply = get_next_furia_match()
    elif '4' in user_message or 'ultimos jogos' in user_message:
        reply = get_last_furia_matches()
    elif '5' in user_message or 'redes sociais' in user_message:
        reply = furia_social()
    elif '6' in user_message or 'roupa' in user_message:
        reply = furia_roupas()
    else:
        reply = 'Fala FURIOSO(A)!\n O que quer saber hoje?\n\n' \
        '1 - nossa história\n' \
        '2 - jogadores\n' \
        '3 - proximo jogo\n' \
        '4 - ultimos jogos\n' \
        '5 - nossas redes sociais\n' \
        '6 - nossas roupas\n' \

        
        

    return jsonify({'reply': reply})



def get_furia_players():
    try:
        res = requests.get(
            'https://api.pandascore.co/csgo/teams?search[name]=FURIA',
            headers={"Authorization": f"Bearer {PANDASCORE_TOKEN}"}
        )
        data = res.json()
        players = data[2]['players']
        return 'Integrantes da FURIA CS2:\n\n' + '\n'.join(f"\n• {p['first_name']} \"{p['name']}\" {p['last_name']} \n {p['age']} anos - {p['nationality']}" for p in players)
    except Exception as e:
        print(e)
        return "Erro ao buscar jogadores!"




def get_next_furia_match():
    try:
        # Endpoint para CS2 (não CSGO)
        res = requests.get(
            'https://api.pandascore.co/csgo/matches/upcoming',
            headers={"Authorization": f"Bearer {PANDASCORE_TOKEN}"}
        )
        matches = res.json()

        # Buscar o primeiro jogo onde FURIA está entre os times
        for match in matches:
            if any(team['opponent']['name'].lower() == 'ence' for team in match.get('opponents', [])):
                teams = [team['opponent']['name'] for team in match['opponents']]
                opponent = [t for t in teams if t.lower() != 'furia'][0] if len(teams) > 1 else "TBD"
                date = match['begin_at']
                date_br = converter_utc_para_brasilia(date)
                tournament = match['tournament']['name']
                return (
                    f"Próxima partida da FURIA:\n\n"
                    f"FURIA vs {opponent}\n"
                    f"Data e hora (BR): {date_br}\n"
                    f"Torneio: {tournament}"
                )

        return "Nenhuma partida futura da FURIA encontrada."
    except Exception as e:
        print(e)
        return "Erro ao buscar partidas!"





def get_last_furia_matches():
    try:
        url = 'https://api.pandascore.co/csgo/matches/past'
        params = {
            'filter[team_id]': 2227,  # ID da FURIA no CSGO
            'sort': '-begin_at',      # Ordena do mais recente para o mais antigo
            'page[size]': 5           # Limita a 5 partidas
        }
        headers = {
            "Authorization": f"Bearer {PANDASCORE_TOKEN}"
        }

        res = requests.get(url, headers=headers, params=params)
        matches = res.json()

        if not matches:
            return "Nenhuma partida recente encontrada."

        resposta = "🕹️ Últimos 5 jogos da FURIA (CSGO):\n"
        for match in matches:
            opponents = [o['opponent']['name'] for o in match.get('opponents', [])]
            placar = match.get('results', [])
            score_str = f"{placar[0]['score']} x {placar[1]['score']}" if len(placar) == 2 else "Placar indisponível"

            data_brasilia = converter_utc_para_brasilia(match.get('begin_at', ''))

            resposta += (
                f"\n🏆 Torneio: {match['tournament']['name']}\n"
                f"🗓️ Data: {data_brasilia}\n"
                f"⚔️ {' vs '.join(opponents)}\n"
                f"🔢 Placar: {score_str}\n"
                f"{'-'*30}"
            )

        return resposta
    except Exception as e:
        print(f"Erro ao buscar partidas passadas: {e}")
        return "Erro ao buscar últimas partidas!"


def furia_historia():
    return """ 
historiaaaa
        """
def furia_social():
    return """ 
olha as redeees
        """

def furia_roupas():
     return """
olha a roupaaaa
            """









def converter_utc_para_brasilia(data_utc):
    try:
        # Parse da data e hora no formato ISO
        utc_dt = datetime.fromisoformat(data_utc.replace("Z", "+00:00"))

        # Se já tiver fuso, não precisa localizar
        if utc_dt.tzinfo is None:
            utc = pytz.utc
            utc_dt = utc.localize(utc_dt)

        # Converter para o fuso de Brasília
        brasilia = pytz.timezone('America/Sao_Paulo')
        brasilia_dt = utc_dt.astimezone(brasilia)

        return brasilia_dt.strftime("%d/%m/%Y %H:%M")
    except Exception as e:
        print(f"Erro ao converter data: {e}")
        return "Data inválida"


if __name__ == '__main__':
    app.run(debug=True)
