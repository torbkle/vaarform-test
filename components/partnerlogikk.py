from components.auth import supabase

def hent_partner_id(bruker_id):
    respons = supabase.table("partners").select("id, user_a_id, user_b_id")\
        .or_(f"user_a_id.eq.{bruker_id},user_b_id.eq.{bruker_id}")\
        .eq("status", "aktiv").execute()

    if respons.data:
        kobling = respons.data[0]
        return kobling["user_b_id"] if kobling["user_a_id"] == bruker_id else kobling["user_a_id"]
    return None

def hent_partnerinfo(partner_id):
    if not partner_id:
        return None

    respons = supabase.table("brukerinfo").select("fornavn", "etternavn", "brukernavn")\
        .eq("bruker_id", partner_id).execute()

    if respons.data:
        data = respons.data[0]
        fullt_navn = f"{data.get('fornavn', '')} {data.get('etternavn', '')}".strip()
        brukernavn = data.get("brukernavn", "")
        return {"navn": fullt_navn, "brukernavn": brukernavn}
    return None
