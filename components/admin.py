import streamlit as st
from components.admin_okt import admin_okt
from components.admin_tilbakemeldinger import hent_antall_tilbakemeldinger, admin_tilbakemeldinger

def admin():
    if st.session_state["user"].email != "admin@infera.no":
        st.error("⛔ Du har ikke tilgang til denne siden.")
        st.stop()

    st.title("🛠️ Adminpanel")

    st.markdown("""
    Her kan du administrere innhold i VårForm – legg til økter og se tilbakemeldinger fra brukere.  
    Du har full tilgang som administrator.
    """)

    # Hent antall tilbakemeldinger
    antall = hent_antall_tilbakemeldinger()

    col1, col2 = st.columns(2)

    with col1:
        with st.expander("🧱 Øvelsesbank", expanded=False):
            admin_okt()

    with col2:
        with st.expander(f"💬 Tilbakemeldinger ({antall})", expanded=False):
            admin_tilbakemeldinger()
