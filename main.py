
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
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
            video_id = video_url.split("v=")[1].split("&")[0]
            
            with st.spinner("Video okunuyor ve analiz ediliyor..."):
                # DOĞRU KULLANIM BURASI:
               transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['tr', 'en', 'tr-orig', 'en-orig'])
                text = " ".join([t['text'] for t in transcript_list])
                
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-pro')
                
                prompt = f"Aşağıdaki video içeriğini detaylı bir ders notuna dönüştür, önemli yerleri vurgula:\n\n{text}"
                response = model.generate_content(prompt)
                
                st.success("Analiz Tamamlandı!")
                st.markdown(response.text)
                
        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")

