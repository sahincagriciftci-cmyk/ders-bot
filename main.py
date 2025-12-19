import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai

# Sayfa Konfigürasyonu
st.set_page_config(page_title="Akıllı Ders Asistanı", layout="centered")

st.title("🎓 Akıllı Ders Asistanı")

with st.sidebar:
    api_key = st.text_input("Gemini API Key:", type="password").strip()

video_url = st.text_input("YouTube Linki:", placeholder="https://www.youtube.com/watch?v=WUvTyaaN2as")

if st.button("Analiz Et"):
    if not api_key or not video_url:
        st.warning("Lütfen API Key ve Link giriniz.")
    else:
        try:
            # Video ID Ayıklama
            if "v=" in video_url:
                v_id = video_url.split("v=")[1].split("&")[0]
            elif "youtu.be/" in video_url:
                v_id = video_url.split("/")[-1].split("?")[0]
            else:
                v_id = video_url

            with st.spinner("Altyazılar çekiliyor..."):
                # EN BASİT VE GÜVENLİ YÖNTEM
                # Önce listeyi alıp sonra içinden seçmek yerine doğrudan get_transcript deneyelim
                try:
                    # Bu video (WUvTyaaN2as) İngilizce olduğu için önce 'en' deniyoruz
                    transcript = YouTubeTranscriptApi.get_transcript(v_id, languages=['en', 'tr'])
                    full_text = " ".join([t['text'] for t in transcript])
                except Exception as e:
                    # Eğer doğrudan çekemezse, tüm dilleri tara
                    t_list = YouTubeTranscriptApi.list_transcripts(v_id)
                    # Mevcut olan ilk altyazıyı al (otomatik veya manuel fark etmez)
                    t_obj = t_list.find_transcript(['en', 'tr'])
                    transcript = t_obj.fetch()
                    full_text = " ".join([t['text'] for t in transcript])

            with st.spinner("AI Analiz Ediyor..."):
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Promptu Türkçeleştirdik
                prompt = f"""Aşağıdaki matematik dersi içeriğini profesyonel ve Türkçe bir ders notuna dönüştür. 
                Önemli kısımları madde madde açıkla: \n\n {full_text[:15000]}"""
                
                response = model.generate_content(prompt)
                st.success("Analiz Tamamlandı!")
                st.markdown(response.text)

        except Exception as e:
            st.error(f"Erişim Hatası: YouTube bu videonun altyazılarını botlara kapatmış olabilir. Hata: {str(e)}")
            st.info("İpucu: Sayfayı yenileyip (F5) 10 saniye sonra tekrar deneyin. Bazen YouTube geçici engeller koyar.")

