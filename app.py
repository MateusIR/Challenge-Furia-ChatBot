from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
import pytz
import random

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
    elif '5' in user_message or 'ultimos jogos' in user_message:
        reply = get_last_furia_wins()
    elif '6' in user_message or 'redes sociais' in user_message:
        reply = furia_social()
    elif '7' in user_message or 'roupa' in user_message:
        reply = furia_roupas()
    else:
        reply = 'Fala FURIOSO(A)!\n O que quer saber hoje?\n\n' \
        '1 - nossa história\n' \
        '2 - jogadores\n' \
        '3 - proximo jogo\n' \
        '4 - ultimos jogos\n' \
        '5 - ultimas vitórias\n' \
        '6 - nossas redes sociais\n' \
        '7 - nossas roupas\n' \

        
        

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
            'filter[opponent_id]': 124530,  # ID da FURIA no CSGO
            'per_page': 5
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

            status = match.get('status', 'desconhecido')
            league = match.get('league', {}).get('name', 'desconhecida')
            serie = match.get('serie', {}).get('full_name', '')

            if (placar[0]['score'] > placar[1]['score']):
                vitoria = "✅ VITÓRIA DA FURIA!"
            else:
              vitoria = "❌ Derrota. NT"  
                


            resposta += (
                f"\n🏆 Torneio: {match['tournament']['name']} ({league} - {serie})\n"
                f"🗓️ Data: {data_brasilia}\n"
                f"⚔️ {' vs '.join(opponents)}\n"
                f"🔢 Placar: {score_str}\n"
                f"📌 Status: {status.capitalize()}\n"
                f"{vitoria}\n"
                f"{'-'*40}"
            )

        return resposta
    except Exception as e:
        print(f"Erro ao buscar partidas passadas: {e}")
        return "Erro ao buscar últimas partidas!"



def get_last_furia_wins():
    try:
        url = 'https://api.pandascore.co/csgo/matches/past'
        params = {
            'filter[opponent_id]': 124530,
            'per_page': 20  
        }
        headers = {
            "Authorization": f"Bearer {PANDASCORE_TOKEN}"
        }

        res = requests.get(url, headers=headers, params=params)
        matches = res.json()

        if not matches:
            return "Nenhuma partida encontrada."

        vitorias = []
        for match in matches:
            placar = match.get('results', [])
            if len(placar) == 2:
                team1 = placar[0]
                team2 = placar[1]
                if team1['team_id'] == 124530 and team1['score'] > team2['score']:
                    vitorias.append(match)
                elif team2['team_id'] == 124530 and team2['score'] > team1['score']:
                    vitorias.append(match)

            if len(vitorias) >= 3:
                break

        if not vitorias:
            return "A FURIA não venceu recentemente."

        resposta = "✅ Últimas 3 vitórias da FURIA (CSGO):\n"
        for match in vitorias:
            opponents = [o['opponent']['name'] for o in match.get('opponents', [])]
            placar = match.get('results', [])
            score_str = f"{placar[0]['score']} x {placar[1]['score']}" if len(placar) == 2 else "Placar indisponível"
            data_brasilia = converter_utc_para_brasilia(match.get('begin_at', ''))

            status = match.get('status', 'desconhecido')
            league = match.get('league', {}).get('name', 'desconhecida')
            serie = match.get('serie', {}).get('full_name', '')

            resposta += (
                f"\n🏆 Torneio: {match['tournament']['name']} ({league} - {serie})\n"
                f"🗓️ Data: {data_brasilia}\n"
                f"⚔️ {' vs '.join(opponents)}\n"
                f"🔢 Placar: {score_str}\n"
                f"📌 Status: {status.capitalize()}\n"
                f"{'-'*40}"
            )

        return resposta
    except Exception as e:
        print(f"Erro ao buscar vitórias: {e}")
        return "Erro ao buscar últimas vitórias!"




def furia_social():
    
    return """ Nossas Redes Sociais:\n
    Instagram: https://www.instagram.com/furiagg/\n
    YouTube: https://www.youtube.com/@FURIAggCS\n
    X: https://x.com/FURIA
        """

def furia_roupas():
     return """ Vista o estilo FURIA:\n
     https://www.furia.gg/collections

            """






def furia_historia():
    historia = """
    FURIA CS: A GARRA QUE CONQUISTOU O MUNDO! 🖤🔥\n
Pra você que tá chegando agora, a Furia nasceu em 2017 NO CS:GO, com a meta de botar o Brasil no topo! E não demorou pra gente mostrar nossa garra e estratégia nos servidores, conquistando vitórias e uma torcida INCRÍVEL!\n

O CS é nossa raiz, onde a pantera mostrou seus primeiros rugidos. A gente joga com união e raça, valores que nos trouxeram até aqui e nos motivam a buscar sempre mais!\n

E o futuro no CS? A Furia segue com sangue nos olhos, focada em disputar os maiores campeonatos e trazer mais orgulho pra nossa torcida! A pantera nunca se aquieta!\n

Se você ama CS, se prepare pra vibrar! O rugido da Furia continua ecoando! 🐾🔫🔥
    """
    extra = """ 
CHEGOU AGORA? VEM COM A FURIA! 🖤🔥\n
Nascemos em 2017 no CS, viramos potência rapidinho e ganhamos vocês, a melhor torcida! De Minas pro mundo, expandimos pro LoL, Valorant, R6... mostrando nossa garra em tudo!\n

Pra gente, união, estratégia e raça são TUDO! A pantera no peito é nossa força pra inovar e impactar.\n

E o futuro? PRETO E AMARELO! Em 2025, futebol 7 com Neymar e Porsche Cup! No LoL, rumo à LTA Sul! A Furia não para!\n

É isso, Furioso(a)! Segura na garra e vambora! 🐾🚀
        """
    numero_sorteado = random.randint(1, 10)
    if numero_sorteado == 4 or numero_sorteado == 8:
        return extra
    else:
       return historia


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
