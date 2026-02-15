import time
import streamlit as st
from database import get_db
from models import Equipe
from scoring import calcular_leaderboard

st.set_page_config(page_title="Leaderboard - Batalha Olimpica", page_icon="🏆", layout="wide", initial_sidebar_state="collapsed")

# --- GLOBAL CSS ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Outfit:wght@300;400;600;700&display=swap');
    .stAppHeader { display: none; }
    section[data-testid="stMain"] > div { padding-top: 1rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

db = get_db()

# --- HEADER ---
st.markdown(
    """
    <div style="text-align:center; padding:1rem 0 2rem;">
        <div style="font-family:'Bebas Neue',sans-serif; font-size:3.5rem; letter-spacing:4px; line-height:1;
                    background:linear-gradient(135deg,#f7971e,#ffd200); -webkit-background-clip:text;
                    -webkit-text-fill-color:transparent;">BATALHA OLIMPICA</div>
        <div style="font-family:'Outfit',sans-serif; color:#666; font-size:0.9rem; letter-spacing:3px;
                    text-transform:uppercase; margin-top:4px;">Ranking Geral</div>
    </div>
    """,
    unsafe_allow_html=True,
)

ranking = calcular_leaderboard(db)

# Include teams with 0 points
equipes_no_ranking = {r["equipe"] for r in ranking}
todas_equipes = db.query(Equipe).all()
for e in todas_equipes:
    if e.nome not in equipes_no_ranking:
        ranking.append({"equipe": e.nome, "pontos": 0})

ranking.sort(key=lambda x: x["pontos"], reverse=True)

if not ranking:
    st.markdown(
        '<div style="text-align:center; color:#666; font-family:Outfit,sans-serif; padding:4rem;">Nenhuma equipe cadastrada.</div>',
        unsafe_allow_html=True,
    )
else:
    max_pontos = max(r["pontos"] for r in ranking) if ranking else 1
    if max_pontos == 0:
        max_pontos = 1

    # Color palette — vibrant, high contrast
    cores = [
        "#ffd200", "#00e5ff", "#ff3d00", "#76ff03",
        "#d500f9", "#ffab00", "#00e676", "#ff1744",
        "#2979ff", "#f50057", "#00bfa5", "#ff6d00",
        "#651fff", "#c6ff00", "#ff9100", "#00b8d4",
        "#dd2c00", "#aeea00", "#304ffe", "#64dd17",
    ]

    bars_html = ""
    for i, item in enumerate(ranking):
        cor = cores[i % len(cores)]
        pct = (item["pontos"] / max_pontos) * 100 if max_pontos > 0 else 0
        # Minimum bar width so text is visible
        bar_width = max(pct, 8) if item["pontos"] > 0 else 2
        posicao = i + 1

        # Top 3 get special treatment
        if posicao == 1:
            medal = "🥇"
            row_bg = "rgba(255,210,0,0.08)"
            name_size = "1.4rem"
            bar_height = "52px"
        elif posicao == 2:
            medal = "🥈"
            row_bg = "rgba(192,192,192,0.06)"
            name_size = "1.25rem"
            bar_height = "44px"
        elif posicao == 3:
            medal = "🥉"
            row_bg = "rgba(205,127,50,0.06)"
            name_size = "1.15rem"
            bar_height = "40px"
        else:
            medal = ""
            row_bg = "transparent"
            name_size = "1.05rem"
            bar_height = "36px"

        bars_html += f"""
        <div style="display:flex; align-items:center; margin-bottom:6px; padding:6px 12px;
                    background:{row_bg}; border-radius:10px;">
            <div style="width:50px; font-family:'Bebas Neue',sans-serif; font-size:1.6rem; color:#888;
                        text-align:center;">{posicao}</div>
            <div style="width:180px; font-family:'Outfit',sans-serif; font-weight:700; font-size:{name_size};
                        color:#eee; padding-right:12px; white-space:nowrap; overflow:hidden;
                        text-overflow:ellipsis;">{medal} {item['equipe']}</div>
            <div style="flex:1; background:rgba(255,255,255,0.06); border-radius:8px; overflow:hidden;
                        height:{bar_height};">
                <div style="width:{bar_width}%; background:linear-gradient(90deg,{cor},{cor}dd);
                            height:100%; border-radius:8px; display:flex; align-items:center;
                            justify-content:flex-end; padding-right:14px; font-family:'Bebas Neue',sans-serif;
                            font-size:1.3rem; color:#000; letter-spacing:1px;
                            transition:width 0.6s cubic-bezier(0.4,0,0.2,1);">
                    {item['pontos']}
                </div>
            </div>
        </div>
        """

    st.markdown(bars_html, unsafe_allow_html=True)

db.close()

# Auto-refresh
time.sleep(4)
st.rerun()
