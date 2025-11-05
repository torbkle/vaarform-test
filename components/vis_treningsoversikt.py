import streamlit as st
import pandas as pd
import altair as alt
from components.auth import supabase

def vis_treningsoversikt(user_id, partner_id=None):
    st.subheader("📊 Treningsoversikt")

    # === Hjelpefunksjon for å hente øvelsesnavn fra planlagt_trening
    def hent_øvelse(trening_id):
        if not trening_id:
            return "Ukjent økt"
        resp = supabase.table("planlagt_trening").select("øvelse").eq("id", trening_id).execute()
        if resp.data and "øvelse" in resp.data[0]:
            return resp.data[0]["øvelse"]
        return "Ukjent økt"

    # === Din siste gjennomførte trening
    bruker_resp = supabase.table("gjennomført_trening").select("*") \
        .eq("bruker_id", user_id).order("dato", desc=True).limit(1).execute()


    if bruker_resp.data:
        siste = bruker_resp.data[0]
        dato = siste.get("dato", "Ukjent")
        status = "✅ Fullført" if siste.get("status") else "❌ Ikke fullført"
        øvelse = hent_øvelse(siste.get("trening_id"))
        st.markdown(f"**Din siste trening:** {dato} – {øvelse}")
        st.markdown(f"**Status:** {status}")
    else:
        st.info("Du har ikke registrert noen trening ennå 💤")

    # === Partnerens siste gjennomførte trening
    if partner_id:
        partner_resp = supabase.table("gjennomført_trening").select("*") \
            .eq("bruker_id", partner_id).order("dato", desc=True).limit(1).execute()

        if partner_resp.data:
            siste_p = partner_resp.data[0]
            dato_p = siste_p.get("dato", "Ukjent")
            status_p = "✅ Fullført" if siste_p.get("status") else "❌ Ikke fullført"
            øvelse_p = hent_øvelse(siste_p.get("trening_id"))
            st.markdown(f"**Partnerens siste trening:** {dato_p} – {øvelse_p}")
            st.markdown(f"**Status:** {status_p}")
        else:
            st.info("Partneren din har ikke registrert noen trening ennå 💤")

    # === Hent siste 30 dager for begge
    def hent_data(bruker_id, navn):
        data = supabase.table("gjennomført_trening").select("dato", "trening_id") \
            .eq("bruker_id", bruker_id).execute().data
        df = pd.DataFrame(data) if data else pd.DataFrame()
        if not df.empty:
            df["dato"] = pd.to_datetime(df["dato"])
            df = df[df["dato"] > pd.Timestamp.now() - pd.Timedelta(days=30)]
            df["øvelse"] = df["trening_id"].apply(hent_øvelse)
            df["antall"] = 1
            df["bruker"] = navn
        return df

    df1 = hent_data(user_id, "Deg")
    df2 = hent_data(partner_id, "Partner") if partner_id else pd.DataFrame()
    df = pd.concat([df1, df2])

    # === Boost-melding
    total_deg = df1["antall"].sum() if not df1.empty else 0
    total_partner = df2["antall"].sum() if not df2.empty else 0

    if total_partner > total_deg:
        st.success("🚀 Partneren din har trent mer enn deg siste 30 dager – tid for en boost!")
    elif total_deg > total_partner and total_partner > 0:
        st.info("👏 Du ligger foran partneren din – hold momentet oppe!")
    elif total_deg == total_partner and total_deg > 0:
        st.info("🤝 Dere ligger likt – perfekt for en felles økt!")

    # === Vis graf
    if not df.empty:
        chart = alt.Chart(df).mark_bar().encode(
            x="dato:T",
            y="antall:Q",
            color="bruker:N",
            tooltip=["dato", "øvelse", "bruker"]
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("Ingen treningsøkter registrert siste 30 dager.")
