# Batalha Olimpica Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a real-time competition leaderboard system for "Semana Olimpica" where judges register team attempts and a public leaderboard updates via polling.

**Architecture:** Single Streamlit multi-page app with SQLAlchemy ORM and SQLite database. Admin manages judges/teams/regatas/questions, judges register correct/incorrect attempts, public pages show leaderboard and questions.

**Tech Stack:** Python, Streamlit, SQLAlchemy, SQLite, bcrypt

---

### Task 1: Project Setup and Dependencies

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`

**Step 1: Create requirements.txt**

```
streamlit>=1.30.0
sqlalchemy>=2.0.0
bcrypt>=4.0.0
```

**Step 2: Create .gitignore**

```
__pycache__/
*.pyc
data.db
.streamlit/
*.egg-info/
venv/
.env
```

**Step 3: Install dependencies**

Run: `pip install -r requirements.txt`
Expected: All packages install successfully

**Step 4: Commit**

```bash
git add requirements.txt .gitignore
git commit -m "feat: add project dependencies and gitignore"
```

---

### Task 2: Database Engine and Base

**Files:**
- Create: `database.py`

**Step 1: Write database.py**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "sqlite:///data.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Step 2: Commit**

```bash
git add database.py
git commit -m "feat: add database engine and session setup"
```

---

### Task 3: ORM Models

**Files:**
- Create: `models.py`
- Test: `tests/test_models.py`

**Step 1: Write the failing test**

Create `tests/__init__.py` (empty) and `tests/test_models.py`:

```python
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from models import User, Equipe, Regata, Questao, Tentativa


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_create_user(db):
    user = User(username="juiz1", password_hash="hash123", role="juiz")
    db.add(user)
    db.commit()
    assert user.id is not None
    assert user.username == "juiz1"
    assert user.role == "juiz"


def test_create_equipe(db):
    equipe = Equipe(nome="Equipe Alfa")
    db.add(equipe)
    db.commit()
    assert equipe.id is not None
    assert equipe.nome == "Equipe Alfa"


def test_create_regata_with_questoes(db):
    regata = Regata(nome="Regata 1", ativa=False)
    db.add(regata)
    db.commit()

    questao = Questao(
        regata_id=regata.id,
        nivel="facil",
        imagem=b"fake_image_data",
        imagem_filename="q1.png",
    )
    db.add(questao)
    db.commit()
    assert questao.regata_id == regata.id
    assert questao.nivel == "facil"


def test_create_tentativa(db):
    equipe = Equipe(nome="Equipe Beta")
    regata = Regata(nome="Regata 1", ativa=True)
    user = User(username="juiz1", password_hash="hash", role="juiz")
    db.add_all([equipe, regata, user])
    db.commit()

    questao = Questao(
        regata_id=regata.id, nivel="medio", imagem=b"img", imagem_filename="q.png"
    )
    db.add(questao)
    db.commit()

    tentativa = Tentativa(
        equipe_id=equipe.id,
        questao_id=questao.id,
        numero=1,
        acertou=True,
        pontos=100,
        juiz_id=user.id,
    )
    db.add(tentativa)
    db.commit()
    assert tentativa.pontos == 100
    assert tentativa.numero == 1
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_models.py -v`
Expected: FAIL — models not defined

**Step 3: Write models.py**

```python
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    LargeBinary,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    role = Column(String(10), nullable=False)  # "admin" or "juiz"
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    tentativas = relationship("Tentativa", back_populates="juiz")


class Equipe(Base):
    __tablename__ = "equipes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    tentativas = relationship("Tentativa", back_populates="equipe")


class Regata(Base):
    __tablename__ = "regatas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    ativa = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    questoes = relationship("Questao", back_populates="regata", cascade="all, delete-orphan")


class Questao(Base):
    __tablename__ = "questoes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    regata_id = Column(Integer, ForeignKey("regatas.id"), nullable=False)
    nivel = Column(String(10), nullable=False)  # "facil", "medio", "dificil"
    imagem = Column(LargeBinary, nullable=False)
    imagem_filename = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    regata = relationship("Regata", back_populates="questoes")
    tentativas = relationship("Tentativa", back_populates="questao")


