import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai

# Sayfa Yapılandırması
st.set_page_config(page_title="Ders Asistanı", layout="wide")
st.title("🎓 Yapay Zeka Ders Asistanı")

# Yan Panel (API Key)
with st.sidebar:
    api_key = st.text_input("Gemini API Key Giriniz:", type="password").strip()
    st.info("API Key'inizi Google AI Studio'dan alabilirsiniz.")

# Ana Ekran Giriş
video_url = st.text_input("YouTube Video Linkini Yapıştırın:").strip()

if st.button("Analiz Et"):
    if not api_key:
        st.error("Lütfen önce API Key giriniz!")
    elif not video_url:
        st.error("Lütfen bir video linki giriniz!")
    else:
        try:
            # Video ID Ayıklama
            if "v=" in video_url:
                v_id = video_url.split("v=")[1].split("&")[0]
            elif "youtu.be/" in video_url:
                v_id = video_url.split("/")[-1].split("?")[0]
            else:
                v_id = video_url

            with st.spinner("Video inceleniyor ve notlar hazırlanıyor..."):
                # Gelişmiş Altyazı Çekme Sistemi
                try:
                    # Önce Türkçe ve İngilizce dillerini dene (Orijinal ve Otomatik dahil)
                    transcript = YouTubeTranscriptApi.get_transcript(v_id, languages=['tr', 'en', 'tr-orig', 'en-orig'])
                except:
                    # Eğer bulamazsa, mevcut tüm altyazıları listele ve uygun olanı çek
                    transcript_list = YouTubeTranscriptApi.list_transcripts(v_id)
                    # Bulabildiği ilk Türkçe veya İngilizce altyazıyı (otomatik çeviri dahil) getirir
                    transcript = transcript_list.find_transcript(['tr', 'en']).fetch()

                full_text = " ".join([t['text'] for t in transcript])
                
                # Gemini Yapılandırması
                genai.configure(api_key=
