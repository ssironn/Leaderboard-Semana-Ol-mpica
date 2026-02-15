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
