import streamlit as st
from components.auth import supabase

def vis_aktiv_partner():
    st.subheader("👥 Din aktive partner")
    bruker_id = st.session_state["user"].id

    # Søk etter aktiv kobling der bruker er A eller B
    respons = supabase.table("partners").select("id, user_a_id, user_b_id")\
        .or_(f"user_a_id.eq.{bruker_id},user_b_id.eq.{bruker_id}")\
        .eq("status", "aktiv").execute()

    if not respons.data:
        st.info("Du har ingen aktiv partner.")
        return

    kobling = respons.data[0]
    partner_id = kobling["user_b_id"] if kobling["user_a_id"] == bruker_id else kobling["user_a_id"]

    # Hent partnerens navn og brukernavn
    partnerinfo = supabase.table("brukerinfo").select("fornavn", "etternavn", "brukernavn")\
        .eq("bruker_id", partner_id).execute()

    if partnerinfo.data:
        p = partnerinfo.data[0]
        fullt_navn = f"{p.get('fornavn', '')} {p.get('etternavn', '')}".strip()
        brukernavn = p.get("brukernavn", "")
        visning = f"{fullt_navn} ({brukernavn})"
    else:
        # Fallback til e-post hvis navn mangler
        partner = supabase.table("brukere").select("email").eq("id", partner_id).execute()
        partner_email = partner.data[0]["email"] if partner.data else "Ukjent"
        visning = partner_email

    st.success(f"🎯 Du er koblet til: **{visning}**")

    if st.button("❌ Fjern partner"):
        # Sett status til "slettet"
        supabase.table("partners").update({"status": "slettet"}).eq("id", kobling["id"]).execute()
        st.warning("Partnerkobling er fjernet.")
        st.rerun()
