import streamlit as st
from components.auth import supabase

def admin_okt():
    st.title("🛠️ Adminpanel – Øvelsesbank")

    # === Tilgangssjekk ===
    if st.session_state["user"].email != "admin@infera.no":
        st.error("⛔ Du har ikke tilgang til denne siden.")
        st.stop()

    st.success("✅ Du er logget inn som administrator.")
    st.markdown("Her kan du legge til, redigere og slette økter i øvelsesbanken.")

    # === Tilstand for skjema ===
    if "vis_nytt_skjema" not in st.session_state:
        st.session_state["vis_nytt_skjema"] = True

    # === Skjema for ny økt ===
    if st.session_state["vis_nytt_skjema"]:
        st.markdown("### ➕ Legg til ny økt")
        with st.form("ny_økt_form"):
            kategori = st.selectbox("Kategori", ["Løping", "Styrke", "Hvile"])
            underkategori = st.text_input("Underkategori", placeholder="F.eks. Intervall, Fullkropp, Yoga")
            navn = st.text_input("Navn på økt")
            beskrivelse = st.text_area("Beskrivelse")
            oppvarming = st.text_input("Oppvarming")
            nedjogging = st.text_input("Nedjogging")
            intensitet = st.text_input("Intensitet")
            varighet = st.number_input("Varighet (min)", min_value=5, max_value=180, step=5)
            submit = st.form_submit_button("✅ Legg til økt")

        if submit:
            supabase.table("øvelsesbank").insert({
                "kategori": kategori,
                "underkategori": underkategori,
                "navn": navn,
                "beskrivelse": beskrivelse,
                "oppvarming": oppvarming,
                "nedjogging": nedjogging,
                "intensitet": intensitet,
                "varighet": varighet,
                "kilde": "egen"
            }).execute()
            st.session_state["vis_nytt_skjema"] = False
            st.session_state["sist_lagt_til"] = navn
            st.rerun()

    else:
        st.success(f"✅ Økten '{st.session_state['sist_lagt_til']}' er lagt til!")
        if st.button("➕ Legg til ny økt"):
            st.session_state["vis_nytt_skjema"] = True
            st.rerun()

    # === Rediger eksisterende økter ===
    st.markdown("### 🔍 Rediger eksisterende økter")
    kategori_filter = st.selectbox("Filtrer kategori", ["Løping", "Styrke", "Hvile"], key="filter_kategori")
    underkategori_filter = st.text_input("Filtrer underkategori", key="filter_underkategori")

    if kategori_filter and underkategori_filter:
        result = supabase.table("øvelsesbank").select("*").eq("kategori", kategori_filter).eq("underkategori", underkategori_filter).execute()
        økter = result.data

        if økter:
            for økt in økter:
                with st.expander(f"✏️ {økt['navn']}"):
                    st.text_area("Beskrivelse", value=økt["beskrivelse"], key=f"beskrivelse_{økt['id']}")
                    st.text_input("Oppvarming", value=økt["oppvarming"], key=f"oppvarming_{økt['id']}")
                    st.text_input("Nedjogging", value=økt["nedjogging"], key=f"nedjogging_{økt['id']}")
                    st.text_input("Intensitet", value=økt["intensitet"], key=f"intensitet_{økt['id']}")
                    st.number_input("Varighet (min)", value=økt["varighet"], key=f"varighet_{økt['id']}")

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 Oppdater", key=f"update_{økt['id']}"):
                            supabase.table("øvelsesbank").update({
                                "beskrivelse": st.session_state[f"beskrivelse_{økt['id']}"],
                                "oppvarming": st.session_state[f"oppvarming_{økt['id']}"],
                                "nedjogging": st.session_state[f"nedjogging_{økt['id']}"],
                                "intensitet": st.session_state[f"intensitet_{økt['id']}"],
                                "varighet": st.session_state[f"varighet_{økt['id']}"]
                            }).eq("id", økt["id"]).execute()
                            st.success("Økt oppdatert!")

                    with col2:
                        if st.button("🗑 Slett", key=f"delete_{økt['id']}"):
                            supabase.table("øvelsesbank").delete().eq("id", økt["id"]).execute()
                            st.warning("Økt slettet.")
                            st.rerun()
        else:
            st.info("Ingen økter funnet for valgt kategori og underkategori.")

    # === Admin-indikator ===
    st.markdown("---")
    st.caption("🧑‍💼 Du har full tilgang som administrator.")
