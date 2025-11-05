import streamlit as st
from PIL import Image
import os
from components.auth import supabase, login, logout, signup, refresh_session
from components.homepage_modules import show_homepage_modules
from components.footer_menu import show_footer_menu
from components.profile import vis_redigerbar_profil
from components.invitasjoner import vis_invitasjoner
from components.partnerlogikk import hent_partner_id, hent_partnerinfo
import base64
from io import BytesIO
from datetime import datetime

def logo_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# === App config ===
st.set_page_config(page_title="VårForm", layout="wide")

# === Logo og tagline ===
logo_path = os.path.join("assets", "images", "varform.png")
logo_exists = os.path.exists(logo_path)
logo = Image.open(logo_path) if logo_exists else None


# === Hent refresh_token fra URL hvis nødvendig ===
params = st.query_params
if "refresh_token" in params and "refresh_token" not in st.session_state:
    st.session_state["refresh_token"] = params["refresh_token"]

# === Automatisk innlogging ved refresh ===
if "user" not in st.session_state or st.session_state["user"] is None:
    refresh_session()

# === Innlogging / registrering ===
if "user" not in st.session_state or st.session_state["user"] is None:
    # Stor logo før innlogging
    if os.path.exists(logo_path):
        logo = Image.open(logo_path)
        encoded_logo = logo_to_base64(logo)
        st.markdown(
            f"""
            <div style='text-align: center; margin-bottom: 1em;'>
                <img src='data:image/png;base64,{encoded_logo}' style='max-width: 90%; height: auto;'/>
                <div style='font-size: 1.2em; color: gray; margin-top: 0.5em;'>Din personlige treningspartner 💪</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center;'>
            <h3>🔐 Velkommen til VårForm</h3>
            <p style='font-size: 1.1em; color: gray;'>Logg inn eller opprett en ny konto for å komme i gang.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:


            mode = st.radio("Velg handling:", ["Logg inn", "Registrer ny bruker"], horizontal=True)
            email = st.text_input("📧 E-post", placeholder="din@email.no")
            password = st.text_input("🔑 Passord", type="password", placeholder="••••••••")

            if mode == "Logg inn" and st.button("✅ Logg inn"):
                result = login(email, password)
                if result:
                    st.query_params = {"refresh_token": result.session.refresh_token}
                    st.rerun()

            elif mode == "Registrer ny bruker" and st.button("🆕 Registrer"):
                result = signup(email, password)
                if result:
                    st.query_params = {"refresh_token": result.session.refresh_token}
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

    st.stop()


# === Bruker er innlogget ===
user_email = st.session_state["user"].email
user_id = st.session_state["user"].id




# Hent fullt navn og brukernavn fra brukerinfo
info_resp = supabase.table("brukerinfo").select("fornavn", "etternavn", "brukernavn").eq("bruker_id", user_id).execute()
if info_resp.data:
    fornavn = info_resp.data[0].get("fornavn", "")
    etternavn = info_resp.data[0].get("etternavn", "")
    brukernavn = info_resp.data[0].get("brukernavn", "")
    fullt_navn = f"{fornavn} {etternavn}".strip()
else:
    fullt_navn = ""
    brukernavn = ""



# === Liten logo etter innlogging med dynamisk tagline ===
if logo:
    encoded_logo = logo_to_base64(logo)

    # Finn tidspunkt på dagen
    hour = datetime.now().hour
    if hour < 12:
        hilsen = f"God morgen, <strong>{fullt_navn}</strong> 💪"
    elif hour < 18:
        hilsen = f"Klar for en ny treningsøkt, <strong>{fullt_navn}</strong>? 💪"
    else:
        hilsen = f"Kveldstrening i sikte, <strong>{fullt_navn}</strong>? 💪"

    st.markdown(
        f"""
        <div style='text-align: center; margin-bottom: 1em;'>
            <img src='data:image/png;base64,{encoded_logo}' style='max-width: 300px; height: auto;'/>
            <div style='font-size: 1em; color: gray; margin-top: 0.5em;'>{hilsen}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# Hent partnerinfo via partnerlogikk
partner_id = hent_partner_id(user_id)
partnerinfo = hent_partnerinfo(partner_id)

if partnerinfo:
    partner_visning = f"{partnerinfo['navn']} (`{partnerinfo['brukernavn']}`)"
else:
    partner_visning = "Ingen partner valgt"

# === Vis profilboks
st.markdown(
    f"""
    <div style='padding: 0.5em; border: 1px solid #ddd; border-radius: 8px; background-color: #f9f9f9; margin-bottom: 1em;'>
        <strong>✅ Innlogget som:</strong><br>
        <span style='font-size: 1.1em;'>{fullt_navn} <code>({brukernavn})</code></span><br>
        <span style='color: gray; font-size: 0.9em;'>{user_email}</span><br>
        <span style='color: #666;'>👯 Partner: {partner_visning}</span>
    </div>
    """,
    unsafe_allow_html=True
)

# === Automatisk visning av partnerforespørsel hvis finnes
partner_check = supabase.table("partner_requests").select("id")\
    .eq("to_user_id", user_id).eq("status", "venter").execute()

if partner_check.data and "vis_side" not in st.session_state:
    st.session_state["vis_side"] = "godkjenn_partner"

# === Sidevisning ===
if "vis_side" not in st.session_state:
    st.session_state["vis_side"] = "hjem"

# === Modulrouter ===
side = st.session_state["vis_side"]

if side in ["hjem"]:
    show_homepage_modules(partner_id)


elif side in ["dagens_plan", "rerun_dagens_plan"]:
    from components.dagens_plan import dagens_plan
    dagens_plan()

elif side == "admin":
    from components.admin import admin
    admin()

elif side == "treningsoversikt":
    from components.vis_treningsoversikt import vis_treningsoversikt
    vis_treningsoversikt(user_id, partner_id)

elif side == "velg_partner":
    from components.velg_partner import velg_partner
    velg_partner()

elif side == "velg_okt":
    from components.velg_okt import velg_okt
    velg_okt()

elif side == "innstillinger":
    st.subheader("⚙️ Innstillinger")

    col1, col2 = st.columns(2)

    with col1:
        with st.expander("👤 Min profil", expanded=False):
            vis_redigerbar_profil()

    with col2:
        with st.expander("👥 Velg partner", expanded=False):
            from components.velg_partner import velg_partner
            velg_partner()

    # Klar for flere moduler:
    # with col1:
    #     with st.expander("🔔 Varsler", expanded=False):
    #         vis_varsler()




elif side == "invitasjoner":
    vis_invitasjoner()

elif side == "godkjenn_partner":
    from components.godkjenn_partner import godkjenn_partner
    godkjenn_partner()

# === Footer ===
show_footer_menu()
