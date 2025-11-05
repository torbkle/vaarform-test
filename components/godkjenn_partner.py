import streamlit as st
from components.auth import supabase

def godkjenn_partner():
    st.subheader("👯 Partnerforespørsler")
    bruker_id = st.session_state["user"].id

    # Hent forespørsler som er sendt til denne brukeren
    respons = supabase.table("partner_requests").select("id, from_user_id, status")\
        .eq("to_user_id", bruker_id).eq("status", "venter").execute()

    forespørsler = respons.data

    if not forespørsler:
        st.info("Du har ingen partnerforespørsler.")
        return

    for f in forespørsler:
        fra_id = f["from_user_id"]
        forespørsel_id = f["id"]

        # Hent navn og brukernavn til den som sendte forespørselen
        info = supabase.table("brukerinfo").select("fornavn", "etternavn", "brukernavn")\
            .eq("bruker_id", fra_id).execute().data

        if info:
            navn = f"{info[0].get('fornavn', '')} {info[0].get('etternavn', '')}".strip()
            brukernavn = info[0].get("brukernavn", "")
            visning = f"{navn} ({brukernavn})"
        else:
            visning = "Ukjent bruker"

        st.markdown(f"📨 Forespørsel fra **{visning}**")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Godkjenn", key=f"godkjenn_{forespørsel_id}"):
                # Opprett kobling i partners-tabellen
                supabase.table("partners").insert({
                    "user_a_id": fra_id,
                    "user_b_id": bruker_id,
                    "status": "aktiv"
                }).execute()

                # Oppdater partner_id i brukerinfo for begge brukere
                supabase.table("brukerinfo").update({"partner_id": fra_id}).eq("bruker_id", bruker_id).execute()
                supabase.table("brukerinfo").update({"partner_id": bruker_id}).eq("bruker_id", fra_id).execute()

                # Oppdater forespørsel til godkjent
                supabase.table("partner_requests").update({"status": "godkjent"}).eq("id", forespørsel_id).execute()

                st.success(f"Du er nå koblet til {visning} som partner!")
                st.rerun()

        with col2:
            if st.button("❌ Avslå", key=f"avslå_{forespørsel_id}"):
                supabase.table("partner_requests").update({"status": "avslått"}).eq("id", forespørsel_id).execute()
                st.warning("Forespørsel avslått.")
                st.rerun()
