import streamlit as st
from components.auth import supabase

def test_invitasjoner():
    st.subheader("🧪 Test: Invitasjoner til innlogget bruker")

    bruker_id = st.session_state["user"].id

    # Hent invitasjoner der bruker er mottaker
    invitasjoner = supabase.table("treningsinvitasjoner").select("*").eq("til_partner_id", bruker_id).execute().data

    if not invitasjoner:
        st.info("Ingen invitasjoner funnet.")
        return

    # Hent alle økt-IDer for feilsøking
    alle_økter = supabase.table("planlagt_trening").select("id").execute().data
    alle_økt_ider = [økt["id"] for økt in alle_økter]
    st.write("🧾 Økter i databasen:", alle_økt_ider)

    for inv in invitasjoner:
        st.write("🔍 Søker etter økt med ID:", inv["trening_id"])

        # Bruk filter i stedet for eq for robust matching
        trening_id = str(inv["trening_id"]).strip()
        #økt_resp = supabase.table("planlagt_trening").select("*").filter("id", "eq", trening_id).execute()
        økt_resp = supabase.table("planlagt_trening").select("*").filter("id", "eq",
                                                                         "04605928-6606-437e-81c2-2b6939a150bc").execute()
        st.write("🔍 Hardkodet test:", økt_resp.data)

        st.write("📦 Økt-respons (etter rens):", økt_resp.data)


        økt = økt_resp.data[0] if økt_resp.data else None

        with st.expander(f"📨 Invitasjon: {inv['id']} – Status: {inv['status']}"):
            st.markdown(f"**Fra bruker:** `{inv['fra_bruker_id']}`")
            st.markdown(f"**Til partner:** `{inv['til_partner_id']}`")
            st.markdown(f"**Trening ID:** `{inv['trening_id']}`")

            if økt:
                st.markdown(f"**Øvelse:** {økt['øvelse']}")
                st.markdown(f"**Dato:** {økt['dato']}")
                st.markdown(f"**Kategori:** {økt.get('kategori', 'Ukjent')}")
                st.markdown(f"**Beskrivelse:** {økt.get('beskrivelse', 'Ingen')}")
                if inv["status"] == "venter":
                    if st.button("✅ Godkjenn økt", key=inv["id"]):
                        supabase.table("treningsinvitasjoner").update({"status": "godkjent"}).eq("id", inv["id"]).execute()
                        st.success("Økten er godkjent!")
                        st.rerun()
            else:
                st.error("⚠️ Økten finnes ikke – sjekk trening_id eller UUID-format.")
