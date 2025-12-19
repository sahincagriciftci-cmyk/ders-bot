import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai

# Sayfa yapılandırması
st.set_page_config(page_title="Yapay Zeka Ders Asistanı", page_icon="🎓")

st.title("🎓 Yapay Zeka Ders Notu Hazırlayıcı")
st.markdown("---")

# Yan panel ayarları
st.sidebar.header("Ayarlar")
api_key = st.sidebar.text_input("Gemini API Key Giriniz:", type="password")
st.sidebar.markdown("[Buradan ücretsiz API anahtarı alabilirsin](https://aistudio.google.com/app/apikey)")

# Ana ekran
video_url = st.text_input("YouTube Video Linkini Buraya Yapıştırın:")

if st.button("Analiz Et ve Notları Çıkar"):
    if not api_key:
        st.warning("Lütfen sol tarafa API anahtarınızı girin.")
    elif not video_url:
        st.warning("Lütfen bir video linki girin.")
    else:
        try:
            with st.spinner("Video inceleniyor..."):
                # Video ID ayıklama
                video_id = video_url.split("v=")[1].split("&")[0] if "v=" in video_url else video_url.split("/")[-1]
                
                # Altyazıları çekme
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['tr', 'en'])
                full_text = " ".join([t['text'] for t in transcript_list])
                
                # Yapay Zekaya Gönderme
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                Sen profesyonel bir eğitim asistanısın. Aşağıdaki video transkriptini analiz et:
                1. Konunun ana fikrini yaz.
                2. Önemli başlıkları ve altındaki detayları madde madde açıkla.
                3. Varsa önemli tarih, isim veya formülleri tablo yap.
                4. Öğrencinin konuyu pekiştirmesi için 3 tane soru sor.
                
                Metin: {full_text[:15000]}
                """
                
                response = model.generate_content(prompt)
                
                st.success("Analiz Tamamlandı!")
                st.markdown("### 📝 Ders Notların")
                st.write(response.text)
                
        except Exception as e:
            st.error(f"Hata: {str(e)}")
            st.info("İpucu: Videoda altyazı desteği olduğundan emin olun.")