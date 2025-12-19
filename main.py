import streamlit as st
import youtube_transcript_api
from youtube_transcript_api import YouTubeTranscriptApi as yta
import google.generativeai as genai

st.set_page_config(page_title="Ders Asistanı", layout="wide")

st.title("🎓 Yapay Zeka Ders Asistanı")

with st.sidebar:
    api_key = st.text_input("Gemini API Key Giriniz:", type="password")
    st.info("API Key'inizi Google AI Studio'dan alabilirsiniz.")

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
                # Bu sefer doğrudan ana modül üzerinden çağırıyoruz:
                transcript_list = yta.get_transcript(video_id, languages=['tr', 'en', 'tr-orig', 'en-orig'])
                text = " ".join([t['text'] for t in transcript_list])
                
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"Aşağıdaki video içeriğini profesyonel bir ders notuna dönüştür:\n\n{text[:15000]}"
                response = model.generate_content(prompt)
                
                st.success("Analiz Tamamlandı!")
                st.markdown("---")
                st.markdown(response.text)
                
        except Exception as e:
            st.error(f"Hata detayı: {e}")
            st.info("Eğer 'No transcript found' diyorsa videoda altyazı yoktur.")
