import streamlit as st
from components.auth import supabase
from datetime import date
import uuid

def velg_okt():
    st.subheader("📋 Velg treningsøkt og legg til i plan")

    # === Hent brukerens UUID direkte fra session_state
    bruker_id = st.session_state["user"].id

    # === Velg dato og kategori ===
    valgt_dato = st.date_input("Velg dato for økt:", value=date.today())
    kategori = st.selectbox("Velg kategori:", ["Løping", "Styrke", "Hvile"])
    underkategori = st.selectbox(
        "Velg underkategori:",
        ["Intervall", "Langløp", "Terrengløp"] if kategori == "Løping"
        else ["Fullkropp", "Overkropp", "Bein", "Kjerne"] if kategori == "Styrke"
        else ["Yoga", "Gå tur", "Mental pause"]
    )

    # === Hent økter fra øvelsesbank ===
    result = supabase.table("øvelsesbank").select("*").eq("kategori", kategori).eq("underkategori", underkategori).execute()
    økter = result.data

    if not økter:
        st.info("Ingen økter funnet for valgt kategori og underkategori.")
        return

    valg = st.radio("Velg økt:", [økt["navn"] for økt in økter])
    valgt = next(o for o in økter if o["navn"] == valg)

    st.markdown(f"**Beskrivelse:** {valgt.get('beskrivelse', 'Ingen')}")
    st.markdown(f"**Oppvarming:** {valgt.get('oppvarming', 'Ingen')}")
    st.markdown(f"**Nedjogging:** {valgt.get('nedjogging', 'Ingen')}")
    st.markdown(f"**Intensitet:** {valgt.get('intensitet', 'Ukjent')}")
    st.markdown(f"**Varighet:** {valgt.get('varighet', 'Ukjent')} min")

    inviter_partner = st.checkbox("👯 Inviter partner til denne økten")

    if st.button("✅ Legg til i planlagt trening"):
        # === Generer UUID for økten
        økt_id = str(uuid.uuid4())

        # === Lagre økten i planlagt_trening
        planlagt_response = supabase.table("planlagt_trening").insert({
            "id": økt_id,
            "bruker_id": bruker_id,
            "dato": str(valgt_dato),
            "øvelse": valgt["navn"],
            "kategori": valgt["kategori"],
            "beskrivelse": valgt["beskrivelse"],
            "kommentar": "",
            "kilde": "øvelsesbank"
        }).execute()

        if not planlagt_response.data:
            st.error("Noe gikk galt ved lagring av økten.")
            return

        st.success(f"✅ Økten '{valgt['navn']}' er lagt til planen!")

        # === Inviter partner hvis valgt
        if inviter_partner:
            partner_respons = supabase.table("partners").select("user_a_id, user_b_id")\
                .or_(f"user_a_id.eq.{bruker_id},user_b_id.eq.{bruker_id}")\
                .eq("status", "aktiv").execute()

            if not partner_respons.data:
                st.warning("Du har ingen aktiv partner å invitere.")
                return

            partner_data = partner_respons.data[0]
            partner_local_id = partner_data["user_b_id"] if partner_data["user_a_id"] == bruker_id else partner_data["user_a_id"]

            # Hent partnerens e-post fra brukere-tabellen
            partner_email_resp = supabase.table("brukere").select("email").eq("id", partner_local_id).execute()
            partner_email = partner_email_resp.data[0]["email"] if partner_email_resp.data else None

            # Hent partnerens UUID fra auth_users view
            partner_auth_resp = supabase.table("auth_users").select("id").eq("email", partner_email).execute()
            partner_uuid = partner_auth_resp.data[0]["id"] if partner_auth_resp.data else None

            if not partner_uuid:
                st.error("Fant ikke partnerens UUID – kan ikke sende invitasjon.")
                return

            # Send invitasjon
            invitasjon_response = supabase.table("treningsinvitasjoner").insert({
                "trening_id": økt_id,
                "fra_bruker_id": bruker_id,
                "til_partner_id": partner_uuid,
                "status": "venter"
            }).execute()

            if invitasjon_response.data:
                st.success("📨 Partner er invitert til økten!")
            else:
                st.error("Kunne ikke sende invitasjon – prøv igjen.")
