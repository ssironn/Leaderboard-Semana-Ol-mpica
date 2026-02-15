# Batalha Olimpica — Design Document

## Overview

Sistema de competicao em tempo real para a "Semana Olimpica". Equipes resolvem problemas em baterias (regatas) de 15-20 minutos. Juizes validam respostas e registram no sistema. Um leaderboard no telao atualiza em tempo real.

## Stack

- **Streamlit** — unico servico, multi-page
- **SQLAlchemy** — ORM
- **SQLite** — banco de dados em arquivo (`data.db`)
- **bcrypt** — hash de senhas

## Arquitetura

```
Streamlit (porta 8501)
  ├── Admin (login)
  ├── Juiz (login)
  ├── Leaderboard (publico)
  └── Questoes (publico)
        │
   SQLAlchemy ORM
        │
   SQLite (data.db)
```

Um unico processo. Sem API separada. Sem Docker.

## Modelo de Dados

### users
| Coluna | Tipo | Notas |
|---|---|---|
| id | Integer PK | Auto-increment |
| username | String(50) | Unique |
| password_hash | String(128) | bcrypt |
| role | String(10) | "admin" ou "juiz" |
| created_at | DateTime | UTC |

### equipes
| Coluna | Tipo | Notas |
|---|---|---|
| id | Integer PK | Auto-increment |
| nome | String(100) | Unique |
| created_at | DateTime | UTC |

### regatas
| Coluna | Tipo | Notas |
|---|---|---|
| id | Integer PK | Auto-increment |
| nome | String(100) | |
| ativa | Boolean | Default false. So uma ativa por vez |
| created_at | DateTime | UTC |

### questoes
| Coluna | Tipo | Notas |
|---|---|---|
| id | Integer PK | Auto-increment |
| regata_id | Integer FK | -> regatas.id |
| nivel | String(10) | "facil", "medio", "dificil" |
| imagem | LargeBinary | BLOB com a imagem |
| imagem_filename | String(255) | Nome original do arquivo |
| created_at | DateTime | UTC |

### tentativas
| Coluna | Tipo | Notas |
|---|---|---|
| id | Integer PK | Auto-increment |
| equipe_id | Integer FK | -> equipes.id |
| questao_id | Integer FK | -> questoes.id |
| numero | Integer | 1, 2 ou 3 (calculado automaticamente) |
| acertou | Boolean | |
| pontos | Integer | 100, 80, 50 ou 0 (calculado automaticamente) |
| juiz_id | Integer FK | -> users.id |
| created_at | DateTime | UTC |

## Regras de Pontuacao

- Maximo 3 tentativas por equipe por questao
- Acerto na 1a tentativa: 100 pontos
- Acerto na 2a tentativa: 80 pontos
- Acerto na 3a tentativa: 50 pontos
- Erro na 3a ou desistencia: 0 pontos
- Apos acerto, nao permite mais tentativas naquela questao
- O juiz so informa: equipe + questao + certo/errado
- O sistema calcula tentativa e pontos automaticamente

## Ambientes

### Admin
- Login com admin/admin (criado na 1a execucao, senha trocavel)
- CRUD de juizes (username/senha)
- CRUD de equipes
- CRUD de regatas (criar, ativar/desativar — so 1 ativa por vez)
- CRUD de questoes por regata (upload imagem + nivel)

### Juiz
- Login com credenciais cadastradas pelo admin
- Ve a regata ativa com suas questoes
- Seleciona equipe + questao
- Clica "Acertou" ou "Errou"
- Sistema mostra feedback: tentativa numero X, pontos ganhos
- Sistema bloqueia se equipe ja acertou ou esgotou tentativas

### Leaderboard (publico, sem login)
- Mostra ranking da regata ativa
- Barras horizontais proporcionais a pontuacao
- Ordenado por pontuacao (maior primeiro)
- Auto-refresh a cada 3-5 segundos via polling

### Questoes (publico, sem login)
- Mostra as 3 imagens da regata ativa (facil, medio, dificil)
- Sem login

## Estrutura de Arquivos

```
leaderboard-semana-olimpica/
├── app.py                     # Entrypoint, cria banco e admin padrao
├── database.py                # Engine, SessionLocal, Base
├── models.py                  # Modelos ORM
├── auth.py                    # Hash, verificacao, controle de sessao
├── pages/
│   ├── 1_Admin.py             # Painel admin
│   ├── 2_Juiz.py              # Painel do juiz
│   ├── 3_Leaderboard.py       # Ranking publico
│   └── 4_Questoes.py          # Questoes da regata ativa
├── requirements.txt           # streamlit, sqlalchemy, bcrypt
└── data.db                    # Criado automaticamente
```

## Deploy

Rodar direto na maquina:
```bash
pip install -r requirements.txt
streamlit run app.py
```
