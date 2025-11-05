import streamlit as st
from components.auth import supabase

def vis_tilbakemelding(user_id):
    st.subheader("🗣️ Tilbakemelding")

    st.markdown("Skriv inn forslag, ønsker eller feil du har oppdaget – vi leser alt! 🙌")

    melding = st.text_area("Din tilbakemelding", placeholder="F.eks. 'Grafen burde vise ukesnivå'")

    if st.button("Send inn"):
        if melding.strip():
            respons = supabase.table("tilbakemelding").insert({
                "bruker_id": user_id,
                "melding": melding
            }).execute()
            if respons.data:
                st.success("✅ Takk for tilbakemeldingen!")
            else:
                st.error("Noe gikk galt – tilbakemeldingen ble ikke lagret.")
        else:
            st.warning("Skriv inn noe før du sender.")
