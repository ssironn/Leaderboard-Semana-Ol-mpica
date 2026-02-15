import streamlit as st
from database import SessionLocal
from models import User, Equipe, Regata, Questao
from auth import login_form, require_auth, hash_password

st.set_page_config(page_title="Admin - Batalha Olimpica", page_icon="⚙️", layout="wide")

db = SessionLocal()

if not login_form(db, User):
    st.stop()

user = require_auth(["admin"])
if not user:
    st.error("Acesso restrito a administradores.")
    st.stop()

st.title("Painel Administrativo")

if st.sidebar.button("Sair"):
    del st.session_state["user"]
    st.rerun()

tab_juizes, tab_equipes, tab_regatas, tab_questoes = st.tabs(
    ["Juizes", "Equipes", "Regatas", "Questoes"]
)

# --- JUIZES ---
with tab_juizes:
    st.subheader("Gerenciar Juizes")

    with st.form("novo_juiz"):
        st.write("Novo Juiz")
        username = st.text_input("Username")
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Criar Juiz")
        if submitted and username and password:
            existing = db.query(User).filter_by(username=username).first()
            if existing:
                st.error("Username ja existe.")
            else:
                juiz = User(
                    username=username,
                    password_hash=hash_password(password),
                    role="juiz",
                )
                db.add(juiz)
                db.commit()
                st.success(f"Juiz '{username}' criado.")
                st.rerun()

    juizes = db.query(User).filter_by(role="juiz").all()
    for j in juizes:
        col1, col2 = st.columns([3, 1])
        col1.write(f"**{j.username}**")
        if col2.button("Remover", key=f"del_juiz_{j.id}"):
            db.delete(j)
            db.commit()
            st.rerun()

# --- EQUIPES ---
with tab_equipes:
    st.subheader("Gerenciar Equipes")

    with st.form("nova_equipe"):
        st.write("Nova Equipe")
        nome = st.text_input("Nome da Equipe")
        submitted = st.form_submit_button("Criar Equipe")
        if submitted and nome:
            existing = db.query(Equipe).filter_by(nome=nome).first()
            if existing:
                st.error("Equipe ja existe.")
            else:
                equipe = Equipe(nome=nome)
                db.add(equipe)
                db.commit()
                st.success(f"Equipe '{nome}' criada.")
                st.rerun()

    equipes = db.query(Equipe).all()
    for e in equipes:
        col1, col2 = st.columns([3, 1])
        col1.write(f"**{e.nome}**")
        if col2.button("Remover", key=f"del_equipe_{e.id}"):
            db.delete(e)
            db.commit()
            st.rerun()

# --- REGATAS ---
with tab_regatas:
    st.subheader("Gerenciar Regatas")

    with st.form("nova_regata"):
        st.write("Nova Regata")
        nome = st.text_input("Nome da Regata")
        submitted = st.form_submit_button("Criar Regata")
        if submitted and nome:
            regata = Regata(nome=nome, ativa=False)
            db.add(regata)
            db.commit()
            st.success(f"Regata '{nome}' criada.")
            st.rerun()

    regatas = db.query(Regata).all()
    for r in regatas:
        col1, col2, col3 = st.columns([3, 1, 1])
        status = "🟢 ATIVA" if r.ativa else "⚪ Inativa"
        col1.write(f"**{r.nome}** — {status}")

        if not r.ativa:
            if col2.button("Ativar", key=f"ativar_{r.id}"):
                # Deactivate all others first
                for other in db.query(Regata).filter(Regata.id != r.id).all():
                    other.ativa = False
                r.ativa = True
                db.commit()
                st.rerun()
        else:
            if col2.button("Desativar", key=f"desativar_{r.id}"):
                r.ativa = False
                db.commit()
                st.rerun()

        if col3.button("Remover", key=f"del_regata_{r.id}"):
            db.delete(r)
            db.commit()
            st.rerun()

# --- QUESTOES ---
with tab_questoes:
    st.subheader("Gerenciar Questoes")

    regatas = db.query(Regata).all()
    if not regatas:
        st.info("Crie uma regata primeiro.")
    else:
        regata_selecionada = st.selectbox(
            "Selecionar Regata",
            regatas,
            format_func=lambda r: r.nome,
        )

        with st.form("nova_questao"):
            st.write(f"Nova Questao para '{regata_selecionada.nome}'")
            nivel = st.selectbox("Nivel", ["facil", "medio", "dificil"])
            imagem = st.file_uploader("Imagem da Questao", type=["png", "jpg", "jpeg"])
            submitted = st.form_submit_button("Adicionar Questao")
            if submitted and imagem:
                questao = Questao(
                    regata_id=regata_selecionada.id,
                    nivel=nivel,
                    imagem=imagem.read(),
                    imagem_filename=imagem.name,
                )
                db.add(questao)
                db.commit()
                st.success("Questao adicionada.")
                st.rerun()

        questoes = (
            db.query(Questao)
            .filter_by(regata_id=regata_selecionada.id)
            .all()
        )
        for q in questoes:
            col1, col2, col3 = st.columns([2, 2, 1])
            col1.write(f"**{q.nivel.upper()}** — {q.imagem_filename}")
            col2.image(q.imagem, width=200)
            if col3.button("Remover", key=f"del_questao_{q.id}"):
                db.delete(q)
                db.commit()
                st.rerun()

db.close()
