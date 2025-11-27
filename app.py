import streamlit as st
from googleapiclient.discovery import build
import google.generativeai as genai
import pandas as pd

# --- BURAYA DİKKAT: API ANAHTARLARIN ---
# Bu tırnak içlerine kendi aldığın anahtarları yapıştıracaksın.
YOUTUBE_API_KEY = "AIzaSyDFe4ehlpspXFKylJM0J0FeD76cxix8JDg"
GEMINI_API_KEY = "AIzaSyDFe4ehlpspXFKylJM0J0FeD76cxix8JDg"



# --- SAYFA AYARLARI (Modern Görünüm İçin İlk Adım) ---
st.set_page_config(
    page_title="Social Insight AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MODERN CSS TASARIMI (Apple/Material Style) ---
# Bu kısım Streamlit'in standart görünümünü değiştirip "Uygulama" havası katar.
st.markdown("""
    <style>
    /* Ana Blok Ayarları */
    .main {
        padding-top: 2rem;
    }
    /* Kart Tasarımı */
    div.css-1r6slb0.e1tzin5v2 {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    /* Metric (Sayılar) Stili */
    [data-testid="stMetricValue"] {
        font-size: 24px;
        font-weight: 700;
        color: #4facfe;
    }
    /* Başlık Stilleri */
    h1 {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        letter-spacing: -1px;
    }
    /* Sidebar Güzelleştirme */
    section[data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    @media (prefers-color-scheme: dark) {
        section[data-testid="stSidebar"] {
            background-color: #1c1c1e;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# --- API BAĞLANTILARI ---
try:
    if GEMINI_API_KEY and "BURAYA" not in GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash')

    if YOUTUBE_API_KEY and "BURAYA" not in YOUTUBE_API_KEY:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
except Exception as e:
    st.error(f"API Bağlantı Hatası: {e}")


# --- FONKSİYONLAR ---
def get_video_info(video_id):
    try:
        request = youtube.videos().list(part="snippet,statistics", id=video_id)
        response = request.execute()
        if not response['items']: return None
        item = response['items'][0]
        return {
            'title': item['snippet']['title'],
            'channel': item['snippet']['channelTitle'],
            'views': int(item['statistics']['viewCount']),
            'likes': int(item['statistics'].get('likeCount', 0)),
            'comment_count': int(item['statistics'].get('commentCount', 0)),
            'thumbnail': item['snippet']['thumbnails']['high']['url'],
            'desc': item['snippet']['description'][:150] + "..."
        }
    except:
        return None


def get_comments(video_id):
    try:
        request = youtube.commentThreads().list(part="snippet", videoId=video_id, maxResults=50, textFormat="plainText")
        response = request.execute()
        return [item['snippet']['topLevelComment']['snippet']['textDisplay'] for item in response['items']]
    except:
        return []


def analyze_comments(comments):
    text = "\n".join(comments)
    prompt = f"""
    Aşağıdaki YouTube yorumlarını analiz et. Çıktıyı Markdown formatında, emoji kullanarak ve çok şık bir dille ver.
    Başlıkları belirgin yap.

    Analiz Formatı:
    1. 📊 **Genel Skor:** (0-100 arası bir puan ver ve nedenini açıkla)
    2. 🎭 **Duygu Analizi:** (İnsanlar mutlu mu, kızgın mı, şaşkın mı?)
    3. 💎 **Öne Çıkanlar:** (En çok konuşulan konular)
    4. ⚠️ **Eleştiriler:** (Varsa negatif noktalar)

    YORUMLAR:
    {text}
    """
    try:
        return model.generate_content(prompt).text
    except:
        return "Analiz yapılamadı."


# --- ARAYÜZ (SIDEBAR - SOL MENÜ) ---
with st.sidebar:
    st.title("📱 Social Insight")
    st.markdown("Sosyal medya analiz asistanınız.")

    selected_platform = st.radio(
        "Platform Seç:",
        ["YouTube", "Instagram", "TikTok"],
        index=0
    )

    st.divider()
    st.info("💡 Instagram ve TikTok modülleri yakında aktif olacak.")

# --- ANA EKRAN AKIŞI ---

if selected_platform == "YouTube":
    st.header("YouTube Video Analizi 🟥")
    st.markdown("Videonun linkini girin, yapay zeka sizin için izleyici nabzını tutsun.")

    url = st.text_input("🔗 Video Linkini Yapıştır", placeholder="https://youtube.com/watch?v=...")

    if st.button("🚀 Analizi Başlat", type="primary"):
        if not YOUTUBE_API_KEY or "BURAYA" in YOUTUBE_API_KEY:
            st.error("Lütfen API Anahtarlarını koda ekleyin.")
        elif url:
            # Video ID Bulma
            if "v=" in url:
                video_id = url.split("v=")[1].split("&")[0]
            elif "youtu.be" in url:
                video_id = url.split("/")[-1]
            else:
                video_id = None

            if video_id:
                with st.spinner("Veriler sunucudan çekiliyor..."):
                    info = get_video_info(video_id)

                if info:
                    # --- MODERN KART GÖRÜNÜMÜ ---
                    col1, col2 = st.columns([1, 2], gap="large")

                    with col1:
                        st.image(info['thumbnail'], use_container_width=True)
                        st.caption(f"📺 Kanal: {info['channel']}")

                    with col2:
                        st.subheader(info['title'])
                        st.markdown(f"_{info['desc']}_")

                        # İstatistik Kartları (Grid Yapısı)
                        m1, m2, m3 = st.columns(3)
                        m1.metric("Görüntülenme", f"{info['views']:,}")
                        m2.metric("Beğeni", f"{info['likes']:,}")
                        m3.metric("Yorum", f"{info['comment_count']:,}")

                    st.divider()

                    # --- YORUM ANALİZİ TABLARI ---
                    tab1, tab2 = st.tabs(["🤖 AI Analiz Raporu", "📝 Ham Yorumlar"])

                    with tab1:
                        with st.spinner("Gemini 2.0 yorumları okuyor..."):
                            comments = get_comments(video_id)
                            if comments:
                                result = analyze_comments(comments)
                                st.markdown(result)
                            else:
                                st.warning("Yorum bulunamadı.")

                    with tab2:
                        st.write(comments)

            else:
                st.error("Geçersiz YouTube linki.")
        else:
            st.warning("Lütfen bir link girin.")

elif selected_platform == "Instagram":
    st.header("Instagram Analizi 📸")
    st.warning("🚧 Bu modül yapım aşamasında. Çok yakında burada!")
    st.image("https://cdn-icons-png.flaticon.com/512/2111/2111463.png", width=100)

elif selected_platform == "TikTok":
    st.header("TikTok Analizi 🎵")
    st.warning("🚧 Bu modül yapım aşamasında. Çok yakında burada!")
    st.image("https://cdn-icons-png.flaticon.com/512/3046/3046121.png", width=100)