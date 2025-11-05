import streamlit as st
from components.auth import supabase
from components.partnerlogikk import hent_partner_id, hent_partnerinfo
from datetime import date, timedelta
import calendar

def vis_valgt_økt(bruker_id, partner_id):
    valgt_dato = st.session_state["valgt_dato_detalj"]
    valgt_økt = st.session_state["valgt_øktnavn"]
    valgt_eier = st.session_state["valgt_eier"]
    valgt_id = bruker_id if valgt_eier == "meg" else partner_id

    st.markdown(f"### 📝 Detaljer for {valgt_økt} ({valgt_dato})")

    respons = supabase.table("planlagt_trening").select("*")\
        .eq("dato", valgt_dato).eq("bruker_id", valgt_id).execute()
    økter = respons.data
    for økt in økter:
        if økt.get("øvelse") == valgt_økt:
            st.markdown(f"**Kategori:** {økt.get('kategori', 'Ukjent')}")
            st.markdown(f"**Beskrivelse:** {økt.get('beskrivelse', 'Ingen beskrivelse')}")
            st.markdown(f"**Kommentar:** {økt.get('kommentar', '')}")
            st.markdown(f"**Kilde:** {økt.get('kilde', 'Ukjent')}")

def månedsplan():
    st.subheader("📅 Månedsplan – Treningskalender med partner")

    bruker_id = st.session_state["user"].id
    partner_id = hent_partner_id(bruker_id)
    partnerinfo = hent_partnerinfo(partner_id)

    if partnerinfo:
        st.info(f"👯 Du er koblet til: **{partnerinfo['navn']}** (`{partnerinfo['brukernavn']}`)")
    else:
        st.warning("Du har ikke koblet til en partner ennå.")

    if "måned_offset" not in st.session_state:
        st.session_state["måned_offset"] = 0

    today = date.today()
    valgt_måned = (today.replace(day=1) + timedelta(days=30 * st.session_state["måned_offset"]))
    måned_navn = valgt_måned.strftime("%B %Y")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Forrige måned"):
            st.session_state["måned_offset"] -= 1
            st.rerun()
    with col2:
        st.markdown(f"<h3 style='text-align:center;'>{måned_navn}</h3>", unsafe_allow_html=True)
    with col3:
        if st.button("➡️ Neste måned"):
            st.session_state["måned_offset"] += 1
            st.rerun()

    første_dag = valgt_måned
    siste_dag = første_dag.replace(day=calendar.monthrange(første_dag.year, første_dag.month)[1])

    def hent_økter(for_id):
        return supabase.table("planlagt_trening").select("*")\
            .eq("bruker_id", for_id)\
            .gte("dato", str(første_dag))\
            .lte("dato", str(siste_dag)).execute().data

    økter = hent_økter(bruker_id)
    partner_økter = hent_økter(partner_id) if partner_id else []

    gjennomføringer = supabase.table("gjennomført_trening").select("*")\
        .gte("dato", str(første_dag)).lte("dato", str(siste_dag)).execute().data

    gjennomført_map = {}
    for g in gjennomføringer:
        key = f"{g['trening_id']}_{g['bruker_id']}"
        gjennomført_map[key] = True

    dato_dict = {}
    for økt in økter + partner_økter:
        økt_id = str(økt["id"])
        d = økt["dato"]
        if d not in dato_dict:
            dato_dict[d] = []
        dato_dict[d].append({
            "id": økt_id,
            "navn": økt.get("øvelse", "Ukjent økt"),
            "kategori": økt.get("kategori", "Ukjent"),
            "beskrivelse": økt.get("beskrivelse", ""),
            "eier": "meg" if økt["bruker_id"] == bruker_id else "partner",
            "gjennomført_meg": gjennomført_map.get(f"{økt_id}_{bruker_id}", False),
            "gjennomført_partner": gjennomført_map.get(f"{økt_id}_{partner_id}", False)
        })

    for key in ["valgt_dato_detalj", "valgt_øktnavn", "valgt_eier"]:
        if key not in st.session_state:
            st.session_state[key] = None

    ukedager = ["Man", "Tir", "Ons", "Tor", "Fre", "Lør", "Søn"]
    kolonner = st.columns(7)
    for i, dag in enumerate(ukedager):
        with kolonner[i]:
            st.markdown(f"**{dag}**")

    start_ukedag = første_dag.weekday()
    dag = første_dag
    celler = [None] * start_ukedag

    while dag <= siste_dag:
        celler.append(dag)
        dag += timedelta(days=1)

    while len(celler) % 7 != 0:
        celler.append(None)

    for uke_start in range(0, len(celler), 7):
        uke = celler[uke_start:uke_start + 7]
        kolonner = st.columns(7)
        for i, dag in enumerate(uke):
            with kolonner[i]:
                if dag:
                    er_i_dag = (dag == date.today())
                    bakgrunn = "#e6f7ff" if er_i_dag else "transparent"
                    st.markdown(
                        f"<div style='padding: 6px; border-radius: 6px; background-color: {bakgrunn}; text-align: center;'>"
                        f"<strong>{dag.day}</strong></div>",
                        unsafe_allow_html=True
                    )

                    if str(dag) in dato_dict:
                        for økt_index, økt in enumerate(dato_dict[str(dag)]):
                            navn = økt["navn"]
                            eier = økt["eier"]
                            gjennomført_meg = økt["gjennomført_meg"]
                            gjennomført_partner = økt["gjennomført_partner"]

                            if gjennomført_meg and gjennomført_partner:
                                ikon = "✅"
                            elif gjennomført_meg:
                                ikon = "🧍"
                            elif gjennomført_partner:
                                ikon = "👥"
                            else:
                                ikon = "▫️"

                            unik_key = f"{dag}_{navn}_{eier}_{økt_index}"

                            if st.button(f"{ikon} {navn}", key=unik_key):
                                st.session_state["valgt_dato_detalj"] = str(dag)
                                st.session_state["valgt_øktnavn"] = navn
                                st.session_state["valgt_eier"] = eier
                                st.rerun()

    if st.session_state["valgt_dato_detalj"] and st.session_state["valgt_øktnavn"]:
        vis_valgt_økt(bruker_id, partner_id)

    st.markdown("---")
    st.markdown("### 📈 Ukesoppsummering")

    dag_i_dag = date.today()
    start_uke = dag_i_dag - timedelta(days=dag_i_dag.weekday())
    slutt_uke = start_uke + timedelta(days=6)

    ukens_økter = []
    for dato_str, økter_liste in dato_dict.items():
        dato = date.fromisoformat(dato_str)
        if start_uke <= dato <= slutt_uke:
            ukens_økter.extend(økter_liste)

    antall_økter = len(ukens_økter)
    antall_gjennomført = sum(1 for økt in ukens_økter if økt["gjennomført_meg"])
    prosent = int((antall_gjennomført / antall_økter) * 100) if antall_økter else 0

    fremdrift_html = ""
    for økt in ukens_økter:
        fremdrift_html += "<span style='color:green;'>✅</span> " if økt["gjennomført_meg"] else "<span style='color:#ccc;'>▫️</span> "

    feiring = ""
    if prosent == 100 and antall_økter > 0:
        feiring = "<div style='background-color:#d4f4dd; padding:10px; border-radius:8px; text-align:center;'>🎉 <strong>Fantastisk!</strong> Du har gjennomført alle økter denne uken!</div>"

    st.markdown(f"""
    <div style='padding:10px; background-color:#f9f9f9; border-radius:8px;'>
        <strong>Planlagte økter:</strong> {antall_økter}<br>
        <strong>Gjennomført:</strong> {antall_gjennomført} av {antall_økter} ({prosent}%)<br>
        <strong>Fremdrift:</strong> {fremdrift_html}
    </div>
    """, unsafe_allow_html=True)

    if feiring:
        st.markdown(feiring, unsafe_allow_html=True)

