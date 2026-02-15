import streamlit as st
from database import init_db

# Ensure DB is ready (tables + default admin)
init_db()

st.set_page_config(page_title="Batalha Olimpica", page_icon="🏅", layout="wide", initial_sidebar_state="collapsed")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Outfit:wght@300;400;600;700&display=swap');
    </style>
    <div style="text-align:center; padding:4rem 1rem;">
        <div style="font-family:'Bebas Neue',sans-serif; font-size:4.5rem; letter-spacing:4px; line-height:1;
                    background:linear-gradient(135deg,#f7971e,#ffd200); -webkit-background-clip:text;
                    -webkit-text-fill-color:transparent;">BATALHA OLIMPICA</div>
        <div style="font-family:'Outfit',sans-serif; color:#999; font-size:1.1rem; margin-top:0.5rem;
                    letter-spacing:2px; text-transform:uppercase;">Semana Olimpica 2026</div>
        <div style="margin-top:3rem; display:flex; justify-content:center; gap:2rem; flex-wrap:wrap;">
            <div style="background:linear-gradient(145deg,#1a1a2e,#16213e); border:1px solid #333;
                        border-radius:16px; padding:2rem 2.5rem; min-width:200px;">
                <div style="font-family:'Bebas Neue',sans-serif; font-size:1.8rem; color:#ffd200;
                            letter-spacing:2px;">LEADERBOARD</div>
                <div style="font-family:'Outfit',sans-serif; color:#888; font-size:0.85rem; margin-top:4px;">
                    Ranking em tempo real</div>
            </div>
            <div style="background:linear-gradient(145deg,#1a1a2e,#16213e); border:1px solid #333;
                        border-radius:16px; padding:2rem 2.5rem; min-width:200px;">
                <div style="font-family:'Bebas Neue',sans-serif; font-size:1.8rem; color:#ffd200;
                            letter-spacing:2px;">QUESTOES</div>
                <div style="font-family:'Outfit',sans-serif; color:#888; font-size:0.85rem; margin-top:4px;">
                    Desafios da regata ativa</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
