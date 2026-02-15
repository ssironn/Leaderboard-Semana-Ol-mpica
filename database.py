import os
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


_initialized = False


def init_db():
    """Create tables and default admin. Safe to call multiple times."""
    global _initialized
    if _initialized:
        return
    _initialized = True

    # Import here to avoid circular imports
    from models import User
    from auth import hash_password

    Base.metadata.create_all(bind=engine)

    # Migrate: add enunciado column if missing (for existing databases)
    inspector = inspect(engine)
    columns = [c["name"] for c in inspector.get_columns("questoes")]
    if "enunciado" not in columns:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE questoes ADD COLUMN enunciado TEXT DEFAULT ''"))
            conn.commit()

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


def get_db():
    """Create a fresh session. Ensures DB is initialized first."""
    init_db()
    db = SessionLocal()
    return db
