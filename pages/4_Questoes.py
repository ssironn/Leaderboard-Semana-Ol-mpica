import time
import streamlit as st
from database import get_db
from models import Regata, Questao

st.set_page_config(page_title="Questoes - Batalha Olimpica", page_icon="📝", layout="wide", initial_sidebar_state="collapsed")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Outfit:wght@300;400;600;700&display=swap');
    </style>
    """,
    unsafe_allow_html=True,
)

db = get_db()

regata = db.query(Regata).filter_by(ativa=True).first()

if not regata:
    st.markdown(
        """
        <div style="text-align:center; padding:6rem 1rem;">
            <div style="font-family:'Bebas Neue',sans-serif; font-size:3rem; letter-spacing:3px;
                        background:linear-gradient(135deg,#f7971e,#ffd200); -webkit-background-clip:text;
                        -webkit-text-fill-color:transparent;">BATALHA OLIMPICA</div>
            <div style="font-family:'Outfit',sans-serif; color:#888; font-size:1.1rem; margin-top:1rem;">
                Nenhuma regata ativa no momento. Aguarde...</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    db.close()
    time.sleep(5)
    st.rerun()

# Header
st.markdown(
    f"""
    <div style="text-align:center; padding:1rem 0 2rem;">
        <div style="font-family:'Bebas Neue',sans-serif; font-size:2.5rem; letter-spacing:3px;
                    background:linear-gradient(135deg,#f7971e,#ffd200); -webkit-background-clip:text;
                    -webkit-text-fill-color:transparent;">QUESTOES</div>
        <div style="font-family:'Outfit',sans-serif; color:#888; font-size:1rem; margin-top:4px;">
            {regata.nome}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

questoes = db.query(Questao).filter_by(regata_id=regata.id).all()

if not questoes:
    st.info("Nenhuma questao cadastrada para esta regata.")
else:
    niveis_ordem = {"facil": 0, "medio": 1, "dificil": 2}
    niveis_label = {"facil": "FACIL", "medio": "MEDIO", "dificil": "DIFICIL"}
    niveis_cor_hex = {"facil": "#4caf50", "medio": "#ff9800", "dificil": "#f44336"}
    niveis_pontos = {"facil": "100", "medio": "100", "dificil": "100"}

    questoes_sorted = sorted(questoes, key=lambda q: niveis_ordem.get(q.nivel, 99))

    for q in questoes_sorted:
        label = niveis_label.get(q.nivel, q.nivel)
        cor = niveis_cor_hex.get(q.nivel, "#888")

        enunciado_html = ""
        if q.enunciado:
            enunciado_html = f"""<div style="font-family:'Outfit',sans-serif; color:#ccc; font-size:1.05rem;
                                            margin-left:4px;">{q.enunciado}</div>"""

        st.markdown(
            f"""
            <div style="display:flex; align-items:center; gap:12px; margin:1.5rem 0 0.4rem;">
                <div style="background:{cor}; color:#000; font-family:'Bebas Neue',sans-serif;
                            font-size:1.2rem; letter-spacing:2px; padding:4px 16px; border-radius:6px;">
                    {label}</div>
            </div>
            {enunciado_html}
            """,
            unsafe_allow_html=True,
        )
        st.image(q.imagem, use_container_width=True)

db.close()
