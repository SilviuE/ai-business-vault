import streamlit as st
import urllib.parse
import requests
import os
from youtube_transcript_api import YouTubeTranscriptApi

st.set_page_config(page_title="AI Business Vault", page_icon="⚡", layout="wide")

st.title("⚡ AI Business Vault")
st.markdown("Transformă conținutul pasiv în strategii de acțiune și monetizare pentru portofoliul tău.")

# Gestionarea cheii API
with st.sidebar:
    st.header("⚙️ Configurare AI")
    groq_api_key = st.text_input("Introdu cheia API Groq:", type="password")
    if not groq_api_key and "GROQ_API_KEY" in os.environ:
        groq_api_key = os.environ["GROQ_API_KEY"]

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
url_input = st.text_input("Introdu link-ul de YouTube:")

def extrage_id_youtube(url):
    parsed_url = urllib.parse.urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed_url.path == '/watch':
            p = urllib.parse.parse_qs(parsed_url.query)
            return p.get('v', [None])[0]
    return None

def obtine_transcriere(video_id):
    try:
        # Preia transcrierea în engleză sau română
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'ro'])
        text = " ".join([t['text'] for t in transcript])
        return text
    except Exception as e:
        return None

def genereaza_analiza_groq(api_key, text_video, proiecte):
    prompt = f"""Ești un consultant de business. Am extras următorul text dintr-un videoclip: 
    "{text_video[:15000]}"...
    
    Te rog să faci o analiză structurată pentru mine. Răspunde exclusiv în limba română folosind formatare Markdown, având următoarea structură:
    
    ### 1. Extragerea Ideilor Principale
    - Rezumă în 2-3 fraze care este esența și direcția strategică din acest videoclip.
    
    ### 2. Mapare pe Proiectele Active
    Pentru fiecare dintre următoarele proiecte pe care le dețin: {proiecte}
    - Analizează strict cum se pot aplica ideile din videoclip (dacă se pot aplica) pentru a crește sau monetiza acel proiect specific. Nu inventa dacă nu are legătură, adaptează la context.
    
    ### 3. Recomandare de Acțiune Imediată
    - O idee clară de executat azi pornind de la informația primită.
    """
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama3-8b-8192", 
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    
    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return f"Eroare API Groq: {response.text}"

if st.button("Generează Raport de Business", type="primary"):
    if not url_input:
        st.error("Te rog să introduci un link valid.")
    elif not groq_api_key:
        st.error("Te rog să introduci cheia API Groq în meniul din stânga.")
    else:
        video_id = extrage_id_youtube(url_input)
        if not video_id:
            st.error("Link-ul de YouTube nu este valid.")
        else:
            with st.spinner("Se preia subtitrarea din YouTube (poate dura câteva secunde)..."):
                transcriere = obtine_transcriere(video_id)
                
            if not transcriere:
                st.error("Nu am putut prelua transcrierea. Videoclipul s-ar putea să nu aibă subtitrări generate (CC) sau este restricționat.")
            else:
                with st.spinner("Inteligența Artificială gândește și generează raportul..."):
                    proiecte_active = [p['nume'] + " (" + p['domeniu'] + ")" for p in st.session_state.proiecte if p["status"] == "Activ"]
                    analiza = genereaza_analiza_groq(groq_api_key, transcriere, proiecte_active)
                    
                    st.success("Analiza a fost generată cu succes!")
                    st.markdown(analiza)
