import streamlit as st
from database import SessionLocal
from models import User, Equipe, Regata, Questao, Tentativa
from auth import login_form, require_auth
from scoring import registrar_tentativa

st.set_page_config(page_title="Juiz - Batalha Olimpica", page_icon="⚖️", layout="wide")

db = SessionLocal()

if not login_form(db, User):
    st.stop()

user = require_auth(["juiz", "admin"])
if not user:
    st.error("Acesso restrito a juizes.")
    st.stop()

st.title(f"Painel do Juiz — {user['username']}")

if st.sidebar.button("Sair"):
    del st.session_state["user"]
    st.rerun()

# Find active regata
regata = db.query(Regata).filter_by(ativa=True).first()

if not regata:
    st.warning("Nenhuma regata ativa no momento.")
    db.close()
    st.stop()

st.subheader(f"Regata: {regata.nome}")

equipes = db.query(Equipe).order_by(Equipe.nome).all()
questoes = db.query(Questao).filter_by(regata_id=regata.id).all()

if not equipes:
    st.warning("Nenhuma equipe cadastrada.")
    db.close()
    st.stop()

if not questoes:
    st.warning("Nenhuma questao nesta regata.")
    db.close()
    st.stop()

equipe_selecionada = st.selectbox(
    "Equipe", equipes, format_func=lambda e: e.nome
)

questao_selecionada = st.selectbox(
    "Questao",
    questoes,
    format_func=lambda q: f"{q.nivel.upper()} — {q.imagem_filename}",
)

# Show current attempt status for this team+question
tentativas_anteriores = (
    db.query(Tentativa)
    .filter_by(equipe_id=equipe_selecionada.id, questao_id=questao_selecionada.id)
    .order_by(Tentativa.numero)
    .all()
)

ja_acertou = any(t.acertou for t in tentativas_anteriores)
num_tentativas = len(tentativas_anteriores)

if ja_acertou:
    st.success(f"Equipe ja acertou esta questao! (Tentativa {next(t.numero for t in tentativas_anteriores if t.acertou)} — {next(t.pontos for t in tentativas_anteriores if t.acertou)} pontos)")
elif num_tentativas >= 3:
    st.error("Equipe ja esgotou as 3 tentativas nesta questao.")
else:
    st.info(f"Tentativas usadas: {num_tentativas}/3 — Proxima: {num_tentativas + 1}a tentativa")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ ACERTOU", use_container_width=True, type="primary"):
            result = registrar_tentativa(
                db, equipe_selecionada.id, questao_selecionada.id, True, user["id"]
            )
            if "erro" in result:
                st.error(result["erro"])
            else:
                st.success(
                    f"**{equipe_selecionada.nome}** — {questao_selecionada.nivel.upper()} — "
                    f"{result['numero']}a tentativa — **+{result['pontos']} pontos!**"
                )
                st.balloons()

    with col2:
        if st.button("❌ ERROU", use_container_width=True):
            result = registrar_tentativa(
                db, equipe_selecionada.id, questao_selecionada.id, False, user["id"]
            )
            if "erro" in result:
                st.error(result["erro"])
            else:
                restantes = 3 - result["numero"]
                st.warning(
                    f"**{equipe_selecionada.nome}** — {questao_selecionada.nivel.upper()} — "
                    f"Errou tentativa {result['numero']}. Restam {restantes} tentativa(s)."
                )

db.close()
