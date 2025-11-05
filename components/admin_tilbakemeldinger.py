import streamlit as st
from components.auth import supabase

def hent_antall_tilbakemeldinger():
    respons = supabase.table("tilbakemelding").select("id").execute()
    return len(respons.data)

def admin_tilbakemeldinger():
    respons = supabase.table("tilbakemelding").select("*").order("opprettet", desc=True).execute()


    if not respons.data:
        st.info("Ingen tilbakemeldinger registrert ennå.")
        return

    for melding in respons.data:
        with st.expander(f"🗓️ {melding['opprettet']} – fra bruker `{melding['bruker_id']}`"):
            st.markdown(f"**Tema:** {melding.get('tema', 'Ukjent')}")
            st.markdown(f"**Melding:** {melding.get('melding', 'Ingen tekst')}")
