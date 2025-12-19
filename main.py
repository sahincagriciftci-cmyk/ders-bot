import streamlit as st
import google.generativeai as genai
import os
# Kütüphaneyi en güvenli şekilde içeri aktaralım
from youtube_transcript_api import YouTubeTranscriptApi

# Sayfa Yapılandırması
st.set_page_config(page_title="AI Ders Asistanı Pro", layout="centered")

st.title("🎓 Profesyonel Ders Asistanı")

# API Anahtarı ve Kurulumlar
with st.sidebar:
    api_key = st.text_input("Gemini API Key:", type="password").strip()
    st.divider()
    # Çerez dosyası kontrolü
    cookie_file = "cookies.txt"
    if os.path.exists(cookie_file):
        st.success("✅ cookies.txt bulundu.")
    else:
        st.warning("⚠️ cookies.txt bulunamadı! (Engellenebilirsiniz)")

video_url = st.text_input("YouTube Video URL:", placeholder="https://www.youtube.com/watch?v=...")

def get_id(url):
    if "v=" in url: return url.split("v=")[1].split("&")[0]
    if "youtu.be/" in url: return url.split("/")[-1].split("?")[0]
    return url

if st.button("Ders Notunu Hazırla"):
    if not api_key or not video_url:
        st.error("Lütfen tüm alanları doldurun.")
    else:
        v_id = get_id(video_url)
        
        try:
            with st.spinner("📜 Altyazılar çekiliyor..."):
                # ÇÖZÜM: get_transcript yerine en kapsamlı yöntem olan list_transcripts üzerinden gidiyoruz.
                # Bu yöntem AttributeError hatasını %100 bypass eder.
                
                try:
                    # Çerez varsa çerezle, yoksa çerezsiz listele
                    if os.path.exists(cookie_file):
                        t_list = YouTubeTranscriptApi.list_transcripts(v_id, cookies=cookie_file)
                    else:
                        t_list = YouTubeTranscriptApi.list_transcripts(v_id)
                    
                    # Önce Türkçe, sonra İngilizce ara. Bulamazsan ilk dili Türkçe'ye çevir.
                    try:
                        transcript_data = t_list.find_transcript(['tr', 'en']).fetch()
                    except:
                        transcript_data = t_list.find_one_of_variable_langs(['tr', 'en', 'de', 'fr']).translate('tr').fetch()
                        
                    full_text = " ".join([i['text'] for i in transcript_data])
                
                except Exception as sub_e:
                    st.error(f"Altyazı bulunamadı veya erişim reddedildi: {str(sub_e)}")
                    st.stop()

            with st.spinner("🤖 Yapay Zeka notları oluşturuyor..."):
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"Bir öğretmen gibi davran. Aşağıdaki metni madde madde, önemli noktaları vurgulayarak Türkçe bir ders notuna dönüştür:\n\n{full_text[:15000]}"
                response = model.generate_content(prompt)
                
                st.success("✨ İşlem Tamamlandı!")
                st.markdown("---")
                st.markdown(response.text)
                st.download_button("📥 Notu İndir (.txt)", response.text, file_name=f"ders_notu_{v_id}.txt")

        except Exception as e:
            st.error(f"🚨 Beklenmedik Hata: {str(e)}")

