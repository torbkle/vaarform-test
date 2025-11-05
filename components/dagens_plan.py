import streamlit as st
from components.auth import supabase
from datetime import date

def dagens_plan():
    st.subheader("📅 Dagens plan")

    bruker_id = st.session_state["user"].id

    if "valgt_dato" not in st.session_state:
        st.session_state["valgt_dato"] = date.today()

    valgt_dato_input = st.date_input("Velg dato:", value=st.session_state["valgt_dato"], key="dato_valg")

    if valgt_dato_input != st.session_state["valgt_dato"]:
        st.session_state["valgt_dato"] = valgt_dato_input
        st.session_state["vis_side"] = "hjem"
        st.rerun()

    valgt_dato = st.session_state["valgt_dato"]

    egne_økter = supabase.table("planlagt_trening").select("*")\
        .eq("bruker_id", bruker_id)\
        .eq("dato", str(valgt_dato)).execute().data

    invitasjoner = supabase.table("treningsinvitasjoner").select("*")\
        .eq("til_partner_id", bruker_id)\
        .eq("status", "godkjent").execute().data

    invitasjon_map = {str(inv["trening_id"]): inv for inv in invitasjoner}
    inviterte_ider = list(invitasjon_map.keys())

    inviterte_økter = []
    for trening_id in inviterte_ider:
        økt_resp = supabase.table("planlagt_trening").select("*")\
            .eq("id", trening_id)\
            .eq("dato", str(valgt_dato)).execute().data
        if økt_resp:
            inviterte_økter.extend(økt_resp)

    alle_økter = egne_økter + inviterte_økter

    if not alle_økter:
        st.info("Ingen planlagte økter for valgt dato.")
        return

    for økt in alle_økter:
        økt_id = str(økt["id"])
        er_egen_økt = økt["bruker_id"] == bruker_id
        er_invitasjon = økt_id in invitasjon_map

        st.markdown(f"### 🏋️ Økt: {økt.get('øvelse', 'Ukjent')}")
        st.markdown(f"- Kategori: {økt.get('kategori', 'Ukjent')}")
        st.markdown(f"- Beskrivelse: {økt.get('beskrivelse', 'Ingen beskrivelse')}")
        st.markdown(f"- Kommentar: {økt.get('kommentar', '')}")

        if er_invitasjon:
            partner_id = invitasjon_map[økt_id]["fra_bruker_id"]
            partnerinfo_resp = supabase.table("brukerinfo").select("brukernavn") \
                .eq("bruker_id", partner_id).execute()
            partnernavn = partnerinfo_resp.data[0]["brukernavn"] if partnerinfo_resp.data else "Ukjent"
            st.markdown(f"🔗 Partnerøkt fra `{partnernavn}`")

        # Sjekk om denne brukeren har markert som gjennomført
        gjennomført_resp = supabase.table("gjennomført_trening").select("*")\
            .eq("trening_id", økt_id)\
            .eq("bruker_id", bruker_id).execute().data

        if gjennomført_resp:
            st.success("✅ Du har markert denne som gjennomført.")
        else:
            if st.button("✅ Marker som gjennomført", key=f"fullført_{økt_id}_{valgt_dato}"):
                supabase.table("gjennomført_trening").insert({
                    "trening_id": økt_id,
                    "bruker_id": bruker_id,
                    "dato": str(valgt_dato),
                    "status": True
                }).execute()
                st.success("Du har nå markert økten som gjennomført.")
                st.session_state["vis_side"] = "hjem"
                st.rerun()

        if er_egen_økt:
            if st.button("🗑 Slett økt", key=f"slett_{økt_id}_{valgt_dato}"):
                supabase.table("planlagt_trening").delete().eq("id", økt_id).execute()
                st.success("Økten er slettet.")
                st.session_state["vis_side"] = "hjem"
                st.rerun()
