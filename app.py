import streamlit as st
from sqlalchemy import inspect, text
from database import engine, get_db, Base
from models import User
from auth import hash_password

# Create all tables
Base.metadata.create_all(bind=engine)

# Migrate: add enunciado column if missing (for existing databases)
inspector = inspect(engine)
columns = [c["name"] for c in inspector.get_columns("questoes")]
if "enunciado" not in columns:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE questoes ADD COLUMN enunciado TEXT DEFAULT ''"))
        conn.commit()

# Create default admin if not exists
db = get_db()
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
