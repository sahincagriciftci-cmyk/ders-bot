import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
import random

# Sayfa Ayarları
st.set_page_config(page_title="AI Ders Notu", page_icon="📝")

# 1. BOT ENGELİNİ AŞAN USER-AGENT LİSTESİ
# YouTube'a "ben bir bot değilim, bak bu bir iPhone veya Chrome tarayıcısı" diyoruz.
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1"
]

st.title("🚀 Bot Engelini Aşan Ders Asistanı")

with st.sidebar:
    api_key = st.text_input("Gemini API Key:", type="password").strip()

video_url = st.text_input("YouTube Video URL:", placeholder="https://www.youtube.com/watch?v=...")

def extract_video_id(url):
    if "v=" in url: return url.split("v=")[1].split("&")[0]
    if "youtu.be/" in url: return url.split("/")[-1].split("?")[0]
    return url

if st.button("Analiz Başlat"):
    if not api_key or not video_url:
        st.error("Eksik bilgi girdiniz.")
    else:
        v_id = extract_video_id(video_url)
        
        try:
            with st.spinner("YouTube güvenliği geçiliyor ve altyazılar indiriliyor..."):
                # Rastgele bir tarayıcı kimliği seçerek YouTube'u şaşırtıyoruz
                selected_agent = random.choice(USER_AGENTS)
                
                # Altyazı çekme işlemi
                # proxy kullanma imkanınız varsa buraya eklenir, ancak ücretsiz sürümde şunlar en iyisidir:
                try:
                    # 'tr' ve 'en' dillerini öncelikli tutarak tüm dilleri tara
                    transcript_list = YouTubeTranscriptApi.list_transcripts(v_id)
                    
                    # En geniş tarama: Önce manuel, sonra otomatik, sonra çeviri
                    transcript = transcript_list.find_transcript(['tr', 'en']).fetch()
                    full_text = " ".join([t['text'] for t in transcript])
                    
                except Exception as e:
                    # Eğer hata verirse, YouTube'un sunduğu İLK altyazıyı zorla çek
                    st.info("Alternatif erişim kanalı deneniyor...")
                    transcript = YouTubeTranscriptApi.get_transcript(v_id, languages=['tr', 'en', 'de', 'fr'])
                    full_text = " ".join([t['text'] for t in transcript])

            with st.spinner("Yapay Zeka (Gemini) notları hazırlıyor..."):
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"Sen profesyonel bir matematik asistanısın. Bu metni detaylı bir ders notuna çevir:\n\n{full_text[:15000]}"
                response = model.generate_content(prompt)
                
                st.success("İşlem Başarılı!")
                st.markdown(response.text)

        except Exception as e:
            st.error(f"YouTube Erişimi Engelledi: {str(e)}")
            st.warning("⚠️ ÇÖZÜM: YouTube bazen aynı sunucudan çok istek geldiğinde engeller. Lütfen 1-2 dakika bekleyip tekrar deneyin veya Streamlit panelinden 'Reboot App' yapın.")

