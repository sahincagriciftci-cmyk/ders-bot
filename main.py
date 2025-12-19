import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai

# Sayfa Yapılandırması
st.set_page_config(page_title="Akıllı Ders Asistanı", page_icon="🎓", layout="centered")

# Görsel Düzenleme
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #007BFF; color: white; font-weight: bold; }
    .success-text { color: #28a745; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎓 Akıllı Ders Asistanı")
st.write("YouTube videolarını profesyonel ders notlarına ve özetlere dönüştürün.")

# Sol Panel Ayarları
with st.sidebar:
    st.header("🔑 Bağlantı Ayarları")
    api_key = st.text_input("Gemini API Key:", type="password", help="Google AI Studio'dan alınmalıdır.").strip()
    st.divider()
    st.info("💡 Not: Altyazıları (CC) aktif olan videoları kullanın.")

# Ana Giriş
video_url = st.text_input("YouTube Video Linkini Girin:", placeholder="https://www.youtube.com/watch?v=...").strip()

def get_video_id(url):
    if "v=" in url: return url.split("v=")[1].split("&")[0]
    if "youtu.be/" in url: return url.split("/")[-1].split("?")[0]
    return url

if st.button("Analiz Et ve Ders Notu Hazırla"):
    if not api_key:
        st.error("Lütfen bir API anahtarı giriniz.")
    elif not video_url:
        st.error("Lütfen bir video linki giriniz.")
    else:
        v_id = get_video_id(video_url)
        
        try:
            with st.spinner("⏳ Adım 1: Altyazılar çekiliyor..."):
                # HİBRİT ALTYAZI ÇEKME MANTIĞI
                # Bu yöntem AttributeError hatalarını engeller
                full_text = ""
                try:
                    # Önce mevcut transkriptleri listele (En sağlam yöntem)
                    proxy_list = YouTubeTranscriptApi.list_transcripts(v_id)
                    
                    # Tercih sırası: Türkçe Manuel -> Türkçe Otomatik -> İngilizce -> Otomatik Çeviri
                    try:
                        t = proxy_list.find_transcript(['tr']).fetch()
                    except:
                        try:
                            t = proxy_list.find_transcript(['en']).fetch()
                        except:
                            t = proxy_list.find_one_of_variable_langs(['en', 'tr', 'de', 'fr']).translate('tr').fetch()
                    
                    full_text = " ".join([i['text'] for i in t])
                except Exception as e:
                    st.error("❌ Bu videonun altyazılarına erişilemedi. Lütfen CC simgesi olan bir video deneyin.")
                    st.stop()

            with st.spinner("🧠 Adım 2: Yapay zeka notları hazırlıyor..."):
                # Gemini Yapılandırması
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                Sen akademik bir asistanısın. Aşağıdaki metni analiz et:
                1. Kapsamlı bir ders özeti çıkar.
                2. Önemli bilgileri madde madde (bullet points) listele.
                3. Varsa tarihleri, isimleri ve teknik terimleri vurgula.
                4. Konuyu pekiştirecek 3 soru ve cevabını ekle.
                
                Metin: {full_text[:15000]}
                """
                
                response = model.generate_content(prompt)
                
                st.success("✨ İşlem Başarıyla Tamamlandı!")
                st.markdown("---")
                st.markdown(response.text)
                
                # İndirme Seçeneği
                st.download_button("📥 Ders Notunu İndir (.txt)", response.text, file_name=f"ders_notu_{v_id}.txt")

        except Exception as e:
            st.error(f"🚨 Bir hata oluştu: {str(e)}")

