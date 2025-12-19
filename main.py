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
                    transcript = YouTubeTranscriptApi.get_transcript(v_id, languages=['tr', 'en', 'tr-orig', 'en-orig'])
                except:
                    transcript_list = YouTubeTranscriptApi.list_transcripts(v_id)
                    transcript = transcript_list.find_transcript(['tr', 'en']).fetch()

                full_text = " ".join([t['text'] for t in transcript])
                
                # Gemini Yapılandırması
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                Aşağıdaki ders içeriğini kullanarak kapsamlı bir ders notu hazırla:
                1. Ana Başlık ve Özet
                2. Önemli Maddeler
                3. Varsa Kavramlar ve Açıklamaları
                4. Öğrenci için 3 adet çalışma sorusu.

                Video Metni:
                {full_text[:15000]}
                """
                
                response = model.generate_content(prompt)
                
                st.success("Tebrikler! Ders notun hazır.")
                st.markdown("---")
                st.markdown(response.text)
                
        except Exception as e:
            st.error(f"Hata oluştu: {e}")
            st.info("İpucu: Altyazıların açık olduğundan emin olun.")

