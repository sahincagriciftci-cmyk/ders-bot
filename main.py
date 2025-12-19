import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
import os

# Sayfa Yapılandırması
st.set_page_config(page_title="AI Ders Notu Pro", page_icon="🎓")

st.title("🚀 Kesintisiz AI Ders Asistanı")
st.markdown("YouTube bot engelini aşmak için **Çerez Desteği** aktif.")

# Yan Panel
with st.sidebar:
    api_key = st.text_input("Gemini API Key:", type="password").strip()
    if os.path.exists('cookies.txt'):
        st.success("✅ cookies.txt dosyası algılandı! YouTube erişimi güçlendirildi.")
    else:
        st.warning("⚠️ cookies.txt bulunamadı. Standart erişim denenecek (Engellenebilir).")

# Giriş Alanı
video_url = st.text_input("YouTube Video URL:", placeholder="https://www.youtube.com/watch?v=...")

def extract_id(url):
    if "v=" in url: return url.split("v=")[1].split("&")[0]
    if "youtu.be/" in url: return url.split("/")[-1].split("?")[0]
    return url

if st.button("Analizi Başlat"):
    if not api_key or not video_url:
        st.error("Lütfen tüm alanları doldurun.")
    else:
        v_id = extract_id(video_url)
        
        try:
            with st.spinner("YouTube üzerinden veri çekiliyor..."):
                # ÇEREZ DESTEKLİ ERİŞİM MANTIĞI
                if os.path.exists('cookies.txt'):
                    # Çerez dosyası varsa onu kullan (Bot engelini aşan en güçlü yöntem)
                    transcript = YouTubeTranscriptApi.get_transcript(v_id, languages=['tr', 'en'], cookies='cookies.txt')
                else:
                    # Çerez yoksa standart dene
                    transcript = YouTubeTranscriptApi.get_transcript(v_id, languages=['tr', 'en'])
                
                full_text = " ".join([t['text'] for t in transcript])

            with st.spinner("Gemini ders notunu hazırlıyor..."):
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""Bir matematik öğretmeni gibi davran. 
                Aşağıdaki transkripti kullanarak detaylı, adım adım açıklayan bir ders notu oluştur.
                Önemli formülleri ve çözüm mantığını vurgula:\n\n{full_text[:15000]}"""
                
                response = model.generate_content(prompt)
                
                st.success("✨ Notlar Başarıyla Hazırlandı!")
                st.markdown("---")
                st.markdown(response.text)
                st.download_button("📥 Notu İndir", response.text, file_name="ders_notu.txt")

        except Exception as e:
            st.error(f"Erişim Başarısız: {str(e)}")
            st.info("💡 Çözüm: cookies.txt dosyasının güncel olduğundan emin olun veya Streamlit uygulamasını 'Reboot' yapın.")
