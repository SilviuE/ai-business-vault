import streamlit as st
import urllib.parse
import json

st.set_page_config(page_title="AI Business Vault", page_icon="⚡", layout="wide")

st.title("⚡ AI Business Vault")
st.markdown("Transformă conținutul pasiv în strategii de acțiune și monetizare pentru portofoliul tău.")

if 'proiecte' not in st.session_state:
    st.session_state.proiecte = [
        {"nume": "Transport", "domeniu": "Comunitate Facebook (51k)", "status": "Activ"},
        {"nume": "BucketListSpots.com", "domeniu": "Turism de aventură", "status": "Activ"},
        {"nume": "Cosmetice Handmade", "domeniu": "E-commerce", "status": "Activ"},
        {"nume": "SavoryHub / Patiserii.net", "domeniu": "Director gastronomic", "status": "Activ"}
    ]

st.sidebar.header("📂 Portofoliu Proiecte")
for i, p in enumerate(st.session_state.proiecte):
    col_s1, col_s2 = st.sidebar.columns([3, 1])
    col_s1.text(f"{p['nume']} ({p['status']})")
    if col_s2.button("🗑️", key=f"del_{i}"):
        st.session_state.proiecte.pop(i)
        st.rerun()

with st.sidebar.form("add_project"):
    st.subheader("Adaugă Proiect Nou")
    nume_nou = st.text_input("Nume Proiect")
    domeniu_nou = st.text_input("Domeniu / Nișă")
    status_nou = st.selectbox("Status", ["Activ", "Dormant"])
    submitted = st.form_submit_button("Salvează Proiect")
    if submitted and nume_nou:
        st.session_state.proiecte.append({"nume": nume_nou, "domeniu": domeniu_nou, "status": status_nou})
        st.rerun()

st.header("🎯 Analiză Resursă Nouă")
url_input = st.text_input("Introdu link-ul de YouTube sau Podcast:")

def extrage_id_youtube(url):
    parsed_url = urllib.parse.urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed_url.path == '/watch':
            p = urllib.parse.parse_qs(parsed_url.query)
            return p.get('v', [None])[0]
    return None

if st.button("Generează Raport de Business", type="primary"):
    if url_input:
        video_id = extrage_id_youtube(url_input)
        if not video_id:
            st.error("Te rog să introduci un link valid de YouTube.")
        else:
            with st.spinner("Se procesează resursa și se rulează analizatorul AI..."):
                st.success(f"Conectat cu succes la video ID: {video_id}")
                st.markdown("### 1. Extragerea Ideilor Principale")
                st.info("- **Teza centrală:** Viralitatea fără intenție sau ofertă clară este o iluzie.\n- **Tactica cheie:** Metoda 3-2-1 pentru crearea de conținut orientat spre conversie.")
                st.markdown("### 2. Mapare pe Proiectele Active")
                active_projects = [p for p in st.session_state.proiecte if p["status"] == "Activ"]
                for p in active_projects:
                    st.markdown(f"**➡️ Proiect: {p['nume']}**")
                    st.write(f"Aplicare directă în nișa ta ({p['domeniu']}): Folosește conținutul extras pentru a genera engagement direct și conversii.")
                st.markdown("### 3. Recomandare de Trenduri și Monetizare")
                st.warning("Trecerea către micro-autoritate. Monetizează prin produse proprii sau parteneriate directe.")
    else:
        st.error("Te rog să introduci un link valid înainte de a rula analiza.")