class Tentativa(Base):
    __tablename__ = "tentativas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    equipe_id = Column(Integer, ForeignKey("equipes.id"), nullable=False)
    questao_id = Column(Integer, ForeignKey("questoes.id"), nullable=False)
    numero = Column(Integer, nullable=False)  # 1, 2, or 3
    acertou = Column(Boolean, nullable=False)
    pontos = Column(Integer, nullable=False, default=0)
    juiz_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    equipe = relationship("Equipe", back_populates="tentativas")
    questao = relationship("Questao", back_populates="tentativas")
    juiz = relationship("User", back_populates="tentativas")
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_models.py -v`
Expected: All 4 tests PASS

**Step 5: Commit**

```bash
git add models.py tests/
git commit -m "feat: add ORM models for users, equipes, regatas, questoes, tentativas"
```

---

### Task 4: Auth Module

**Files:**
- Create: `auth.py`
- Test: `tests/test_auth.py`

**Step 1: Write the failing test**

```python
import pytest
from auth import hash_password, verify_password


def test_hash_and_verify_password():
    password = "senha123"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("errada", hashed) is False
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_auth.py -v`
Expected: FAIL — auth module not found

**Step 3: Write auth.py**

```python
import bcrypt
import streamlit as st


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def require_auth(allowed_roles: list[str]) -> dict | None:
    """Check if user is logged in with correct role. Returns user dict or None."""
    user = st.session_state.get("user")
    if user and user.get("role") in allowed_roles:
        return user
    return None


def login_form(db_session, User):
    """Display login form and authenticate user. Returns True if logged in."""
    if st.session_state.get("user"):
        return True

    st.subheader("Login")
    username = st.text_input("Usuario")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        user = db_session.query(User).filter_by(username=username).first()
        if user and verify_password(password, user.password_hash):
            st.session_state["user"] = {
                "id": user.id,
                "username": user.username,
                "role": user.role,
            }
            st.rerun()
        else:
            st.error("Usuario ou senha incorretos.")
    return False
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_auth.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add auth.py tests/test_auth.py
git commit -m "feat: add auth module with password hashing and login form"
```

---

### Task 5: Business Logic — Scoring and Attempt Registration

**Files:**
- Create: `scoring.py`
- Test: `tests/test_scoring.py`

**Step 1: Write the failing tests**

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from models import User, Equipe, Regata, Questao, Tentativa
from scoring import registrar_tentativa, calcular_leaderboard


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Seed data
    juiz = User(username="juiz1", password_hash="hash", role="juiz")
    equipe_a = Equipe(nome="Equipe A")
    equipe_b = Equipe(nome="Equipe B")
    regata = Regata(nome="Regata 1", ativa=True)
    session.add_all([juiz, equipe_a, equipe_b, regata])
    session.commit()

    questao = Questao(
        regata_id=regata.id, nivel="facil", imagem=b"img", imagem_filename="q.png"
    )
    session.add(questao)
    session.commit()

    yield session
    session.close()


def test_acerto_primeira_tentativa(db):
    equipe = db.query(Equipe).filter_by(nome="Equipe A").first()
    questao = db.query(Questao).first()
    juiz = db.query(User).first()

    result = registrar_tentativa(db, equipe.id, questao.id, True, juiz.id)
    assert result["numero"] == 1
    assert result["pontos"] == 100
    assert result["acertou"] is True


def test_acerto_segunda_tentativa(db):
    equipe = db.query(Equipe).filter_by(nome="Equipe A").first()
    questao = db.query(Questao).first()
    juiz = db.query(User).first()

    # 1st attempt: wrong
    registrar_tentativa(db, equipe.id, questao.id, False, juiz.id)
    # 2nd attempt: correct
    result = registrar_tentativa(db, equipe.id, questao.id, True, juiz.id)
    assert result["numero"] == 2
    assert result["pontos"] == 80


def test_acerto_terceira_tentativa(db):
    equipe = db.query(Equipe).filter_by(nome="Equipe A").first()
    questao = db.query(Questao).first()
    juiz = db.query(User).first()

    registrar_tentativa(db, equipe.id, questao.id, False, juiz.id)
    registrar_tentativa(db, equipe.id, questao.id, False, juiz.id)
    result = registrar_tentativa(db, equipe.id, questao.id, True, juiz.id)
    assert result["numero"] == 3
    assert result["pontos"] == 50


def test_bloqueia_apos_3_tentativas(db):
    equipe = db.query(Equipe).filter_by(nome="Equipe A").first()
    questao = db.query(Questao).first()
    juiz = db.query(User).first()

    registrar_tentativa(db, equipe.id, questao.id, False, juiz.id)
    registrar_tentativa(db, equipe.id, questao.id, False, juiz.id)
    registrar_tentativa(db, equipe.id, questao.id, False, juiz.id)

    result = registrar_tentativa(db, equipe.id, questao.id, True, juiz.id)
    assert result["erro"] == "Equipe ja esgotou as 3 tentativas nesta questao."


def test_bloqueia_apos_acerto(db):
    equipe = db.query(Equipe).filter_by(nome="Equipe A").first()
    questao = db.query(Questao).first()
    juiz = db.query(User).first()

    registrar_tentativa(db, equipe.id, questao.id, True, juiz.id)
    result = registrar_tentativa(db, equipe.id, questao.id, True, juiz.id)
    assert result["erro"] == "Equipe ja acertou esta questao."


def test_erro_terceira_tentativa_zero_pontos(db):
    equipe = db.query(Equipe).filter_by(nome="Equipe A").first()
    questao = db.query(Questao).first()
    juiz = db.query(User).first()

    registrar_tentativa(db, equipe.id, questao.id, False, juiz.id)
    registrar_tentativa(db, equipe.id, questao.id, False, juiz.id)
    result = registrar_tentativa(db, equipe.id, questao.id, False, juiz.id)
    assert result["numero"] == 3
    assert result["pontos"] == 0
    assert result["acertou"] is False


def test_calcular_leaderboard(db):
    equipe_a = db.query(Equipe).filter_by(nome="Equipe A").first()
    equipe_b = db.query(Equipe).filter_by(nome="Equipe B").first()
    questao = db.query(Questao).first()
    juiz = db.query(User).first()
    regata = db.query(Regata).first()

    # Equipe A: acerta de primeira (100 pts)
    registrar_tentativa(db, equipe_a.id, questao.id, True, juiz.id)
    # Equipe B: erra, depois acerta (80 pts)
    registrar_tentativa(db, equipe_b.id, questao.id, False, juiz.id)
    registrar_tentativa(db, equipe_b.id, questao.id, True, juiz.id)

    ranking = calcular_leaderboard(db, regata.id)
    assert len(ranking) == 2
    assert ranking[0]["equipe"] == "Equipe A"
    assert ranking[0]["pontos"] == 100
    assert ranking[1]["equipe"] == "Equipe B"
    assert ranking[1]["pontos"] == 80
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_scoring.py -v`
Expected: FAIL — scoring module not found

