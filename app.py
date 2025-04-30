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

        html = '<h3>👥 Integrantes da FURIA CS2:</h3><br>'
        for p in players:
            nome_completo = f"{p['first_name']} {p['last_name']}"
            nickname = f"{p['name']}"
            idade_nacionalidade = f"{p['age']} y   {p['nationality']}"
            foto = p.get('image_url') or "/static/img/furia_logo.png"
            html += f"""
                <div class="jogador">
                    <img src="{foto}" alt="Foto de {p['name']}" class="foto-jogador">
                    <div class="jogador-nomes">
                        <p style="width: 10rem;"><strong>{nickname}</strong><br>{nome_completo}</p><br>
                        <small>{idade_nacionalidade}</small>
                    </div>
                </div>
            """
        return html
    except Exception as e:
        print(e)
        return "Erro ao buscar jogadores!"



def get_next_furia_match():
    try:
        res = requests.get(
            'https://api.pandascore.co/csgo/matches/upcoming',
            headers={"Authorization": f"Bearer {PANDASCORE_TOKEN}"}
        )
        matches = res.json()

        for match in matches:
            if any(team['opponent']['name'].lower() == 'furia' for team in match.get('opponents', [])):
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





def get_furia_matches_from_api(per_page=5):
    """Shared function to get FURIA matches from PandaScore API"""
    url = 'https://api.pandascore.co/csgo/matches/past'
    params = {
        'filter[opponent_id]': 124530,  # ID da FURIA no CSGO
        'per_page': per_page
    }
    headers = {
        "Authorization": f"Bearer {PANDASCORE_TOKEN}"
    }
    res = requests.get(url, headers=headers, params=params)
    return res.json()

def format_match_response(match, include_victory_status=False):
    """Format a single match into a string response"""
    opponents = [o['opponent']['name'] for o in match.get('opponents', [])]
    placar = match.get('results', [])
    score_str = f"{placar[0]['score']} x {placar[1]['score']}" if len(placar) == 2 else "Placar indisponível"
    data_brasilia = converter_utc_para_brasilia(match.get('begin_at', ''))
    
    status = match.get('status', 'desconhecido')
    league = match.get('league', {}).get('name', 'desconhecida')
    serie = match.get('serie', {}).get('full_name', '')
    
    response = (
        f"\n🏆 Torneio: {match['tournament']['name']} ({league} - {serie})\n"
        f"🗓️ Data: {data_brasilia}\n"
        f"⚔️ {' vs '.join(opponents)}\n"
        f"🔢 Placar: {score_str}\n"
        f"📌 Status: {status.capitalize()}\n"
    )
    
    if include_victory_status and len(placar) == 2:
        if (placar[0]['team_id'] == 124530 and placar[0]['score'] > placar[1]['score']) or \
           (placar[1]['team_id'] == 124530 and placar[1]['score'] > placar[0]['score']):
            response += "✅ VITÓRIA DA FURIA!\n"
        else:
            response += "❌ Derrota. NT\n"
    
    response += f"{'-'*40}"
    return response

def get_last_furia_matches():
    try:
        matches = get_furia_matches_from_api(per_page=5)
        
        if not matches:
            return "Nenhuma partida recente encontrada."

        resposta = "🕹️ Últimos 5 jogos da FURIA (CSGO):\n"
        for match in matches:
            resposta += format_match_response(match, include_victory_status=True)

        return resposta
    except Exception as e:
        print(f"Erro ao buscar partidas passadas: {e}")
        return "Erro ao buscar últimas partidas!"

def get_last_furia_wins():
    try:
        matches = get_furia_matches_from_api(per_page=20)
        
        if not matches:
            return "Nenhuma partida encontrada."

        vitorias = []
        for match in matches:
            placar = match.get('results', [])
            if len(placar) == 2:
                team1 = placar[0]
                team2 = placar[1]
                if (team1['team_id'] == 124530 and team1['score'] > team2['score']) or \
                   (team2['team_id'] == 124530 and team2['score'] > team1['score']):
                    vitorias.append(match)

            if len(vitorias) >= 3:
                break

        if not vitorias:
            return "A FURIA não venceu recentemente."

        resposta = "✅ Últimas 3 vitórias da FURIA (CSGO):\n"
        for match in vitorias:
            resposta += format_match_response(match)

        return resposta
    except Exception as e:
        print(f"Erro ao buscar vitórias: {e}")
        return "Erro ao buscar últimas vitórias!"



def furia_social():
    return """🌐 Nossas Redes Sociais:<br>
    <div class="social-buttons">
    <h4>📷 Instagram:</h4>
        <a href="https://www.instagram.com/furiagg/" target="_blank" class="social-btn instagram">@Furiagg</a>
    <h4>🎥 YouTube:</h4>
        <a href="https://www.youtube.com/@FURIAggCS" target="_blank" class="social-btn youtube">@FURIAggCS</a>
    <h4>💬 X:</h4>
        <a href="https://x.com/FURIA" target="_blank" class="social-btn twitter">@FURIA</a>
    </div>
    """

def furia_roupas():
     return """ Vista o estilo FURIA:
    <div class="social-buttons">
    <h4>🔥Acesse nossa loja:</h4>
        <a href=" https://www.furia.gg/collections" target="_blank" class="social-btn loja">Furia.gg</a>
    </div>
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
