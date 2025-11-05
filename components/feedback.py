import streamlit as st
from components.auth import supabase

def vis_tilbakemelding(user_id):
    st.subheader("🗣️ Tilbakemelding")

    st.markdown("""
    Har du forslag, ønsker eller noe som ikke fungerer?  
    Skriv det inn her – vi setter stor pris på alle innspill! 🙌
    """)

    melding = st.text_area("Din tilbakemelding", placeholder="F.eks. 'Jeg synes treningsgrafen burde vise ukesnivå'")

    if st.button("Send inn"):
        if melding.strip():
            respons = supabase.table("tilbakemelding").insert({
                "bruker_id": user_id,
                "melding": melding
            }).execute()
            if respons.status_code == 201:
                st.success("✅ Takk for tilbakemeldingen!")
            else:
                st.error("Noe gikk galt – prøv igjen senere.")
        else:
            st.warning("Skriv inn noe før du sender.")
