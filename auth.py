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

    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Outfit:wght@300;400;600;700&display=swap');
        </style>
        <div style="text-align:center; padding:2rem 0 1rem;">
            <div style="font-family:'Bebas Neue',sans-serif; font-size:3rem; letter-spacing:3px;
                        background:linear-gradient(135deg,#f7971e,#ffd200); -webkit-background-clip:text;
                        -webkit-text-fill-color:transparent;">BATALHA OLIMPICA</div>
            <div style="font-family:'Outfit',sans-serif; color:#888; font-size:0.95rem; margin-top:4px;">
                Acesso restrito</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        username = st.text_input("Usuario", placeholder="Digite seu usuario")
        password = st.text_input("Senha", type="password", placeholder="Digite sua senha")

        if st.button("Entrar", use_container_width=True, type="primary"):
            if not username or not password:
                st.error("Preencha usuario e senha.")
            else:
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
