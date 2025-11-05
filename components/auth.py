import streamlit as st
from supabase import create_client, Client
from datetime import datetime

# === Supabase-klient ===
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# === Innlogging ===
def login(email, password):
    try:
        result = supabase.auth.sign_in_with_password({"email": email, "password": password})
        user = result.user
        st.session_state["user"] = user
        st.session_state["access_token"] = result.session.access_token
        st.session_state["refresh_token"] = result.session.refresh_token

        # Hent brukerdata
        bruker = supabase.table("brukere").select("*").eq("id", user.id).single().execute()
        st.session_state["bruker"] = bruker.data

        info = supabase.table("brukerinfo").select("*").eq("bruker_id", user.id).execute()
        st.session_state["brukerinfo"] = info.data[0] if info.data else None

        st.success(f"✅ Logget inn som {user.email}")
        return result
    except Exception as e:
        st.error(f"🚫 Innlogging feilet: {e}")
        return None

# === Registrering ===
def signup(email, password):
    try:
        # Registrer og logg inn
        supabase.auth.sign_up({"email": email, "password": password})
        result = supabase.auth.sign_in_with_password({"email": email, "password": password})
        user = result.user

        # Opprett bruker via RPC
        supabase.rpc("opprett_bruker", {"email": email}).execute()

        # Lagre tokens og brukerdata
        st.session_state["user"] = user
        st.session_state["access_token"] = result.session.access_token
        st.session_state["refresh_token"] = result.session.refresh_token

        bruker = supabase.table("brukere").select("*").eq("id", user.id).single().execute()
        st.session_state["bruker"] = bruker.data

        info = supabase.table("brukerinfo").select("*").eq("bruker_id", user.id).execute()
        st.session_state["brukerinfo"] = info.data[0] if info.data else None

        st.success("✅ Konto opprettet og logget inn!")
        return result
    except Exception as e:
        st.error(f"🚫 Registrering feilet: {e}")
        return None

# === Utlogging ===
def logout():
    try:
        supabase.auth.sign_out()
        for key in ["user", "bruker", "brukerinfo", "access_token", "refresh_token"]:
            st.session_state[key] = None
        st.success("👋 Du er logget ut.")
    except Exception as e:
        st.error(f"🚫 Utlogging feilet: {e}")

# === Automatisk innlogging ===
def refresh_session():
    if "refresh_token" in st.session_state and st.session_state["refresh_token"]:
        try:
            session = supabase.auth.refresh_session(st.session_state["refresh_token"])
            user = session.user
            st.session_state["user"] = user

            bruker = supabase.table("brukere").select("*").eq("id", user.id).single().execute()
            st.session_state["bruker"] = bruker.data

            info = supabase.table("brukerinfo").select("*").eq("bruker_id", user.id).execute()
            st.session_state["brukerinfo"] = info.data[0] if info.data else None

            st.success("🔁 Automatisk innlogging fullført")
            return True
        except Exception as e:
            st.warning(f"⚠️ Automatisk innlogging feilet: {e}")
            return False
    return False
