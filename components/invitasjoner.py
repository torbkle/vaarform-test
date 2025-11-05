import streamlit as st
from components.auth import supabase

def vis_invitasjoner():
    st.subheader("📨 Dine treningsinvitasjoner")

    bruker_id = st.session_state["user"].id

    # === Hent alle invitasjoner til bruker
    invitasjoner = supabase.table("treningsinvitasjoner").select("*")\
        .eq("til_partner_id", bruker_id).execute().data

    if not invitasjoner:
        st.info("Du har ingen invitasjoner.")
        return

    # === Vis invitasjoner som tabell
    st.markdown("### 📊 Invitasjonsoversikt")
    rows = []

    for inv in invitasjoner:
        trening_id = inv["trening_id"]
        økt_resp = supabase.table("planlagt_trening").select("*")\
            .eq("id", trening_id).execute()
        økt = økt_resp.data[0] if økt_resp.data else None

        partner_resp = supabase.table("auth_users").select("email")\
            .eq("id", inv["fra_bruker_id"]).execute()
        partner_email = partner_resp.data[0]["email"] if partner_resp.data else "Ukjent"

        status = inv["status"]
        farge = {
            "godkjent": "✅",
            "avvist": "❌",
            "venter": "⏳"
        }.get(status, "❔")

        etikett = {
            "godkjent": "🔗 Partnerøkt (godkjent)",
            "avvist": "🚫 Avvist",
            "venter": "⏳ Venter på svar"
        }.get(status, "")

        rows.append({
            "Øvelse": økt["øvelse"] if økt else "⚠️ Økt mangler",
            "Dato": økt["dato"] if økt else "-",
            "Partner": partner_email,
            "Status": f"{farge} {status}",
            "Kommentar": økt["kommentar"] if økt else "",
            "Etikett": etikett,
            "Invitasjon ID": inv["id"]
        })

    st.dataframe(rows, use_container_width=True)

    # === Godkjenn / Avvis invitasjoner
    st.markdown("### ✍️ Behandle invitasjoner")
    for inv in invitasjoner:
        if inv["status"] == "venter":
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"✅ Godkjenn {inv['id']}", key=f"godkjenn_{inv['id']}"):
                    supabase.table("treningsinvitasjoner").update({"status": "godkjent"}).eq("id", inv["id"]).execute()
                    st.success(f"Invitasjon {inv['id']} er godkjent.")
                    st.rerun()
            with col2:
                if st.button(f"❌ Avvis {inv['id']}", key=f"avvis_{inv['id']}"):
                    supabase.table("treningsinvitasjoner").update({"status": "avvist"}).eq("id", inv["id"]).execute()
                    st.info(f"Invitasjon {inv['id']} er avvist.")
                    st.rerun()

    # === Slett-knapper
    st.markdown("### 🗑 Slett invitasjoner")
    for inv in invitasjoner:
        if st.button(f"Slett invitasjon {inv['id']}", key=f"slett_{inv['id']}"):
            supabase.table("treningsinvitasjoner").delete().eq("id", inv["id"]).execute()
            st.success(f"Invitasjon {inv['id']} er slettet.")
            st.rerun()
