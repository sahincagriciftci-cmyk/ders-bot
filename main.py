import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai

# Sayfa Yapılandırması
st.set_page_config(page_title="Ders Asistanı", layout="wide")

st.title("🎓 Yapay Zeka Ders Asistanı")

# Yan Panel (API Key)
with st.sidebar:
    api_key = st.text_input("Gemini API Key Giriniz:", type="password")
    st.info("API Key'inizi Google AI Studio'dan alabilirsiniz.")

# Ana Ekran Giriş
video_url = st.text_input("YouTube Video Linkini Yapıştırın:")

if st.button("Analiz Et"):
    if not api_key:
        st.error("Lütfen önce API Key giriniz!")
    elif not video_url:
        st.error("Lütfen bir video linki giriniz!")
    else:
        try:
            # Video ID Ayıklama
            if "v=" in video_url:
                video_id = video_url.split("v=")[1].split("&")[0]
            elif "youtu.be/" in video_url:
                video_id = video_url.split("/")[-1]
            else:
                video_id = video_url

            with st.spinner("Video okunuyor ve analiz ediliyor..."):
                # Altyazı çekme - Tüm ihtimalleri ekledik
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['tr', 'en', 'tr-orig', 'en-orig'])
                text = " ".join([t['text'] for t in transcript_list])
                
                # Yapay Zeka Yapılandırması
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # İstek (Prompt)
                prompt = f"""
                Aşağıdaki video içeriğini profesyonel bir ders notuna dönüştür:
                1. Konu özeti ve ana fikir.
                2. Önemli kısımları madde madde açıkla.
                3. Varsa önemli kavramları vurgula.
                
                Video Metni:
                {text[:15000]}
                """
                
                response = model.generate_content(prompt)
                
                st.success("Analiz Tamamlandı!")
                st.markdown("---")
                st.markdown(response.text)
                
        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")
            st.info("İpucu: Videoda altyazıların (CC) açık olduğundan ve linkin doğru olduğundan emin olun.")
