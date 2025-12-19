import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai

# 1. Sayfa Konfigürasyonu
st.set_page_config(page_title="AI Ders Asistanı", page_icon="📖", layout="centered")

# 2. Arayüz Tasarımı (CSS)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 8px; background-color: #4CAF50; color: white; font-weight: bold; }
    .stTextInput>div>div>input { border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎓 Yapay Zeka Ders Asistanı")
st.write("YouTube videolarını dakikalar içinde kapsamlı ders notlarına dönüştürün.")

# 3. Yan Panel Ayarları
with st.sidebar:
    st.header("🔑 Yapılandırma")
    api_key = st.text_input("Gemini API Key:", type="password", placeholder="AIza...").strip()
    st.markdown("---")
    st.markdown("### Nasıl Kullanılır?")
    st.write("1. API Key'inizi girin.\n2. Video linkini yapıştırın.\n3. Analiz et butonuna basın.")

# 4. Ana Uygulama Mantığı
video_url = st.text_input("YouTube Video URL:", placeholder="https://www.youtube.com/watch?v=...").strip()

if st.button("Ders Notu Oluştur"):
    if not api_key:
        st.error("Lütfen bir Gemini API Key giriniz.")
    elif not video_url:
        st.error("Lütfen geçerli bir YouTube video linki giriniz.")
    else:
        try:
            # Video ID Ayıklama
            if "v=" in video_url:
                v_id = video_url.split("v=")[1].split("&")[0]
            elif "youtu.be/" in video_url:
                v_id = video_url.split("/")[-1].split("?")[0]
            else:
                v_id = video_url

            with st.spinner("⏳ Video içeriği okunuyor (bu işlem videonun uzunluğuna göre 10-30 saniye sürebilir)..."):
                # Altyazı Çekme İşlemi (Çoklu Dil Desteği ile)
                try:
                    t_list = YouTubeTranscriptApi.list_transcripts(v_id)
                    # Önce Türkçe, yoksa İngilizce, o da yoksa ilk dili Türkçe'ye çevirerek al
                    try:
                        transcript = t_list.find_transcript(['tr']).fetch()
                    except:
                        try:
                            transcript = t_list.find_transcript(['en']).fetch()
                        except:
                            transcript = t_list.find_one_of_variable_langs(['en', 'tr', 'de', 'fr']).translate('tr').fetch()
                    
                    full_text = " ".join([t['text'] for t in transcript])
                    
                except Exception as e:
                    st.error(f"❌ Altyazı alınamadı. Video sahibi altyazıları kapatmış olabilir. Hata: {str(e)}")
                    st.stop()

                # Gemini ile Analiz
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                Sen profesyonel bir not tutma asistanısın. Aşağıdaki video transkriptini analiz et ve:
                - Konuyu açıklayan bir başlık koy.
                - Videoyu 3-5 ana başlık altında detaylandır.
                - Önemli kavramları kalın yazıyla vurgula.
                - En sonda öğrenci için 3 adet 'Biliyor muydunuz?' sorusu hazırla.
                
                Transkript:
                {full_text[:15000]}
                """
                
                response = model.generate_content(prompt)
                
                # Sonuçları Göster
                st.success("✨ Ders notlarınız hazır!")
                st.markdown("---")
                st.markdown(response.text)
                
                # İndirme Butonu
                st.download_button("📥 Notları TXT Olarak İndir", response.text, file_name="ders_notu.txt")

        except Exception as e:
            st.error(f"🚨 Beklenmedik bir hata: {str(e)}")