**Step 3: Write scoring.py**

```python
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Tentativa, Equipe, Questao

PONTOS_POR_TENTATIVA = {1: 100, 2: 80, 3: 50}


def registrar_tentativa(
    db: Session, equipe_id: int, questao_id: int, acertou: bool, juiz_id: int
) -> dict:
    """Register an attempt and calculate points automatically."""
    # Check previous attempts
    tentativas_anteriores = (
        db.query(Tentativa)
        .filter_by(equipe_id=equipe_id, questao_id=questao_id)
        .order_by(Tentativa.numero)
        .all()
    )

    # Check if already correct
    for t in tentativas_anteriores:
        if t.acertou:
            return {"erro": "Equipe ja acertou esta questao."}

    # Check if max attempts reached
    if len(tentativas_anteriores) >= 3:
        return {"erro": "Equipe ja esgotou as 3 tentativas nesta questao."}

    numero = len(tentativas_anteriores) + 1

    if acertou:
        pontos = PONTOS_POR_TENTATIVA.get(numero, 0)
    else:
        pontos = 0

    tentativa = Tentativa(
        equipe_id=equipe_id,
        questao_id=questao_id,
        numero=numero,
        acertou=acertou,
        pontos=pontos,
        juiz_id=juiz_id,
    )
    db.add(tentativa)
    db.commit()

    return {
        "numero": numero,
        "acertou": acertou,
        "pontos": pontos,
    }


def calcular_leaderboard(db: Session, regata_id: int) -> list[dict]:
    """Calculate leaderboard for a regata, sorted by total points descending."""
    results = (
        db.query(Equipe.nome, func.coalesce(func.sum(Tentativa.pontos), 0).label("pontos"))
        .outerjoin(Tentativa, Tentativa.equipe_id == Equipe.id)
        .outerjoin(Questao, Tentativa.questao_id == Questao.id)
        .filter(Questao.regata_id == regata_id)
        .group_by(Equipe.id)
        .order_by(func.sum(Tentativa.pontos).desc())
        .all()
    )

    return [{"equipe": nome, "pontos": pontos} for nome, pontos in results]
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_scoring.py -v`
Expected: All 7 tests PASS

**Step 5: Commit**

