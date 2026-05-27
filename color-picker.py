import streamlit as st
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans

# Konfigurasi Halaman
st.set_page_config(page_title="PaletteGen | K-Means", page_icon="🎨", layout="centered")

# Custom CSS
st.markdown("""
    <style>
    .title-font {
        font-size:40px !important;
        font-weight: bold;
        color: #2C3E50;
        text-align: center;
        margin-bottom: 0px;
    }
    .subtitle-font {
        text-align: center;
        color: #7F8C8D;
        margin-bottom: 30px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        background-color: #3498DB;
        color: white;
    }
    .stButton>button:hover {
        background-color: #2980B9;
    }
    </style>
""", unsafe_allow_html=True)

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % (int(rgb[0]), int(rgb[1]), int(rgb[2]))

@st.cache_data 
def get_dominant_colors(image, k):
    # Resize gambar
    image = image.resize((150, 150))
    img_array = np.array(image)
    
    # Reshape ke 2D array untuk K-Means
    pixels = img_array.reshape((-1, 3))
    
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(pixels)
    
    centroids = kmeans.cluster_centers_
    hex_colors = [rgb_to_hex(color) for color in centroids]
    
    return hex_colors


st.markdown('<p class="title-font">🎨 Image Color Extractor</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-font">Temukan palet warna dominan dari gambarmu menggunakan K-Means Clustering!</p>', unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Pengaturan")
    k_value = st.slider("Jumlah Warna Dominan (K)", min_value=2, max_value=8, value=5)
    
    st.markdown("---")
    st.markdown("### 🧠 Cara Kerja (Behind the Scene)")
    st.write("Aplikasi ini menggunakan algoritma **K-Means Clustering** dari library `scikit-learn`.")
    st.write("Setiap pixel dalam gambar dianggap sebagai data point. Algoritma akan mengelompokkan pixel-pixel tersebut ke dalam `K` cluster berdasarkan kedekatan warna (Euclidean distance).")
    st.caption("Dibuat untuk Tugas AI - Bakti Champions 2026")

uploaded_file = st.file_uploader("📂 Upload Gambar Kamu di Sini", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("**🖼️ Gambar Asli:**")
        st.image(image, use_column_width=True, width=300)
    
    with col2:
        st.markdown("**🎨 Hasil Palet Warna:**")
        with st.spinner("Mesin K-Means sedang berpikir... 🤖"):
            try:
                dominant_colors = get_dominant_colors(image, k=k_value)
                
                color_cols = st.columns(k_value)
                for i, col in enumerate(color_cols):
                    with col:
                        st.color_picker(f"#{i+1}", value=dominant_colors[i], key=i)
                        st.code(dominant_colors[i]) 
                
                st.success("Yeay! Berhasil mengekstrak warna.")
                
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")
else:
    st.info("👆 Silakan upload gambar terlebih dahulu.")