import time
import streamlit as st
from database import SessionLocal
from models import Equipe
from scoring import calcular_leaderboard

st.set_page_config(page_title="Leaderboard - Batalha Olimpica", page_icon="🏆", layout="wide", initial_sidebar_state="collapsed")

db = SessionLocal()

st.title("🏆 Batalha Olimpica")

ranking = calcular_leaderboard(db)

# Include teams with 0 points
equipes_no_ranking = {r["equipe"] for r in ranking}
todas_equipes = db.query(Equipe).all()
for e in todas_equipes:
    if e.nome not in equipes_no_ranking:
        ranking.append({"equipe": e.nome, "pontos": 0})

# Sort by points descending
ranking.sort(key=lambda x: x["pontos"], reverse=True)

if not ranking:
    st.info("Nenhuma equipe cadastrada.")
else:
    max_pontos = max(r["pontos"] for r in ranking) if ranking else 1
    if max_pontos == 0:
        max_pontos = 1

    # Colors for the bars
    cores = [
        "#FFD700", "#C0C0C0", "#CD7F32",
        "#4CAF50", "#2196F3", "#9C27B0",
        "#FF5722", "#00BCD4", "#E91E63",
        "#8BC34A", "#FF9800", "#607D8B",
        "#3F51B5", "#CDDC39", "#795548",
        "#009688", "#F44336", "#673AB7",
        "#FFC107", "#03A9F4",
    ]

    for i, item in enumerate(ranking):
        cor = cores[i % len(cores)]
        pct = (item["pontos"] / max_pontos) * 100 if max_pontos > 0 else 0

        posicao = i + 1
        st.markdown(
            f"""
            <div style="display:flex; align-items:center; margin-bottom:8px;">
                <div style="width:40px; font-size:1.4em; font-weight:bold; text-align:center;">{posicao}</div>
                <div style="width:150px; font-weight:bold; font-size:1.1em; padding-right:10px;">{item['equipe']}</div>
                <div style="flex:1; background:#222; border-radius:8px; overflow:hidden; height:36px;">
                    <div style="width:{pct}%; background:{cor}; height:100%; border-radius:8px;
                                display:flex; align-items:center; justify-content:flex-end; padding-right:10px;
                                font-weight:bold; color:#000; min-width:fit-content; transition: width 0.5s ease;">
                        {item['pontos']} pts
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

db.close()

# Auto-refresh every 4 seconds
time.sleep(4)
st.rerun()
