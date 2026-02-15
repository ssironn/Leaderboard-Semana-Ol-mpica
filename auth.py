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
