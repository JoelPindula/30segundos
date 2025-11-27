# Arquitetura do Sistema - 30 Segundos

## Visão Geral

O sistema é composto por três componentes principais:
┌─────────────────────────────────────────────────────────────┐
│                      SERVIDOR (Python)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   FastAPI   │  │  Socket.IO  │  │      SQLite         │  │
│  │  (HTTP API) │  │  (Realtime) │  │  (Banco de Dados)   │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
│
┌─────────┴─────────┐
│   Rede Wi-Fi      │
│     Local         │
└─────────┬─────────┘
│
┌─────────────────────┼─────────────────────┐
│                     │                     │
▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│    ADMIN      │    │    BOARD      │    │    PLAYER     │
│  (Navegador)  │    │  (TV/Projetor)│    │(Celular/Tablet│
│               │    │               │    │               │
│ - Criar jogo  │    │ - Tabuleiro   │    │ - Ver carta   │
│ - Config      │    │ - Timer       │    │ - Virar carta │
│ - Gerenciar   │    │ - Placar      │    │               │
└───────────────┘    └───────────────┘    └───────────────┘

## Estrutura de Camadas do Backend


backend/
├── core/           # Domínio (regras de negócio puras)
│   ├── models.py       # Entidades: Game, Team, Card, etc.
│   ├── game_engine.py  # Motor do jogo
│   ├── card_generator.py # Geração de cartas
│   └── exceptions.py   # Exceções de domínio
│
├── services/       # Aplicação (casos de uso)
│   ├── game_service.py    # Orquestra operações de jogo
│   ├── session_service.py # Gerencia sessões de jogador
│   └── deck_service.py    # Gerencia decks
│
└── api/            # Interface (comunicação externa)
├── http_routes.py     # Rotas REST
└── socket_handlers.py # Eventos Socket.IO

## Fluxo de Dados

### Criar Partida

Admin → POST /api/games → game_service.create_game() → Game criado

### Iniciar Rodada

Admin → Socket: admin_start_round
→ game_service.start_round()
→ Socket: round_started (→ Board)
→ Socket: card_assigned (→ Player)

### Virar Carta

Player → Socket: player_flip_card
→ game_service.flip_card() (valida token)
→ Socket: card_flipped (→ Player)
→ Socket: player_flipped_card (→ Board)

## Tecnologias

- **FastAPI**: Framework web assíncrono para Python
- **Socket.IO**: Comunicação em tempo real bidirecional
- **SQLite**: Banco de dados embutido (arquivo único)
- **Uvicorn**: Servidor ASGI para rodar a aplicação

## Requisitos para Execução

```bash
# Instalar dependências
pip install fastapi uvicorn python-socketio aiosqlite

# Executar
uvicorn backend.main:socket_app --host 0.0.0.0 --port 8000


---

### Arquivo: `docs/regras_jogo.md`

```markdown
# Regras do Jogo - 30 Segundos

## Objetivo

O objetivo é ser o primeiro time a chegar ao final do tabuleiro, 
acertando o máximo de palavras possível em cada rodada de 30 segundos.

## Componentes

### Tabuleiro
- Uma trilha de casas coloridas
- Primeira casa: NEUTRA (início)
- Demais casas: alternância entre AMARELA e AZUL
- Um peão que avança conforme os acertos

### Cartas
- Cada carta tem dois lados: AMARELO e AZUL
- Cada lado tem 5 palavras
- As palavras têm diferentes níveis de dificuldade

## Fluxo do Jogo

### Preparação
1. Criar partida no painel Admin
2. Selecionar temas e níveis
3. Abrir tela do Tabuleiro na TV
4. Jogador conecta pelo celular

### Rodada
1. **Determinação do Lado Inicial**
   - A cor da casa onde o peão está determina o lado inicial
   - Casa AMARELA → começa pelo lado AMARELO da carta
   - Casa AZUL → começa pelo lado AZUL da carta
   - Casa NEUTRA → começa pelo AMARELO (padrão)

2. **Leitura das Palavras (30 segundos)**
   - O jogador com o celular vê as 5 palavras
   - Deve dar dicas para sua equipe adivinhar
   - NÃO pode dizer a palavra nem derivações
   - NÃO pode usar gestos

3. **Virar a Carta**
   - O jogador pode virar a carta até 2 vezes
   - Primeira virada: sem penalidade
   - Segunda virada: penalidade de -2 pontos

4. **Fim da Rodada**
   - Quando o tempo acaba, o admin marca os acertos
   - Pontuação = número de acertos - penalidades

### Avanço no Tabuleiro
- Após cada rodada, o peão avança
- Regra padrão: 1 casa por rodada
- Regra alternativa: 1 casa por palavra acertada

## Pontuação

| Ação | Pontos |
|------|--------|
| Palavra acertada | +1 |
| Segunda virada da carta | -2 |

## Fim do Jogo

O jogo termina quando o peão de algum time chega ao final do tabuleiro.
O time com mais pontos vence. Em caso de empate, vence quem chegou primeiro.

## Dicas para Jogar Bem

1. Comece pelas palavras mais fáceis
2. Se não consegue dar dicas de uma palavra, passe para a próxima
3. Pense se vale a pena virar a carta (penalidade de -2!)
4. O time que adivinha deve prestar atenção nas dicas