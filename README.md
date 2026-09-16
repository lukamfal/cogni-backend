# CogniMente — Backend

API FastAPI para o app de treinamento cognitivo para idosos.

## Requisitos
- Python 3.12+
- PostgreSQL 16+
- Redis 7+

## Configuração rápida

```bash
# 1. Clone e entre na pasta
cd cogni-backend

# 2. Crie o .env a partir do exemplo
cp .env.example .env
# edite o .env com suas credenciais

# 3. Instale dependências
pip install -r requirements.txt

# 4. Suba o banco e redis com Docker
docker compose up db redis -d

# 5. Crie as tabelas
make shell

# 6. Rode o servidor
make dev
```

A documentação interativa estará em: http://localhost:8000/docs

## Rotas principais

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | /api/auth/register | Cadastro de usuário |
| POST | /api/auth/login | Login, retorna token JWT |
| GET | /api/profiles/me | Perfil do usuário logado |
| POST | /api/games/memory/start | Inicia jogo da memória |
| POST | /api/games/memory/finish/{id} | Finaliza e salva pontuação |
| POST | /api/games/math/start | Inicia jogo de matemática |
| POST | /api/games/face/start | Inicia jogo de familiares |
| POST | /api/games/word/start | Inicia jogo de palavras |
| GET | /api/games/suggest-difficulty/{type} | Sugere nível baseado no histórico |
| GET | /api/family/ | Lista familiares cadastrados |
| POST | /api/family/ | Adiciona familiar com foto |
| GET | /api/scores/history | Histórico de sessões |
| GET | /api/scores/best | Melhores pontuações |
| GET | /api/scores/summary | Resumo geral (streak, pontos) |

## Estrutura de dificuldade adaptativa

O endpoint `/api/games/suggest-difficulty/{game_type}` analisa as últimas
5 sessões do jogador e sugere automaticamente o nível ideal:
- Acurácia > 85% → sobe o nível
- Acurácia < 50% → desce o nível
- Entre 50-85% → mantém o nível atual

## Docker completo

```bash
make docker-up   # sobe tudo (api + db + redis)
make docker-down # derruba
```
