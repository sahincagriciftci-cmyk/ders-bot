import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai

# Sayfa Yapılandırması
st.set_page_config(page_title="Yapay Zeka Ders Asistanı", layout="wide", page_icon="🎓")

# Özel CSS ile Arayüzü Güzelleştirelim
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #ff4b4b; color: white; }
    .stTextInput>div>div>input { border-radius: 5px; }
    </style>
    """, unsafe_allow_stdio=True)

st.title("🎓 Yapay Zeka Ders Asistanı")
st.caption("YouTube videolarını profesyonel ders notlarına dönüştürün.")

# Yan Panel (API Key)
with st.sidebar:
    st.header("⚙️ Ayarlar")
    api_key = st.text_input("Gemini API Key Giriniz:", type="password", help="Google AI Studio'dan aldığınız anahtar.").strip()
    st.divider()
    st.info("💡 İpucu: Altyazıları olan (CC) videolar her zaman daha iyi sonuç verir.")

# Ana Giriş Alanı
video_url = st.text_input("YouTube Video Linkini Buraya Yapıştırın:", placeholder="https://www.youtube.com/watch?v=...").strip()

if st.button("Analiz Et ve Not Çıkar"):
    if not api_key:
        st.warning("⚠️ Lütfen sol taraftaki menüden geçerli bir API Key giriniz.")
    elif not video_url:
        st.warning("⚠️ Lütfen analiz etmek istediğiniz bir YouTube video linki giriniz.")
    else:
        try:
            # 1. Video ID Ayıklama (Her türlü link formatı için)
            video_id = ""
            if "v=" in video_url:
                video_id = video_url.split("v=")[1].split("&")[0]
            elif "youtu.be/" in video_url:
                video_id = video_url.split("/")[-1].split("?")[0]
            else:
                video_id = video_url # Sadece ID girilirse

            if not video_id:
                st.error("❌ Video linki anlaşılamadı. Lütfen linki kontrol edin.")
                st.stop()

            with st.spinner("🔍 Video inceleniyor, altyazılar toplanıyor..."):
                # 2. Gelişmiş Altyazı Çekme (Hata almamak için 3 aşamalı deneme)
                full_text = ""
                try:
                    # Aşama A: Mevcut tüm altyazıları listele
                    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                    
                    try:
                        # Aşama B: Önce Türkçe veya İngilizce manuel/otomatik altyazı ara
                        transcript = transcript_list.find_transcript(['tr', 'en']).fetch()
                    except:
                        # Aşama C: Eğer yoksa, mevcut ilk altyazıyı (herhangi bir dilde) bul ve Türkçe'ye çevir
                        # Bu İlber Ortaylı gibi sadece tek dilde otomatik altyazısı olanlar için hayat kurtarır
                        transcript = transcript_list.find_one_of_variable_langs(['tr', 'en', 'de', 'fr']).translate('tr').fetch()
                    
                    full_text = " ".join([t['text'] for t in transcript])
                
                except Exception as sub_e:
                    st.error(f"⚠️ Altyazı Erişilemedi: Bu videoda altyazı kapalı olabilir veya YouTube erişimi engelliyor.")
                    st.stop()

                # 3. Gemini Analizi
                if full_text:
                    genai.configure(api_key=api_key)
                    # En stabil model olan flash-1.5 kullanıyoruz
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    prompt = f"""
                    Sen uzman bir eğitim asistanısın. Aşağıdaki video transkriptini kullanarak öğrencilerin çalışabileceği düzenli bir ders notu oluştur.
                    
                    Lütfen şu yapıyı takip et:
                    - **Dersin Konusu ve Özet**: Videonun ne anlattığını kısaca açıkla.
                    - **Ana Başlıklar ve Detaylı Notlar**: Önemli kısımları madde madde, anlaşılır bir dille açıkla.
                    - **Kilit Kavramlar**: Varsa videoda geçen önemli terimleri tanımla.
                    - **Öğrenci Soruları**: Konuyu pekiştirmek için 3 adet soru hazırla.
                    
                    Video Metni:
                    {full_text[:20000]} 
                    """
                    
                    response = model.generate_content(prompt)
                    
                    st.success("✅ Analiz başarıyla tamamlandı!")
                    st.markdown("---")
                    st.markdown(response.text)
                    
                    # Notları indirme butonu ekleyelim
                    st.download_button(label="📥 Notları İndir (.txt)", data=response.text, file_name="ders_notu.txt", mime="text/plain")

        except Exception as e:
            st.error(f"🚨 Beklenmedik bir hata oluştu: {str(e)}")
            st.info("Lütfen sayfayı yenileyip tekrar deneyin veya farklı bir video deneyin.")

