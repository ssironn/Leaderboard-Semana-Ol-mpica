import time
import streamlit as st
from database import SessionLocal
from models import Regata, Questao

st.set_page_config(page_title="Questoes - Batalha Olimpica", page_icon="📝", layout="wide", initial_sidebar_state="collapsed")

db = SessionLocal()

regata = db.query(Regata).filter_by(ativa=True).first()

if not regata:
    st.title("Batalha Olimpica — Questoes")
    st.info("Nenhuma regata ativa no momento. Aguarde...")
    db.close()
    time.sleep(5)
    st.rerun()

st.title(f"Questoes — {regata.nome}")

questoes = db.query(Questao).filter_by(regata_id=regata.id).all()

if not questoes:
    st.info("Nenhuma questao cadastrada para esta regata.")
else:
    # Group by level
    niveis_ordem = {"facil": 0, "medio": 1, "dificil": 2}
    niveis_label = {"facil": "FACIL", "medio": "MEDIO", "dificil": "DIFICIL"}
    niveis_cor = {"facil": "🟢", "medio": "🟡", "dificil": "🔴"}

    questoes_sorted = sorted(questoes, key=lambda q: niveis_ordem.get(q.nivel, 99))

    cols = st.columns(len(questoes_sorted))
    for i, q in enumerate(questoes_sorted):
        with cols[i]:
            st.markdown(f"### {niveis_cor.get(q.nivel, '')} {niveis_label.get(q.nivel, q.nivel)}")
            st.image(q.imagem, use_container_width=True)

db.close()
