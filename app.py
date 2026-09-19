import streamlit as st
import urllib.parse
import requests
import os
from youtube_transcript_api import YouTubeTranscriptApi

st.set_page_config(page_title="AI Business Vault", page_icon="⚡", layout="wide")

st.title("⚡ AI Business Vault")
st.markdown("Transformă conținutul pasiv în strategii de acțiune și monetizare pentru portofoliul tău.")

# Gestionarea cheii API pentru Google Gemini
with st.sidebar:
    st.header("⚙️ Configurare AI")
    gemini_api_key = st.text_input("Introdu cheia API Google Gemini:", type="password")
    if not gemini_api_key and "GEMINI_API_KEY" in os.environ:
        gemini_api_key = os.environ["GEMINI_API_KEY"]

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

metoda_input = st.radio("Alege modalitatea de preluare:", ["Link YouTube", "Introducere Directă Text / Transcriere"])

text_de_analizat = ""
video_id = None

def extrage_id_youtube(url):
    parsed_url = urllib.parse.urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed_url.path == '/watch':
            p = urllib.parse.parse_qs(parsed_url.query)
            return p.get('v', [None])[0]
    return None

if metoda_input == "Link YouTube":
    url_input = st.text_input("Introdu link-ul de YouTube:")
    if url_input:
        video_id = extrage_id_youtube(url_input)
else:
    text_de_analizat = st.text_area("Lipește textul sau transcrierea videoclipului/podcastului aici:")

def genereaza_analiza_gemini(api_key, text_video, proiecte):
    prompt = f"""Ești un consultant de business. Am extras următorul conținut: 
    "{text_video[:15000]}"...
    
    Te rog să faci o analiză structurată pentru mine. Răspunde exclusiv în limba română folosind formatare Markdown, având următoarea structură:
    
    ### 1. Extragerea Ideilor Principale
    - Rezumă în 2-3 fraze care este esența și direcția strategică din acest conținut.
    
    ### 2. Mapare pe Proiectele Active
    Pentru fiecare dintre următoarele proiecte pe care le dețin: {proiecte}
    - Analizează strict cum se pot aplica ideile din material (dacă se pot aplica) pentru a crește sau monetiza acel proiect specific. Nu inventa dacă nu are legătură, adaptează la context.
    
    ### 3. Recomandare de Acțiune Imediată
    - O idee clară de executat azi pornind de la informația primită.
    """
    
    # Modelul cerut de server: gemini-3.6-flash
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={api_key}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        try:
            return data['candidates'][0]['content']['parts'][0]['text']
        except Exception:
            return f"Eroare la procesarea răspunsului Gemini: {data}"
    else:
        return f"Eroare API Gemini: {response.text}"

if st.button("Generează Raport de Business", type="primary"):
    if not gemini_api_key:
        st.error("Te rog să introduci cheia API Google Gemini în meniul din stânga.")
    else:
        continut_final = ""
        if metoda_input == "Link YouTube":
            if not video_id:
                st.error("Link-ul de YouTube nu este valid.")
            else:
                try:
                    with st.spinner("Se încearcă preluarea subtitrării..."):
                        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'ro'])
                        continut_final = " ".join([t['text'] for t in transcript])
                except Exception:
                    st.error("YouTube a restricționat preluarea automată pe acest server. Te rog să folosești opțiunea 'Introducere Directă Text / Transcriere'.")
        else:
            continut_final = text_de_analizat

        if continut_final:
            with st.spinner("Gemini analizează conținutul..."):
                proiecte_active = [p['nume'] + " (" + p['domeniu'] + ")" for p in st.session_state.proiecte if p["status"] == "Activ"]
                analiza = genereaza_analiza_gemini(gemini_api_key, continut_final, proiecte_active)
                
                st.success("Analiza a fost generată cu succes de Google Gemini!")
                st.markdown(analiza)
