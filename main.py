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
            # Video ID'yi her iki link formatı için de alalım
            if "v=" in video_url:
                v_id = video_url.split("v=")[1].split("&")[0]
            else:
                v_id = video_url.split("/")[-1]

            with st.spinner("Video inceleniyor..."):
                # Kütüphaneyi doğrudan çağırıyoruz
                transcript = YouTubeTranscriptApi.get_transcript(v_id, languages=['tr', 'en'])
                full_text = " ".join([t['text'] for t in transcript])
                
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"Aşağıdaki metni detaylı ders notuna dönüştür:\n\n{full_text[:15000]}"
                response = model.generate_content(prompt)
                
                st.success("İşlem Başarılı!")
                st.markdown(response.text)
                
        except Exception as e:
            st.error(f"Hata oluştu: {e}")