```bash
git add scoring.py tests/test_scoring.py
git commit -m "feat: add scoring logic with attempt registration and leaderboard calculation"
```

---

### Task 6: App Entrypoint with DB Initialization

**Files:**
- Create: `app.py`

**Step 1: Write app.py**

```python
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

st.set_page_config(page_title="Batalha Olimpica", page_icon="🏅", layout="wide")

st.title("Batalha Olimpica")
st.markdown("Selecione uma pagina no menu lateral.")
st.markdown("""
- **Admin** — Gerenciar juizes, equipes, regatas e questoes
- **Juiz** — Registrar tentativas das equipes
- **Leaderboard** — Ranking em tempo real
- **Questoes** — Questoes da regata ativa
""")
```

**Step 2: Verify it runs**

Run: `streamlit run app.py --server.headless true` (then Ctrl+C)
Expected: App starts, creates data.db, creates admin user

**Step 3: Commit**

```bash
git add app.py
git commit -m "feat: add app entrypoint with DB init and default admin user"
```

---

### Task 7: Admin Page

**Files:**
- Create: `pages/1_Admin.py`

**Step 1: Write pages/1_Admin.py**

```python
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
```

**Step 2: Verify it runs**

Run: `streamlit run app.py --server.headless true` — navigate to Admin, login admin/admin
Expected: All 4 tabs functional

**Step 3: Commit**

```bash
mkdir -p pages
git add pages/1_Admin.py
git commit -m "feat: add admin page with CRUD for judges, teams, regatas, questions"
```

---

### Task 8: Judge Page

**Files:**
- Create: `pages/2_Juiz.py`

**Step 1: Write pages/2_Juiz.py**

```python
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
```

**Step 2: Verify it runs**

Run: Create a judge in admin, login as judge, test attempt registration
Expected: Correct/incorrect attempts work, points calculated, blocks after 3 attempts or after correct

**Step 3: Commit**

```bash
git add pages/2_Juiz.py
git commit -m "feat: add judge page with attempt registration"
```

---

### Task 9: Leaderboard Page

**Files:**
- Create: `pages/3_Leaderboard.py`

**Step 1: Write pages/3_Leaderboard.py**

```python
import time
import streamlit as st
from database import SessionLocal
from models import Regata, Equipe
from scoring import calcular_leaderboard

st.set_page_config(page_title="Leaderboard - Batalha Olimpica", page_icon="🏆", layout="wide")

db = SessionLocal()

regata = db.query(Regata).filter_by(ativa=True).first()

if not regata:
    st.title("Batalha Olimpica")
    st.info("Nenhuma regata ativa no momento. Aguarde...")
    db.close()
    time.sleep(5)
    st.rerun()

st.title(f"🏆 {regata.nome}")

ranking = calcular_leaderboard(db, regata.id)

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
```

**Step 2: Verify it runs**

Run: Activate a regata, add teams, register some attempts, check leaderboard updates
Expected: Horizontal bars showing ranking, auto-refreshes every 4 seconds

**Step 3: Commit**

```bash
git add pages/3_Leaderboard.py
git commit -m "feat: add public leaderboard with horizontal bars and auto-refresh"
```

---

### Task 10: Questions Page

**Files:**
- Create: `pages/4_Questoes.py`

**Step 1: Write pages/4_Questoes.py**

```python
import time
import streamlit as st
from database import SessionLocal
from models import Regata, Questao

st.set_page_config(page_title="Questoes - Batalha Olimpica", page_icon="📝", layout="wide")

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
```

**Step 2: Verify it runs**

Run: Add questions with images to the active regata, check the questions page
Expected: Images displayed in columns grouped by difficulty

**Step 3: Commit**

```bash
git add pages/4_Questoes.py
git commit -m "feat: add public questions page showing regata images by difficulty"
```

---

### Task 11: Final Integration Test and Polish

**Step 1: Run all tests**

Run: `python -m pytest tests/ -v`
Expected: All tests PASS

**Step 2: Manual end-to-end test**

1. `streamlit run app.py`
2. Login as admin/admin
3. Create 2 judges, 3 teams, 1 regata with 3 questions (one per level), activate regata
4. Open Juiz page in new tab, login as judge
5. Register some attempts (correct/incorrect)
6. Open Leaderboard in new tab — verify bars update
7. Open Questoes in new tab — verify images show

**Step 3: Final commit**

```bash
git add -A
git commit -m "feat: complete Batalha Olimpica system"
```
