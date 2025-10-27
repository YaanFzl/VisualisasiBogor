import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import requests
import json

# Konfigurasi halaman
st.set_page_config(
    page_title="Visualisasi Data Kabupaten Bogor",
    page_icon="🗺️",
    layout="wide"
)

# Title dan Header
st.markdown("""
    <div style='background: linear-gradient(to right, #16a085, #2980b9, #8e44ad); padding: 20px; border-radius: 10px;'>
        <h1 style='color: white; text-align: center;'>🗺️ Visualisasi Data Kabupaten Bogor</h1>
        <p style='color: white; text-align: center;'>Bogor Regency - Peta Kecamatan Interaktif dengan Batas Asli</p>
    </div>
""", unsafe_allow_html=True)

st.write("")


# Opsi untuk load GeoJSON
@st.cache_data
def load_geojson_from_url(url):
    """Load GeoJSON from URL"""
    try:
        response = requests.get(url, timeout=10)
        return response.json()
    except:
        return None


# Function to load GeoJSON from file
@st.cache_data
def load_bogor_geojson():
    """Load Bogor Regency GeoJSON from local file"""
    try:
        with open('bogor_regency.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None


# Sidebar untuk upload file
with st.sidebar:
    st.header("📂 Upload Data")

    # Opsi GeoJSON
    st.subheader("🗺️ Sumber Peta")
    geojson_option = st.radio(
        "Pilih sumber GeoJSON:",
        ["Gunakan Peta Bawaan", "Upload File GeoJSON", "Gunakan Placeholder (Kotak)"]
    )

    geojson_data = None

    if geojson_option == "Gunakan Peta Bawaan":
        geojson_data = load_bogor_geojson()
        if geojson_data:
            st.success(f"✅ Loaded: {len(geojson_data.get('features', []))} kecamatan")
        else:
            st.error("❌ File bogor_regency.json tidak ditemukan")
            st.info("💡 Upload file GeoJSON atau gunakan placeholder")

    elif geojson_option == "Upload File GeoJSON":
        geojson_file = st.file_uploader(
            "Upload file GeoJSON untuk batas kecamatan",
            type=['geojson', 'json'],
            help="File GeoJSON harus berisi polygon batas kecamatan Bogor"
        )

        if geojson_file:
            geojson_data = json.load(geojson_file)
            st.success(f"✅ GeoJSON loaded: {len(geojson_data.get('features', []))} features")

    st.divider()

    st.write("Upload file Excel atau CSV dengan kolom:")
    st.code("KECAMATAN | POTENSI")

    uploaded_file = st.file_uploader(
        "Pilih file CSV atau Excel",
        type=['csv', 'xlsx', 'xls'],
        help="File harus memiliki kolom KECAMATAN dan POTENSI/NILAI"
    )

    st.divider()

    # Download contoh CSV
    sample_data = """KECAMATAN,POTENSI
Citeureup,33537
Babakan Madang,18105
Sukamakmur,13622
Caringin,20863
Cijeruk,14656
Cigombong,15346
Cibinong,25000
Bojong Gede,22000
Tajur Halang,19000
Kemang,17500
Rumpin,16000
Jasinga,15800
Parung Panjang,18500
Leuwiliang,14200
Ciseeng,19300
Parung,21000
Gunung Sindur,20500
Cibungbulang,13900
Pamijahan,12800
Ciampea,16700
Dramaga,19800
Ciomas,23000
Tamansari,15500
Ciawi,17200
Cisarua,14800
Megamendung,13500
Cariu,15200
Tanjungsari,14500
Jonggol,16300
Cileungsi,24500
Klapanunggal,17800
Gunung Putri,26000"""

    st.download_button(
        label="📥 Download Contoh CSV",
        data=sample_data,
        file_name="contoh_data_bogor.csv",
        mime="text/csv"
    )

    st.info(
        "💡 **Tips**: Untuk peta yang akurat, gunakan file GeoJSON dengan batas administratif sebenarnya dari sumber seperti GADM atau OpenStreetMap.")

# Placeholder GeoJSON (kotak sederhana)
placeholder_geojson = {
    "type": "FeatureCollection",
    "features": [
        {"type": "Feature", "properties": {"name": "Citeureup"},
         "geometry": {"type": "Polygon", "coordinates": [
             [[106.85, -6.45], [106.92, -6.45], [106.92, -6.52], [106.85, -6.52], [106.85, -6.45]]]}},
        {"type": "Feature", "properties": {"name": "Babakan Madang"},
         "geometry": {"type": "Polygon", "coordinates": [
             [[106.85, -6.52], [106.92, -6.52], [106.92, -6.58], [106.85, -6.58], [106.85, -6.52]]]}},
        {"type": "Feature", "properties": {"name": "Sukamakmur"},
         "geometry": {"type": "Polygon", "coordinates": [
             [[106.92, -6.45], [106.99, -6.45], [106.99, -6.52], [106.92, -6.52], [106.92, -6.45]]]}},
        {"type": "Feature", "properties": {"name": "Caringin"},
         "geometry": {"type": "Polygon", "coordinates": [
             [[106.78, -6.58], [106.85, -6.58], [106.85, -6.65], [106.78, -6.65], [106.78, -6.58]]]}},
        {"type": "Feature", "properties": {"name": "Cijeruk"},
         "geometry": {"type": "Polygon", "coordinates": [
             [[106.71, -6.52], [106.78, -6.52], [106.78, -6.58], [106.71, -6.58], [106.71, -6.52]]]}},
        {"type": "Feature", "properties": {"name": "Cigombong"},
         "geometry": {"type": "Polygon", "coordinates": [
             [[106.78, -6.65], [106.85, -6.65], [106.85, -6.72], [106.78, -6.72], [106.78, -6.65]]]}},
        {"type": "Feature", "properties": {"name": "Cibinong"},
         "geometry": {"type": "Polygon", "coordinates": [
             [[106.85, -6.58], [106.92, -6.58], [106.92, -6.65], [106.85, -6.65], [106.85, -6.58]]]}},
        {"type": "Feature", "properties": {"name": "Bojong Gede"},
         "geometry": {"type": "Polygon", "coordinates": [
             [[106.78, -6.52], [106.85, -6.52], [106.85, -6.58], [106.78, -6.58], [106.78, -6.52]]]}},
        {"type": "Feature", "properties": {"name": "Tajur Halang"},
         "geometry": {"type": "Polygon", "coordinates": [
             [[106.85, -6.65], [106.92, -6.65], [106.92, -6.72], [106.85, -6.72], [106.85, -6.65]]]}},
        {"type": "Feature", "properties": {"name": "Kemang"},
         "geometry": {"type": "Polygon", "coordinates": [
             [[106.71, -6.58], [106.78, -6.58], [106.78, -6.65], [106.71, -6.65], [106.71, -6.58]]]}},
        {"type": "Feature", "properties": {"name": "Rumpin"},
         "geometry": {"type": "Polygon", "coordinates": [
             [[106.64, -6.58], [106.71, -6.58], [106.71, -6.65], [106.64, -6.65], [106.64, -6.58]]]}},
        {"type": "Feature", "properties": {"name": "Jasinga"},
         "geometry": {"type": "Polygon", "coordinates": [
             [[106.64, -6.65], [106.71, -6.65], [106.71, -6.72], [106.64, -6.72], [106.64, -6.65]]]}},
    ]
}


def get_color_for_value(value, min_val, max_val):
    """Generate warna berdasarkan nilai"""
    colors = [
        '#4CAF50', '#2196F3', '#FF9800', '#E91E63', '#9C27B0',
        '#FF5722', '#00BCD4', '#FFEB3B', '#795548', '#607D8B',
        '#3F51B5', '#009688', '#FFC107', '#CDDC39', '#FF4081',
        '#00ACC1', '#7CB342', '#D32F2F', '#512DA8', '#689F38',
        '#F44336', '#03A9F4', '#8BC34A', '#FFC107', '#673AB7'
    ]

    if max_val == min_val:
        return colors[0]

    ratio = (value - min_val) / (max_val - min_val)
    index = int(ratio * (len(colors) - 1))
    return colors[min(index, len(colors) - 1)]


def normalize_name(name):
    """Normalize nama kecamatan untuk matching"""
    return name.lower().strip().replace(" ", "").replace("-", "")


# Main content
if uploaded_file is not None:
    try:
        # Baca file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Cari kolom kecamatan dan nilai
        kecamatan_col = [col for col in df.columns if 'kecamatan' in col.lower() or 'kec' in col.lower()]
        nilai_col = [col for col in df.columns if
                     any(x in col.lower() for x in ['nilai', 'potensi', 'value', 'jumlah'])]

        if not kecamatan_col or not nilai_col:
            st.error("❌ File harus memiliki kolom 'KECAMATAN' dan 'NILAI/POTENSI'")
        else:
            # Clean data
            df = df[[kecamatan_col[0], nilai_col[0]]].copy()
            df.columns = ['Kecamatan', 'Nilai']
            df['Kecamatan'] = df['Kecamatan'].str.strip()
            df['Nilai'] = pd.to_numeric(df['Nilai'], errors='coerce')
            df = df.dropna()

            # Normalized names untuk matching
            df['Kecamatan_normalized'] = df['Kecamatan'].apply(normalize_name)

            # Pilih GeoJSON yang akan digunakan
            if geojson_data is None:
                geojson_data = placeholder_geojson
                st.warning("⚠️ Menggunakan placeholder (kotak). Upload GeoJSON untuk batas yang akurat.")

            # Layout dengan columns
            col1, col2 = st.columns([3, 1])

            with col2:
                st.subheader("📊 Statistik")
                st.metric("Total Kecamatan", len(df))
                st.metric("Nilai Tertinggi", f"{df['Nilai'].max():,.0f}")
                st.metric("Nilai Terendah", f"{df['Nilai'].min():,.0f}")
                st.metric("Rata-rata", f"{df['Nilai'].mean():,.0f}")

                st.divider()

                st.subheader("📋 Data")
                df_sorted = df[['Kecamatan', 'Nilai']].sort_values('Nilai', ascending=False).reset_index(drop=True)
                df_sorted.index = df_sorted.index + 1
                st.dataframe(df_sorted, use_container_width=True, height=400)

            with col1:
                st.subheader("🗺️ Peta Interaktif")

                # Buat peta
                m = folium.Map(
                    location=[-6.60, 106.85],
                    zoom_start=10,
                    tiles='OpenStreetMap'
                )

                # Tambahkan GeoJSON dengan warna
                min_val = df['Nilai'].min()
                max_val = df['Nilai'].max()

                matched_count = 0
                unmatched = []

                for feature in geojson_data.get('features', []):
                    # Coba berbagai field untuk nama (GADM format uses NAME_3)
                    kecamatan_name = (
                            feature['properties'].get('NAME_3') or
                            feature['properties'].get('name') or
                            feature['properties'].get('NAME') or
                            feature['properties'].get('KECAMATAN') or
                            feature['properties'].get('Kecamatan') or
                            feature['properties'].get('NAMOBJ') or
                            "Unknown"
                    )

                    kec_normalized = normalize_name(kecamatan_name)
                    kecamatan_data = df[df['Kecamatan_normalized'] == kec_normalized]

                    if not kecamatan_data.empty:
                        matched_count += 1
                        nilai = kecamatan_data['Nilai'].values[0]
                        color = get_color_for_value(nilai, min_val, max_val)

                        folium.GeoJson(
                            feature,
                            style_function=lambda x, color=color: {
                                'fillColor': color,
                                'color': 'white',
                                'weight': 2,
                                'fillOpacity': 0.7
                            },
                            tooltip=f"<b>{kecamatan_name}</b>",
                            popup=folium.Popup(
                                f"""
                                <div style='font-family: Arial; width: 200px;'>
                                    <h4 style='margin: 0; color: #333;'>{kecamatan_name}</h4>
                                    <hr style='margin: 5px 0;'>
                                    <p style='margin: 5px 0;'><b>Nilai:</b> {nilai:,.0f}</p>
                                </div>
                                """,
                                max_width=250
                            )
                        ).add_to(m)
                    else:
                        unmatched.append(kecamatan_name)
                        folium.GeoJson(
                            feature,
                            style_function=lambda x: {
                                'fillColor': '#e0e0e0',
                                'color': 'white',
                                'weight': 2,
                                'fillOpacity': 0.5
                            },
                            tooltip=f"<b>{kecamatan_name}</b> (Tidak ada data)"
                        ).add_to(m)

                folium_static(m, width=900, height=600)

                # Info matching
                st.info(f"✅ Berhasil match: {matched_count}/{len(geojson_data.get('features', []))} kecamatan")

                if unmatched:
                    with st.expander("⚠️ Kecamatan tanpa data"):
                        st.write(", ".join(unmatched))

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.exception(e)
else:
    st.info("👆 Silakan upload file CSV atau Excel di sidebar untuk memulai visualisasi")

    st.markdown("### 📖 Cara Mendapatkan GeoJSON yang Akurat")
    st.markdown("""
    **Sumber GeoJSON untuk Bogor Regency:**

    1. **GADM (Recommended)**
       - Website: https://gadm.org/download_country.html
       - Pilih Indonesia → Level 3 (Kecamatan)
       - Download format GeoJSON

    2. **Indonesia Geospatial**
       - Website: https://tanahair.indonesia.go.id/portal-web/
       - Cari data administratif Kabupaten Bogor

    3. **OpenStreetMap**
       - Gunakan Overpass Turbo: https://overpass-turbo.eu/
       - Query: `[out:json];area["name"="Bogor Regency"];(relation(area)["admin_level"="6"];);out geom;`

    4. **GitHub**
       - Cari: "indonesia geojson" atau "bogor geojson"
    """)

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>Visualisasi Data Kabupaten Bogor | Dibuat dengan Streamlit & Folium</p>
        <p style='font-size: 0.9em;'>💡 Gunakan GeoJSON asli untuk batas yang akurat</p>
    </div>
""", unsafe_allow_html=True)