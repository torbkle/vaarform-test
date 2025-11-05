import streamlit as st
from components.auth import supabase

def velg_partner():
    st.subheader("👯 Send partnerforespørsel")
    bruker_id = st.session_state["user"].id
    bruker_email = st.session_state["user"].email

    # === Søkefelt ===
    søk = st.text_input("Skriv inn partnerens e-postadresse")

    if "partner_søk_resultat" not in st.session_state:
        st.session_state["partner_søk_resultat"] = None

    if st.button("🔍 Finn partner") and søk:
        respons = supabase.table("brukere").select("id, email").eq("email", søk).execute()
        data = respons.data
        if data:
            st.session_state["partner_søk_resultat"] = data[0]
        else:
            st.session_state["partner_søk_resultat"] = "ingen"

    # === Vis søkeresultat ===
    if st.session_state["partner_søk_resultat"] == "ingen":
        st.warning("❌ Fant ingen bruker med den e-posten.")
    elif isinstance(st.session_state["partner_søk_resultat"], dict):
        partner = st.session_state["partner_søk_resultat"]
        partner_id = partner["id"]
        partner_email = partner["email"]

        # Hent navn og brukernavn fra brukerinfo
        partnerinfo_resp = supabase.table("brukerinfo").select("fornavn", "etternavn", "brukernavn")\
            .eq("bruker_id", partner_id).execute()

        if partnerinfo_resp.data:
            partnerinfo = partnerinfo_resp.data[0]
            fullt_navn = f"{partnerinfo.get('fornavn', '')} {partnerinfo.get('etternavn', '')}".strip()
            brukernavn = partnerinfo.get("brukernavn", "")
            visning = f"{fullt_navn} ({brukernavn})"
        else:
            visning = partner_email

        st.success(f"✅ Fant bruker: {visning}")
        if st.button("📨 Send forespørsel"):
            # Sjekk om forespørsel allerede finnes
            eksisterende = supabase.table("partner_requests").select("*")\
                .eq("from_user_id", bruker_id)\
                .eq("to_user_id", partner_id)\
                .eq("status", "venter").execute()

            if eksisterende.data:
                st.warning("Du har allerede sendt en forespørsel til denne brukeren.")
            else:
                insert_resp = supabase.table("partner_requests").insert({
                    "from_user_id": bruker_id,
                    "to_user_id": partner_id,
                    "status": "venter"
                }).execute()

                if not insert_resp.data:
                    st.error("Feil ved lagring av forespørsel. Ingen data ble returnert.")
                else:
                    st.success(f"Forespørsel sendt til {visning}. Partner må godkjenne i appen.")
                    st.session_state["partner_søk_resultat"] = None
                    st.rerun()
