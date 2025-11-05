import streamlit as st
from components.auth import supabase

def vis_redigerbar_profil():
    st.subheader("👤 Min profil")

    bruker_id = st.session_state["user"].id
    brukerinfo = st.session_state.get("brukerinfo")

    # === Hent fra Supabase hvis ikke allerede i session_state ===
    if not brukerinfo:
        respons = supabase.table("brukerinfo").select("*").eq("bruker_id", bruker_id).execute()
        if respons.data:
            brukerinfo = respons.data[0]
            st.session_state["brukerinfo"] = brukerinfo

    # === Vis profiloppsummering hvis lagret ===
    if brukerinfo and not st.session_state.get("rediger_profil"):
        st.success("✅ Profil lagret!")
        st.markdown(f"**Brukernavn:** {brukerinfo.get('brukernavn', '')}")
        st.markdown(f"**Fornavn:** {brukerinfo.get('fornavn', '')}")
        st.markdown(f"**Etternavn:** {brukerinfo.get('etternavn', '')}")
        st.markdown(f"**Adresse:** {brukerinfo.get('adresse', '')}")
        st.markdown(f"**Kjønn:** {brukerinfo.get('kjønn', '')}")
        st.markdown(f"**Alder:** {brukerinfo.get('alder', '')} år")
        st.markdown(f"**Høyde:** {brukerinfo.get('høyde_cm', '')} cm")
        st.markdown(f"**Startvekt:** {brukerinfo.get('startvekt', '')} kg")
        st.markdown(f"**Målvekt:** {brukerinfo.get('målvekt_kg', '')} kg")
        st.markdown(f"**Treningsmål:** {brukerinfo.get('treningsmål', '')}")

        if st.button("✏️ Rediger profil"):
            st.session_state["rediger_profil"] = True
            st.rerun()

    # === Skjema for ny eller redigert profil ===
    else:
        st.markdown("### ➕ Legg inn eller rediger profil")
        with st.form("profil_form"):
            brukernavn = st.text_input("Brukernavn", value=brukerinfo.get("brukernavn", "") if brukerinfo else "")
            fornavn = st.text_input("Fornavn", value=brukerinfo.get("fornavn", "") if brukerinfo else "")
            etternavn = st.text_input("Etternavn", value=brukerinfo.get("etternavn", "") if brukerinfo else "")
            adresse = st.text_input("Adresse", value=brukerinfo.get("adresse", "") if brukerinfo else "")
            kjønn = st.selectbox("Kjønn", ["", "Mann", "Kvinne", "Annet"], index=["", "Mann", "Kvinne", "Annet"].index(brukerinfo.get("kjønn", "") if brukerinfo else ""))
            alder = int(st.number_input("Alder", min_value=0, max_value=120, value=int(brukerinfo.get("alder", 0) if brukerinfo else 0)))
            høyde_cm = int(st.number_input("Høyde (cm)", min_value=0, value=int(brukerinfo.get("høyde_cm", 0) if brukerinfo else 0)))
            startvekt = int(st.number_input("Startvekt (kg)", min_value=0.0, value=float(brukerinfo.get("startvekt", 0) if brukerinfo else 0)))
            målvekt_kg = int(st.number_input("Målvekt (kg)", min_value=0.0, value=float(brukerinfo.get("målvekt_kg", 0) if brukerinfo else 0)))
            treningsmål = st.text_area("Treningsmål", value=brukerinfo.get("treningsmål", "") if brukerinfo else "")
            lagre = st.form_submit_button("💾 Lagre profil")

        if lagre:
            data = {
                "brukernavn": brukernavn,
                "fornavn": fornavn,
                "etternavn": etternavn,
                "adresse": adresse,
                "kjønn": kjønn,
                "alder": alder,
                "startvekt": startvekt,
                "høyde_cm": høyde_cm,
                "målvekt_kg": målvekt_kg,
                "treningsmål": treningsmål,
                "bruker_id": bruker_id
            }

            eksisterende = supabase.table("brukerinfo").select("*").eq("bruker_id", bruker_id).execute()

            if eksisterende.data:
                supabase.table("brukerinfo").update(data).eq("bruker_id", bruker_id).execute()
                st.success("✅ Profil oppdatert!")
            else:
                supabase.table("brukerinfo").insert(data).execute()
                st.success("✅ Profil opprettet!")

            st.session_state["brukerinfo"] = data
            st.session_state["rediger_profil"] = False
            st.rerun()
