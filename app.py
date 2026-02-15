import streamlit as st
from database import engine, SessionLocal, Base
from models import User
from auth import hash_password

# Create all tables
Base.metadata.create_all(bind=engine)

# Create default admin if not exists
db = SessionLocal()
try:
    admin = db.query(User).filter_by(username="admin").first()
    if not admin:
        admin = User(
            username="admin",
            password_hash=hash_password("admin"),
            role="admin",
        )
        db.add(admin)
        db.commit()
finally:
    db.close()

st.set_page_config(page_title="Batalha Olimpica", page_icon="🏅", layout="wide", initial_sidebar_state="collapsed")

st.title("Batalha Olimpica")
st.markdown("Selecione uma pagina no menu lateral.")
st.markdown("""
- **Admin** — Gerenciar juizes, equipes, regatas e questoes
- **Juiz** — Registrar tentativas das equipes
- **Leaderboard** — Ranking em tempo real
- **Questoes** — Questoes da regata ativa
""")
