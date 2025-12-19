import streamlit as st
import youtube_transcript_api # Modülü doğrudan içeri aktar
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
import os

# Sayfa Yapılandırması
st.set_page_config(page_title="AI Ders Notu Pro", page_icon="🎓")

st.title("🚀 Kesintisiz AI Ders Asistanı")
st.markdown("YouTube erişim protokolü güncellendi.")

# Yan Panel
with st.sidebar:
    st.header("⚙️ Ayarlar")
    api_key = st.text_input("Gemini API Key:", type="password").strip()
    
    # Çerez kontrolü
    cookie_path = 'cookies.txt'
    if os.path.exists(cookie_path):
        st.success("✅ cookies.txt aktif.")
    else:
        st.warning("⚠️ cookies.txt bulunamadı.")

video_url = st.text_input("YouTube URL:", placeholder="https://www.youtube.com/watch?v=...")

def extract_id(url):
    if "v=" in url: return url.split("v=")[1].split("&")[0]
    if "youtu.be/" in url: return url.split("/")[-1].split("?")[0]
    return url

if st.button("Analizi Başlat"):
    if not api_key or not video_url:
        st.error("Eksik bilgi!")
    else:
        v_id = extract_id(video_url)
        
        try:
            with st.spinner("YouTube verisi alınıyor..."):
                # HATAYI ÇÖZEN ÇAĞRI YÖNTEMİ
                # Sınıf üzerinden değil, modül üzerinden çağırmayı deniyoruz
                if os.path.exists(cookie_path):
                    # Çerez dosyası varsa
                    transcript = YouTubeTranscriptApi.get_transcript(v_id, languages=['tr', 'en'], cookies=cookie_path)
                else:
                    # Çerez yoksa
                    transcript = YouTubeTranscriptApi.get_transcript(v_id, languages=['tr', 'en'])
                
                full_text = " ".join([t['text'] for t in transcript])

            with st.spinner("AI Notları Hazırlıyor..."):
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"Aşağıdaki transkripti profesyonel bir ders notuna dönüştür:\n\n{full_text[:15000]}"
                response = model.generate_content(prompt)
                
                st.success("✅ Tamamlandı!")
                st.markdown("---")
                st.markdown(response.text)
                st.download_button("📥 Notu İndir", response.text, file_name="ders_notu.txt")

        except Exception as e:
            st.error(f"Erişim Hatası: {str(e)}")
            st.info("Eğer 'cookies.txt' kullanıyorsanız, dosya formatının doğru olduğundan (Netscape formatı) emin olun.")

