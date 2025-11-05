import streamlit as st
from datetime import date
from components.auth import supabase

def importer_trening():
    st.subheader("📥 Importer trening – velg forslag")

    # === Velg kategori ===
    kategori = st.selectbox("Velg kategori:", ["Løping", "Styrke", "Hvile"])

    # === Forslag basert på kategori ===
    forslag = {
        "Løping": [
            {"navn": "Intervall – 4×4", "beskrivelse": "4 drag à 4 min med 2 min pause"},
            {"navn": "Rolig langtur", "beskrivelse": "45–60 min rolig tempo"},
            {"navn": "Bakkeløp", "beskrivelse": "6 drag i motbakke"},
            {"navn": "Gå/jogg", "beskrivelse": "30 min lett aktivitet"}
        ],
        "Styrke": [
            {"navn": "Fullkropp", "beskrivelse": "3 sett x 5 øvelser"},
            {"navn": "Beinøkt", "beskrivelse": "Knebøy, utfall, hip thrust"},
            {"navn": "Overkropp", "beskrivelse": "Pullups, benkpress, roing"},
            {"navn": "Kjernestyrke", "beskrivelse": "15 min mage/rygg"}
        ],
        "Hvile": [
            {"navn": "Gå tur", "beskrivelse": "30 min rolig tur"},
            {"navn": "Yoga", "beskrivelse": "20 min myk yoga"},
            {"navn": "Stretching", "beskrivelse": "Lett tøying av hele kroppen"},
            {"navn": "Mental pause", "beskrivelse": "Lesing, meditasjon eller pust"}
        ]
    }

    # === Velg forslag ===
    valg = st.radio("Velg økt:", [f["navn"] for f in forslag[kategori]])
    valgt_forslag = next(f for f in forslag[kategori] if f["navn"] == valg)

    st.markdown(f"**Beskrivelse:** {valgt_forslag['beskrivelse']}")

    # === Tilpasning (valgfritt) ===
    kommentar = st.text_input("Kommentar (valgfritt)", placeholder="F.eks. føltes lett, gjorde 5 drag i stedet for 4")

    # === Lagre til Supabase ===
    if st.button("✅ Importer økt"):
        data = {
            "bruker_id": st.session_state["user"].id,
            "dato": str(date.today()),
            "øvelse": valgt_forslag["navn"],
            "kategori": kategori,
            "beskrivelse": valgt_forslag["beskrivelse"],
            "kommentar": kommentar,
            "kilde": "forslag"
        }
        supabase.table("trening").insert(data).execute()
        st.success(f"✅ Økten '{valg}' er importert!")
