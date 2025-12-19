import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai

# Sayfa Yapılandırması
st.set_page_config(page_title="Akıllı Ders Asistanı", page_icon="🎓", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #007BFF; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎓 Akıllı Ders Asistanı")

with st.sidebar:
    st.header("🔑 Bağlantı Ayarları")
    api_key = st.text_input("Gemini API Key:", type="password").strip()
    st.info("💡 Not: Altyazıları (CC) aktif olan videoları kullanın.")

video_url = st.text_input("YouTube Video Linkini Girin:").strip()

def get_video_id(url):
    if "v=" in url: return url.split("v=")[1].split("&")[0]
    if "youtu.be/" in url: return url.split("/")[-1].split("?")[0]
    return url

if st.button("Analiz Et ve Ders Notu Hazırla"):
    if not api_key:
        st.error("Lütfen bir API anahtarı giriniz.")
    elif not video_url:
        st.error("Lütfen bir video linki giriniz.")
    else:
        v_id = get_video_id(video_url)
        
        try:
            with st.spinner("⏳ Altyazılar aranıyor..."):
                # GÜÇLENDİRİLMİŞ ALTYAZI ÇEKME
                full_text = ""
                try:
                    # 1. Aşama: Tüm transkript listesini al
                    transcript_list = YouTubeTranscriptApi.list_transcripts(v_id)
                    
                    # 2. Aşama: Önce Türkçe, sonra İngilizce, sonra herhangi biri
                    try:
                        transcript = transcript_list.find_transcript(['tr', 'en']).fetch()
                    except:
                        # Eğer yukarıdaki diller yoksa, mevcut olan İLK dili bul ve Türkçe'ye çevir
                        # Bu en sağlam yöntemdir:
                        first_transcript = next(iter(transcript_list._manually_created_transcripts.values() if transcript_list._manually_created_transcripts else transcript_list._generated_transcripts.values()))
                        transcript = first_transcript.translate('tr').fetch()
                    
                    full_text = " ".join([i['text'] for i in transcript])
                
                except Exception as e:
                    # Hata mesajını daha detaylı gösterelim ki sorunu anlayalım
                    st.error(f"❌ Altyazı Erişim Hatası: {str(e)}")
                    st.stop()

            with st.spinner("🧠 Yapay zeka notları hazırlıyor..."):
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"Aşağıdaki matematik dersi transkriptini, önemli formülleri ve mantıksal adımları vurgulayarak Türkçe bir ders notuna dönüştür:\n\n{full_text[:15000]}"
                
                response = model.generate_content(prompt)
                st.success("✨ İşlem Başarıyla Tamamlandı!")
                st.markdown("---")
                st.markdown(response.text)
                st.download_button("📥 Ders Notunu İndir", response.text, file_name="ders_notu.txt")

        except Exception as e:
            st.error(f"🚨 Genel Hata: {str(e)}")

