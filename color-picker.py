import streamlit as st
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
import json

st.set_page_config(
    page_title="PaletteGen | K-Means", 
    page_icon="https://cdn-icons-png.flaticon.com/512/2916/2916315.png", 
    layout="centered"
)

st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
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
    .icon-spacing {
        margin-right: 8px;
        color: #3498DB;
    }
    </style>
""", unsafe_allow_html=True)

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % (int(rgb[0]), int(rgb[1]), int(rgb[2]))

def get_dominant_colors_and_model(image, k):
    small_image = image.copy()
    small_image.thumbnail((150, 150))
    img_array = np.array(small_image, dtype=float) 
    pixels = img_array.reshape((-1, 3))
    
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(pixels)
    
    centroids = kmeans.cluster_centers_
    hex_colors = [rgb_to_hex(color) for color in centroids]
    
    return hex_colors, kmeans

def highlight_color_on_image(image, kmeans, cluster_index):
    display_img = image.copy()
    display_img.thumbnail((500, 500)) 
    
    img_array = np.array(display_img, dtype=float)
    h, w, c = img_array.shape
    pixels = img_array.reshape((-1, 3))
    
    labels = kmeans.predict(pixels)
    
    mask = (labels != cluster_index)
    pixels[mask] *= 0.2 
    
    highlighted_img = pixels.reshape((h, w, c)).astype(np.uint8)
    return Image.fromarray(highlighted_img)

st.markdown('<p class="title-font"><i class="fas fa-palette icon-spacing"></i> Image Color Extractor</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-font">Temukan palet warna dominan dari gambarmu menggunakan K-Means Clustering!</p>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<h3><i class="fas fa-sliders-h icon-spacing"></i> Pengaturan</h3>', unsafe_allow_html=True)
    k_value = st.slider("Jumlah Warna Dominan (K)", min_value=2, max_value=8, value=5)
    
    st.markdown("---")
    st.markdown('<h4><i class="fas fa-microchip icon-spacing"></i> Cara Kerja</h4>', unsafe_allow_html=True)
    st.write("Menggunakan algoritma **K-Means Clustering** dari library `scikit-learn`.")
    st.write("Pixel gambar dikelompokkan ke dalam `K` cluster berdasarkan jarak warna (Euclidean distance). Fitur 'Sorot' bekerja dengan memprediksi label tiap pixel dan meredupkan label yang tidak dipilih.")
    st.caption("Valensius Alven - 140810240059")

st.markdown('<p style="font-weight: bold;"><i class="fas fa-upload icon-spacing"></i> Upload Gambar Kamu di Sini</p>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert('RGB')
    
    col1, col2 = st.columns([1, 1]) 
    
    with col1:
        st.markdown('**<i class="fas fa-image icon-spacing"></i> Gambar Asli:**', unsafe_allow_html=True)
        st.image(image, use_column_width=True)
    
    with col2:
        st.markdown('**<i class="fas fa-swatchbook icon-spacing"></i> Hasil Palet Warna:**', unsafe_allow_html=True)
        with st.spinner("Mesin K-Means sedang memproses..."):
            try:
                dominant_colors, trained_kmeans = get_dominant_colors_and_model(image, k=k_value)
               
                palette_html = '<div style="display: flex; flex-wrap: wrap; gap: 12px; justify-content: flex-start; margin-bottom: 20px;">'
                for hex_code in dominant_colors:
                    palette_html += f'<div style="display: flex; flex-direction: column; align-items: center;"><label style="cursor: pointer;"><input type="color" value="{hex_code}" style="opacity: 0; position: absolute; width: 0; height: 0;"><div style="width: 50px; height: 50px; background-color: {hex_code}; border-radius: 8px; border: 1px solid #444; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);"></div></label><span style="font-family: monospace; font-size: 13px; margin-top: 5px;">{hex_code}</span></div>'
                palette_html += '</div>'
                
                st.markdown(palette_html, unsafe_allow_html=True)
                st.success("Ekstraksi selesai!")
                
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")
                st.stop()

    st.markdown("---")
    st.markdown('<h3><i class="fas fa-search-location icon-spacing"></i> Lacak Lokasi Warna</h3>', unsafe_allow_html=True)
    st.markdown("Pilih salah satu warna di bawah ini untuk melihat bagian gambar mana yang memiliki elemen warna tersebut.")
    
    options = [f"Warna {i+1} ({hex_c})" for i, hex_c in enumerate(dominant_colors)]
    selected_option = st.radio("Pilih Warna:", options, horizontal=True, label_visibility="collapsed")
    
    selected_index = options.index(selected_option)
    highlighted_result = highlight_color_on_image(image, trained_kmeans, selected_index)
    
    mid_col1, mid_col2, mid_col3 = st.columns([1, 2, 1])
    with mid_col2:
        st.image(highlighted_result, caption=f"Menyorot area untuk {selected_option}", use_column_width=True)

    st.markdown("---")
    st.markdown('**<i class="fas fa-file-export icon-spacing"></i> Ekspor Palet**', unsafe_allow_html=True)
    
    css_data = ":root {\n" + "".join([f"  --color-{i+1}: {hex_code};\n" for i, hex_code in enumerate(dominant_colors)]) + "}"
    json_data = json.dumps({"palette": dominant_colors}, indent=4)
    txt_data = ", ".join(dominant_colors)
    
    dl_col1, dl_col2, dl_col3 = st.columns(3)
    with dl_col1:
        st.download_button("Format CSS", data=css_data, file_name="palette.css", mime="text/css", use_container_width=True)
    with dl_col2:
        st.download_button("Format JSON", data=json_data, file_name="palette.json", mime="application/json", use_container_width=True)
    with dl_col3:
        st.download_button("Format TXT", data=txt_data, file_name="palette.txt", mime="text/plain", use_container_width=True)

else:
    st.info("Silakan upload gambar terlebih dahulu untuk memulai ekstraksi warna.")