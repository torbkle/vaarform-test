import streamlit as st
from components.auth import supabase

def godkjenn_treningsinvitasjoner():
    st.subheader("📨 Treningsinvitasjoner")

    bruker_id = st.session_state["user"].id

    # Hent invitasjoner som er sendt til denne brukeren
    respons = supabase.table("treningsinvitasjoner").select("id, trening_id, fra_bruker_id")\
        .eq("til_partner_id", bruker_id).eq("status", "venter").execute()

    invitasjoner = respons.data

    if not invitasjoner:
        st.info("Du har ingen treningsinvitasjoner.")
        return

    for invitasjon in invitasjoner:
        trening_id = invitasjon["trening_id"]
        invitasjon_id = invitasjon["id"]
        fra_id = invitasjon["fra_bruker_id"]

        # Hent treningsdetaljer
        trening_respons = supabase.table("planlagt_trening").select("*").eq("id", trening_id).execute()
        if not trening_respons.data:
            st.warning(f"⚠️ Økten til invitasjon {invitasjon_id} finnes ikke lenger.")
            continue

        trening = trening_respons.data[0]

        # Hent e-post til avsender
        bruker_respons = supabase.table("brukere").select("email").eq("id", fra_id).execute()
        fra_bruker = bruker_respons.data[0]["email"] if bruker_respons.data else "Ukjent"

        st.markdown(f"📅 Økt fra **{fra_bruker}** – {trening['dato']}")
        st.markdown(f"**Øvelse:** {trening.get('øvelse', 'Ukjent')}")
        st.markdown(f"**Kategori:** {trening.get('kategori', 'Ukjent')}")
        st.markdown(f"**Beskrivelse:** {trening.get('beskrivelse', 'Ingen beskrivelse')}")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Godkjenn", key=f"godkjenn_{invitasjon_id}"):
                # Kopier økten til partnerens treningstabell
                supabase.table("trening").insert({
                    "bruker_id": bruker_id,
                    "dato": trening["dato"],
                    "øvelse": trening["øvelse"],
                    "kategori": trening["kategori"],
                    "beskrivelse": trening["beskrivelse"],
                    "kommentar": f"Godkjent fra {fra_bruker}",
                    "kilde": "partnerinvitasjon"
                }).execute()

                # Oppdater invitasjon
                supabase.table("treningsinvitasjoner").update({"status": "godkjent"}).eq("id", invitasjon_id).execute()
                st.success("Økten er lagt til din logg.")
                st.rerun()

        with col2:
            if st.button("❌ Avslå", key=f"avslå_{invitasjon_id}"):
                supabase.table("treningsinvitasjoner").update({"status": "avslått"}).eq("id", invitasjon_id).execute()
                st.warning("Invitasjonen er avslått.")
                st.rerun()
