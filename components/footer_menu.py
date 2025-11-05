import streamlit as st
from components.auth import logout

def show_footer_menu():
    st.markdown("""
    <style>
    .footer-fixed {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #f9f9f9;
        border-top: 1px solid #ccc;
        padding: 0.5em 0.5em;
        z-index: 9999;
    }
    .footer-row {
        display: flex;
        justify-content: center;
        gap: 1rem;
        flex-wrap: wrap;
    }
    .footer-row button {
        background-color: #ffffff;
        border: 1px solid #ccc;
        border-radius: 6px;
        padding: 0.5em 1em;
        font-size: 1em;
        cursor: pointer;
    }
    .footer-row button:hover {
        background-color: #e0e0e0;
    }
    .logout-button {
        background-color: #ff4b4b !important;
        color: white !important;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 70px;'></div>", unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='footer-fixed'><div class='footer-row'>", unsafe_allow_html=True)

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            if st.button("🏠 Hjem"):
                st.session_state["vis_side"] = "hjem"
                st.rerun()
        with col2:
            if st.button("📋 Velg økt"):
                st.session_state["vis_side"] = "velg_okt"
                st.rerun()
        with col3:
            if st.button("⚙️ Innstillinger"):
                st.session_state["vis_side"] = "innstillinger"
                st.rerun()
        with col4:
            if st.session_state.get("user") and st.session_state["user"].email == "admin@infera.no":
                if st.button("🛠️ Adminpanel"):
                    st.session_state["vis_side"] = "admin"
                    st.rerun()
        with col5:
            if st.button("🚪 Logg ut", key="logout_knapp"):
                logout()
                st.session_state.clear()
                st.rerun()

        st.markdown("</div></div>", unsafe_allow_html=True)
