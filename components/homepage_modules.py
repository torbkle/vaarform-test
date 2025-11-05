import streamlit as st
from components.auth import supabase
from components.godkjenn_partner import godkjenn_partner
from components.vis_tilbakemelding import vis_tilbakemelding
from components.vis_treningsoversikt import vis_treningsoversikt

def show_homepage_modules(partner_id=None):

    st.subheader("📋 Din oversikt")
    st.info("""
    🧪 **Dette er en testversjon av VårForm (v1.0)**  
    Du er blant de første som prøver ut appen – takk for at du er med! 🎉  
    Vi setter stor pris på alle tilbakemeldinger, forslag og feilrapporter.

    👉 Appen er under aktiv utvikling, og design og funksjoner vil forbedres fortløpende.  
    👉 Du kan sende inn tilbakemelding direkte nedenfor 👇
    """)

    bruker_id = st.session_state["user"].id
    vis_tilbakemelding(bruker_id)


    # === Partnerforespørsler
    forespørsler = supabase.table("partner_requests").select("id") \
        .eq("to_user_id", bruker_id) \
        .eq("status", "venter").execute().data

    if forespørsler:
        with st.expander("📥 Du har partnerforespørsler"):
            godkjenn_partner()

    # === Treningsinvitasjoner som venter
    invitasjoner = supabase.table("treningsinvitasjoner").select("*") \
        .eq("til_partner_id", bruker_id) \
        .eq("status", "venter").execute().data

    if invitasjoner:
        st.markdown("### 📨 Aktive treningsinvitasjoner")
        for inv in invitasjoner:
            inv_id = inv["id"]
            trening_id = inv["trening_id"]
            økt_resp = supabase.table("planlagt_trening").select("*") \
                .eq("id", trening_id).execute()
            økt = økt_resp.data[0] if økt_resp.data else None

            if not økt:
                st.warning(f"⚠️ Økten med ID `{trening_id}` finnes ikke.")
                continue

            st.markdown(f"**🏋️ Øvelse:** {økt.get('øvelse', 'Ukjent')}")
            st.markdown(f"**🗓️ Dato:** {økt.get('dato', 'Ukjent')}")
            st.markdown(f"**📌 Status:** `{inv['status']}`")
            st.markdown(f"**👤 Fra partner:** `{inv['fra_bruker_id']}`")

            if st.button("✍️ Behandle invitasjoner", key=f"invitasjon_{inv_id}"):
                st.session_state["vis_side"] = "invitasjoner"
                st.rerun()

            st.markdown("---")

    # === Første rad: Dagens plan og Siste trening
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.get("vis_side") in ["dagens_plan", "rerun_dagens_plan"]:
            from components.dagens_plan import dagens_plan
            dagens_plan()
        else:
            with st.expander("📆 Dagens plan"):
                from components.dagens_plan import dagens_plan
                dagens_plan()

    with col2:
        with st.expander("🏋️ Siste trening"):
            vis_treningsoversikt(bruker_id, partner_id)

    # === Andre rad: Partneroversikt og Månedsplan
    col3, col4 = st.columns(2)
    with col3:
        with st.expander("👥 Partneroversikt"):
            from components.aktiv_partner import vis_aktiv_partner
            vis_aktiv_partner()

    with col4:
        with st.expander("🗓️ Månedsplan"):
            from components.månedsplan import månedsplan
            månedsplan()


