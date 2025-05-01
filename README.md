
# 🐾 Challenge FURIA Chatbot - Flask App

Um chatbot interativo e responsivo para fãs da FURIA, integrado à [PandaScore API](https://developers.pandascore.co/), oferecendo informações sobre a equipe, próximos jogos, jogadores, últimas partidas, redes sociais e loja.

---

## 🚀 Funcionalidades

- 📜 História da FURIA
- 🎮 Lista atualizada de integrantes
- 📅 Próxima partida
- 📊 Últimas partidas
- ✅ Últimas vitórias
- 🌐 Links diretos para redes sociais
- 🛍️ Link para a loja oficial

- 📱 Layout responsivo para mobile
---

## 🛠️ Tecnologias Utilizadas

- Python 3.10+
- Flask
- HTML/CSS customizado
- API PandaScore (requer token)
- JavaScript (para comunicação assíncrona com a API)
---

## 📦 Instalação Manual

1. Clone o repositório:

```bash
git clone https://github.com/MateusIR/challenge-furia-chatbot.git
cd challenge-furia-chatbot
```

2. Crie um ambiente virtual e ative:

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Crie um arquivo `.env` na raiz do projeto com seu token da PandaScore:

```
PANDASCORE_TOKEN=seu_token_aqui
```
Pegue seu token em: https://app.pandascore.co/

5. Execute a aplicação:

```bash
python app.py
```

Acesse em [http://localhost:5000](http://localhost:5000)

---


3. Acesse via navegador: (https://challenge-furia-chatbot.onrender.com/)

---

## 🗃️ Estrutura de Arquivos

```
challenge-furia-chatbot/
│
├── app.py                # Lógica principal do chatbot Flask
├── .env                  # Token de API (não incluso)
├── static/
│   └── style.css         # Estilo visual
|   └── scripts.js       
├── templates/
│   └── index.html        # HTML principal
└── README.md             # Este arquivo
```

---

## 💬 Comandos disponíveis
```
| Entrada do usuário           | Resposta do bot                                     |
|------------------------------|-----------------------------------------------------|
| `1`, `história`              | História da FURIA (com mensagem aleatória)         |
| `2`, `jogadores`             | Lista dos integrantes da lineup CS2 atual          |
| `3`, `próximo jogo`          | Detalhes da próxima partida da FURIA               |
| `4`, `últimos jogos`         | Resumo dos últimos 5 jogos com placar              |
| `5`, `vitórias`              | Últimas 3 vitórias da FURIA                        |
| `6`, `redes sociais`         | Links para Instagram, YouTube e X (Twitter)        |
| `7`, `roupas`                | Link para a loja oficial da FURIA                  |

```

---
## 📜 Licença

Este projeto é de uso educacional e não oficial da organização FURIA.
