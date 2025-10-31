import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import json
import requests
import plotly.express as px
import plotly.graph_objects as go

# Konfigurasi halaman
st.set_page_config(
    page_title="Dashboard Potensi & Realisasi Bogor",
    page_icon="📊",
    layout="wide"
)

# Title dan Header
st.markdown("""
    <div style='background: linear-gradient(to right, #004aad, #0074e0); padding: 20px; border-radius: 10px;'>
        <h1 style='color: white; text-align: center;'>📊 Dashboard Potensi & Akuisisi Perisai</h1>
        <p style='color: white; text-align: center;'>Kabupaten Bogor - Monitoring & Visualisasi Interaktif</p>
    </div>
""", unsafe_allow_html=True)

st.write("")


# Function to load GeoJSON from file
@st.cache_data
def load_bogor_geojson():
    """Load Bogor Regency GeoJSON from local file"""
    try:
        with open('bogor_regency.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None


# Function to load data from Google Sheets
@st.cache_data(ttl=300)
def load_google_sheets_data(url):
    """Load data from Google Apps Script"""
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get('status') == 'ok':
            return pd.DataFrame(data['data'])
        return None
    except Exception as e:
        st.error(f"Error loading from Google Sheets: {str(e)}")
        return None


# Placeholder GeoJSON (kotak sederhana)
placeholder_geojson = {
    "type": "FeatureCollection",
    "features": [
        {"type": "Feature", "properties": {"NAME_3": "Citeureup"},
         "geometry": {"type": "Polygon", "coordinates": [
             [[106.85, -6.45], [106.92, -6.45], [106.92, -6.52], [106.85, -6.52], [106.85, -6.45]]]}},
        {"type": "Feature", "properties": {"NAME_3": "Babakan Madang"},
         "geometry": {"type": "Polygon", "coordinates": [
             [[106.85, -6.52], [106.92, -6.52], [106.92, -6.58], [106.85, -6.58], [106.85, -6.52]]]}},
        {"type": "Feature", "properties": {"NAME_3": "Sukamakmur"},
         "geometry": {"type": "Polygon", "coordinates": [
             [[106.92, -6.45], [106.99, -6.45], [106.99, -6.52], [106.92, -6.52], [106.92, -6.45]]]}},
        {"type": "Feature", "properties": {"NAME_3": "Cibinong"},
         "geometry": {"type": "Polygon", "coordinates": [
             [[106.85, -6.58], [106.92, -6.58], [106.92, -6.65], [106.85, -6.65], [106.85, -6.58]]]}},
    ]
}


def normalize_name(name):
    """Normalize nama kecamatan untuk matching"""
    return name.lower().strip().replace(" ", "").replace("-", "")


def get_color_by_percentage(persen):
    """Warna berdasarkan persentase realisasi (untuk progress bar)"""
    if persen >= 80:
        return '#28a745'  # Hijau
    elif persen >= 50:
        return '#ffc107'  # Kuning
    elif persen > 0:
        return '#dc3545'  # Merah
    else:
        return '#e0e0e0'  # Abu-abu (tidak ada data)


def get_colorful_palette():
    """Warna warni untuk peta"""
    return [
        '#4CAF50', '#2196F3', '#FF9800', '#E91E63', '#9C27B0',
        '#FF5722', '#00BCD4', '#FFEB3B', '#795548', '#607D8B',
        '#3F51B5', '#009688', '#FFC107', '#CDDC39', '#FF4081',
        '#00ACC1', '#7CB342', '#D32F2F', '#512DA8', '#689F38',
        '#F44336', '#03A9F4', '#8BC34A', '#E65100', '#673AB7',
        '#00897B', '#6D4C41', '#5E35B1', '#1E88E5', '#43A047'
    ]


# Sidebar
with st.sidebar:
    st.header("⚙️ Konfigurasi")

    # Data Source
    st.subheader("📂 Sumber Data")
    data_source = st.radio(
        "Pilih sumber data:",
        ["Google Sheets", "Upload File"]
    )

    df = None

    if data_source == "Google Sheets":
        gs_url = st.text_input(
            "Google Apps Script URL",
            value="https://script.google.com/macros/s/AKfycbwdWbIsHNUvba1fMh3K41-1sS0-nuQmvDbcoHJMc2z_v-mCSFvKbWkHHucfZkiN1gmc/exec?action=getPotensiRealisasi",
            help="URL dari Google Apps Script yang mengembalikan data JSON"
        )

        if st.button("🔄 Load Data from Google Sheets"):
            with st.spinner("Loading..."):
                df = load_google_sheets_data(gs_url)
                if df is not None:
                    st.success(f"✅ Loaded {len(df)} kecamatan")
    else:
        uploaded_file = st.file_uploader(
            "Upload CSV atau Excel",
            type=['csv', 'xlsx', 'xls'],
            help="File dengan kolom: KECAMATAN, POTENSI, REALISASI"
        )

        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                    st.success(f"✅ Loaded {len(df)} rows")
                else:
                    # Excel file - check for multiple sheets
                    excel_file = pd.ExcelFile(uploaded_file)
                    sheet_names = excel_file.sheet_names

                    st.info(f"📋 Sheet ditemukan: {', '.join(sheet_names)}")

                    # Check if we have POTENSI and AKUISISI sheets
                    if 'POTENSI' in sheet_names and 'AKUISISI' in sheet_names:
                        df_potensi = pd.read_excel(uploaded_file, sheet_name='POTENSI')
                        df_akuisisi = pd.read_excel(uploaded_file, sheet_name='AKUISISI')

                        # Remove empty rows
                        df_potensi = df_potensi.dropna(how='all')
                        df_akuisisi = df_akuisisi.dropna(how='all')

                        # Clean column names
                        df_potensi.columns = [str(col).strip().upper() for col in df_potensi.columns]
                        df_akuisisi.columns = [str(col).strip().upper() for col in df_akuisisi.columns]

                        st.sidebar.write("**POTENSI columns:**", list(df_potensi.columns)[:5])
                        st.sidebar.write("**AKUISISI columns:**", list(df_akuisisi.columns)[:5])

                        # Find kecamatan columns - prioritize exact matches
                        kec_col_pot = None
                        kec_col_aku = None

                        # Try exact matches first
                        if 'KECAMATAN' in df_potensi.columns:
                            kec_col_pot = 'KECAMATAN'
                        elif 'KODE KECAMATAN' in df_potensi.columns:
                            kec_col_pot = 'KODE KECAMATAN'
                        else:
                            for c in df_potensi.columns:
                                if 'KEC' in c:
                                    kec_col_pot = c
                                    break

                        if 'KECAMATAN' in df_akuisisi.columns:
                            kec_col_aku = 'KECAMATAN'
                        elif 'KODE KECAMATAN' in df_akuisisi.columns:
                            kec_col_aku = 'KODE KECAMATAN'
                        else:
                            for c in df_akuisisi.columns:
                                if 'KEC' in c:
                                    kec_col_aku = c
                                    break

                        if kec_col_pot and kec_col_aku:
                            # Remove rows where kecamatan is empty
                            df_potensi = df_potensi[df_potensi[kec_col_pot].notna()]
                            df_akuisisi = df_akuisisi[df_akuisisi[kec_col_aku].notna()]

                            # Check if there's a POTENSI column (numeric values) or just count rows
                            has_potensi_col = any('POTENSI' in str(col).upper() or 'NILAI' in str(col).upper()
                                                  for col in df_potensi.columns if col != kec_col_pot)

                            if has_potensi_col:
                                # Find the numeric potensi column
                                potensi_value_col = None
                                for col in df_potensi.columns:
                                    if col != kec_col_pot and (
                                            'POTENSI' in str(col).upper() or 'NILAI' in str(col).upper()):
                                        potensi_value_col = col
                                        break

                                if potensi_value_col:
                                    # Sum the potensi values per kecamatan
                                    df_potensi[potensi_value_col] = pd.to_numeric(df_potensi[potensi_value_col],
                                                                                  errors='coerce').fillna(0)
                                    potensi_count = df_potensi.groupby(kec_col_pot)[
                                        potensi_value_col].sum().reset_index()
                                    potensi_count.columns = ['Kecamatan', 'Potensi']
                                    st.sidebar.info(f"📊 Menggunakan kolom nilai: {potensi_value_col}")
                                else:
                                    # Fallback: count rows
                                    potensi_count = df_potensi[kec_col_pot].value_counts().reset_index()
                                    potensi_count.columns = ['Kecamatan', 'Potensi']
                                    st.sidebar.info("📊 Menghitung jumlah baris (row count)")
                            else:
                                # Count rows per kecamatan
                                potensi_count = df_potensi[kec_col_pot].value_counts().reset_index()
                                potensi_count.columns = ['Kecamatan', 'Potensi']
                                st.sidebar.info("📊 Menghitung jumlah baris (row count)")

                            # For AKUISISI, always count rows (number of people acquired)
                            akuisisi_count = df_akuisisi[kec_col_aku].value_counts().reset_index()
                            akuisisi_count.columns = ['Kecamatan', 'Realisasi']

                            # Convert to string and clean
                            potensi_count['Kecamatan'] = potensi_count['Kecamatan'].astype(str).str.strip()
                            akuisisi_count['Kecamatan'] = akuisisi_count['Kecamatan'].astype(str).str.strip()


                            # Remove code prefixes and clean names more aggressively
                            def clean_kecamatan_name(name):
                                name = str(name).strip()
                                # Remove leading numbers and spaces (e.g., "320138 ")
                                name = pd.Series(name).str.replace(r'^\d+\s*', '', regex=True).iloc[0]
                                # Remove "Kecamatan" prefix (case insensitive)
                                name = pd.Series(name).str.replace(r'^Kecamatan\s+', '', case=False, regex=True).iloc[0]
                                # Final strip
                                return name.strip()


                            potensi_count['Kecamatan'] = potensi_count['Kecamatan'].apply(clean_kecamatan_name)
                            akuisisi_count['Kecamatan'] = akuisisi_count['Kecamatan'].apply(clean_kecamatan_name)

                            # Show preview
                            with st.sidebar.expander("📊 Preview Data"):
                                st.write("**Potensi (Top 5):**")
                                st.dataframe(potensi_count.head(5), use_container_width=True)
                                st.write("**Akuisisi (Top 5):**")
                                st.dataframe(akuisisi_count.head(5), use_container_width=True)

                            # Merge
                            df = pd.merge(potensi_count, akuisisi_count, on='Kecamatan', how='outer').fillna(0)
                            df['Potensi'] = df['Potensi'].astype(int)
                            df['Realisasi'] = df['Realisasi'].astype(int)

                            st.success(
                                f"✅ Merged: {len(df)} kecamatan | Total Potensi: {df['Potensi'].sum():,} | Total Realisasi: {df['Realisasi'].sum():,}")
                        else:
                            st.error(
                                f"❌ Kolom kecamatan tidak ditemukan. Potensi: {kec_col_pot}, Akuisisi: {kec_col_aku}")
                            df = None
                    else:
                        # Single sheet or different names
                        selected_sheet = st.sidebar.selectbox("Pilih sheet:", sheet_names)
                        df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
                        st.success(f"✅ Loaded {len(df)} rows from '{selected_sheet}'")

            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.exception(e)

    st.divider()

    # GeoJSON Source
    st.subheader("🗺️ Sumber Peta")
    map_source = st.radio(
        "Pilih sumber GeoJSON:",
        ["Gunakan Peta Bawaan", "Upload GeoJSON", "Placeholder"]
    )

    geojson_data = None

    if map_source == "Gunakan Peta Bawaan":
        geojson_data = load_bogor_geojson()
        if geojson_data:
            st.success(f"✅ {len(geojson_data.get('features', []))} kecamatan")
        else:
            st.warning("⚠️ bogor_regency.json tidak ditemukan")
    elif map_source == "Upload GeoJSON":
        geojson_file = st.file_uploader("Upload file GeoJSON", type=['geojson', 'json'])
        if geojson_file:
            geojson_data = json.load(geojson_file)
            st.success(f"✅ {len(geojson_data.get('features', []))} features")
    else:
        geojson_data = placeholder_geojson
        st.info("Menggunakan placeholder")

    st.divider()

    # Download sample
    sample_csv = """kecamatan,potensi,realisasi
Citeureup,33537,26829
Babakan Madang,18105,14484
Sukamakmur,13622,10897
Caringin,20863,16690
Cijeruk,14656,11724
Cibinong,25000,20000"""

    st.download_button(
        "📥 Download Contoh CSV",
        data=sample_csv,
        file_name="contoh_data.csv",
        mime="text/csv"
    )

# Main Content
if df is not None and not df.empty:
    # Clean and prepare data
    try:
        # Standardize column names
        df.columns = [col.lower() for col in df.columns]

        # Show detected columns for debugging
        st.sidebar.info(f"Kolom terdeteksi: {', '.join(df.columns)}")

        # Find relevant columns with better detection
        kec_col = None
        pot_col = None
        real_col = None

        # Detect kecamatan column
        for c in df.columns:
            if any(x in c for x in ['kec', 'wilayah', 'daerah', 'lokasi']):
                kec_col = c
                break

        # Detect potensi column
        for c in df.columns:
            if any(x in c for x in ['potensi', 'pot', 'target', 'nilai']):
                pot_col = c
                break

        # Detect realisasi column (optional)
        for c in df.columns:
            if any(x in c for x in ['realisasi', 'real', 'capaian', 'akuisisi']):
                real_col = c
                break

        # Validate required columns
        if not kec_col:
            st.error(
                "❌ Kolom KECAMATAN tidak ditemukan. Pastikan ada kolom dengan kata 'kecamatan', 'wilayah', atau 'daerah'")
            st.stop()

        if not pot_col:
            st.error(
                "❌ Kolom POTENSI tidak ditemukan. Pastikan ada kolom dengan kata 'potensi', 'target', atau 'nilai'")
            st.stop()

        # Prepare dataframe
        if real_col:
            df = df[[kec_col, pot_col, real_col]].copy()
            df.columns = ['Kecamatan', 'Potensi', 'Realisasi']
            df['Realisasi'] = pd.to_numeric(df['Realisasi'], errors='coerce').fillna(0).astype(int)
        else:
            # No realisasi column - set to 0
            df = df[[kec_col, pot_col]].copy()
            df.columns = ['Kecamatan', 'Potensi']
            df['Realisasi'] = 0
            st.warning("⚠️ Kolom REALISASI tidak ditemukan. Semua realisasi diset ke 0.")

        # Clean data
        df['Kecamatan'] = df['Kecamatan'].str.strip()
        df['Kecamatan'] = df['Kecamatan'].str.replace('Kecamatan ', '', case=False)
        df['Potensi'] = pd.to_numeric(df['Potensi'], errors='coerce').fillna(0).astype(int)

        # Calculate metrics
        df['Sisa'] = df['Potensi'] - df['Realisasi']
        df['Persentase'] = df.apply(
            lambda row: (row['Realisasi'] / row['Potensi'] * 100) if row['Potensi'] > 0 else 0,
            axis=1
        )
        df['Kecamatan_normalized'] = df['Kecamatan'].apply(normalize_name)

        # Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Potensi", f"{df['Potensi'].sum():,}")
        with col2:
            st.metric("Total Realisasi", f"{df['Realisasi'].sum():,}")
        with col3:
            st.metric("Total Sisa", f"{df['Sisa'].sum():,}")
        with col4:
            avg_persen = (df['Realisasi'].sum() / df['Potensi'].sum() * 100) if df['Potensi'].sum() > 0 else 0
            st.metric("Rata-rata Capaian", f"{avg_persen:.1f}%")

        st.divider()

        # Layout: Map + Charts
        col_map, col_chart = st.columns([3, 2])

        with col_map:
            st.subheader("🗺️ Peta Interaktif Realisasi")

            if geojson_data:
                # Create map
                m = folium.Map(
                    location=[-6.60, 106.85],
                    zoom_start=10,
                    tiles='OpenStreetMap'
                )

                matched = 0
                unmatched = []
                color_palette = get_colorful_palette()
                color_index = 0

                for feature in geojson_data.get('features', []):
                    kecamatan_name = (
                            feature['properties'].get('NAME_3') or
                            feature['properties'].get('name') or
                            feature['properties'].get('NAMOBJ') or
                            "Unknown"
                    )

                    kec_normalized = normalize_name(kecamatan_name)
                    kecamatan_data = df[df['Kecamatan_normalized'] == kec_normalized]

                    if not kecamatan_data.empty:
                        matched += 1
                        row = kecamatan_data.iloc[0]
                        potensi = row['Potensi']
                        realisasi = row['Realisasi']
                        sisa = row['Sisa']
                        persen = row['Persentase']

                        # Gunakan warna warni untuk peta
                        map_color = color_palette[color_index % len(color_palette)]
                        color_index += 1

                        # Warna progress bar di popup tetap berdasarkan persentase
                        progress_color = get_color_by_percentage(persen)

                        popup_html = f"""
                        <div style='font-family: Arial; width: 220px;'>
                            <h4 style='margin: 0; color: #004aad;'>{kecamatan_name}</h4>
                            <hr style='margin: 5px 0;'>
                            <table style='width:100%; font-size:13px;'>
                                <tr><td><b>Potensi:</b></td><td style='text-align:right;'>{potensi:,}</td></tr>
                                <tr><td><b>Realisasi:</b></td><td style='text-align:right;'>{realisasi:,}</td></tr>
                                <tr><td><b>Sisa:</b></td><td style='text-align:right;'>{sisa:,}</td></tr>
                                <tr><td><b>Capaian:</b></td><td style='text-align:right;'><b>{persen:.1f}%</b></td></tr>
                            </table>
                            <div style='margin-top:8px; background:#eee; height:12px; border-radius:6px; overflow:hidden;'>
                                <div style='background:{progress_color}; height:100%; width:{persen:.1f}%;'></div>
                            </div>
                        </div>
                        """

                        folium.GeoJson(
                            feature,
                            style_function=lambda x, color=map_color: {
                                'fillColor': color,
                                'color': 'white',
                                'weight': 2,
                                'fillOpacity': 0.7
                            },
                            tooltip=f"<b>{kecamatan_name}</b><br>Capaian: {persen:.1f}%",
                            popup=folium.Popup(popup_html, max_width=280)
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
                            tooltip=f"<b>{kecamatan_name}</b><br>(Tidak ada data)"
                        ).add_to(m)

                folium_static(m, width=None, height=600)

                st.info(f"✅ Matched: {matched}/{len(geojson_data.get('features', []))} kecamatan")

                # Legend
                st.markdown("""
                **Legend Peta:**
                - 🌈 Setiap kecamatan dengan warna berbeda
                - ⚪ Abu-abu: Tidak ada data

                **Legend Progress Bar (di popup):**
                - 🟢 Hijau: ≥80% (Sangat Baik)
                - 🟡 Kuning: 50-79% (Cukup)
                - 🔴 Merah: <50% (Kurang)
                """)

        with col_chart:
            st.subheader("📊 Proporsi Potensi")

            # Pie Chart - hanya untuk kecamatan dengan data
            df_pie = df[df['Potensi'] > 0].sort_values('Potensi', ascending=False)

            if len(df_pie) > 0:
                fig_pie = px.pie(
                    df_pie,
                    values='Potensi',
                    names='Kecamatan',
                    color_discrete_sequence=px.colors.qualitative.Set3,
                    hole=0.3  # Donut chart
                )
                fig_pie.update_traces(
                    textposition='inside',
                    textinfo='label+percent',
                    textfont_size=10,
                    hovertemplate='<b>%{label}</b><br>Potensi: %{value:,}<br>Persentase: %{percent}<extra></extra>'
                )
                fig_pie.update_layout(
                    height=400,
                    showlegend=False,
                    margin=dict(l=10, r=10, t=10, b=10)
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.warning("Tidak ada data potensi untuk ditampilkan")

            st.subheader("📈 Top 10 Kecamatan")

            # Bar Chart - Horizontal
            top10 = df.nlargest(10, 'Potensi').sort_values('Potensi', ascending=True)

            fig_bar = go.Figure()

            # Add Potensi bars
            fig_bar.add_trace(go.Bar(
                y=top10['Kecamatan'],
                x=top10['Potensi'],
                name='Potensi',
                orientation='h',
                marker_color='#0074e0',
                text=top10['Potensi'],
                textposition='outside',
                texttemplate='%{text:,}',
                hovertemplate='<b>%{y}</b><br>Potensi: %{x:,}<extra></extra>'
            ))

            # Add Realisasi bars
            fig_bar.add_trace(go.Bar(
                y=top10['Kecamatan'],
                x=top10['Realisasi'],
                name='Realisasi',
                orientation='h',
                marker_color='#28a745',
                text=top10['Realisasi'],
                textposition='inside',
                texttemplate='%{text:,}',
                hovertemplate='<b>%{y}</b><br>Realisasi: %{x:,}<extra></extra>'
            ))

            fig_bar.update_layout(
                barmode='overlay',
                height=450,
                xaxis_title="Jumlah",
                yaxis_title="",
                font=dict(size=11),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                margin=dict(l=10, r=10, t=30, b=10)
            )

            st.plotly_chart(fig_bar, use_container_width=True)

        # Table Section
        st.divider()
        st.subheader("📋 Tabel Monitoring Lengkap")


        # Add progress bar HTML
        def create_progress_html(persen):
            color = get_color_by_percentage(persen)
            return f"""
            <div style='background:#eee; border-radius:8px; height:20px; overflow:hidden;'>
                <div style='background:{color}; height:100%; width:{persen:.1f}%; 
                     color:white; text-align:center; font-size:11px; font-weight:bold;
                     line-height:20px;'>{persen:.1f}%</div>
            </div>
            """


        df_display = df[['Kecamatan', 'Potensi', 'Realisasi', 'Sisa', 'Persentase']].copy()
        df_display = df_display.sort_values('Persentase', ascending=False).reset_index(drop=True)
        df_display.index = df_display.index + 1

        # Format numbers
        df_display['Potensi'] = df_display['Potensi'].apply(lambda x: f"{x:,}")
        df_display['Realisasi'] = df_display['Realisasi'].apply(lambda x: f"{x:,}")
        df_display['Sisa'] = df_display['Sisa'].apply(lambda x: f"{x:,}")
        df_display['Progress'] = df_display['Persentase'].apply(create_progress_html)

        st.markdown(
            df_display[['Kecamatan', 'Potensi', 'Realisasi', 'Sisa', 'Progress']].to_html(escape=False, index=True),
            unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error processing data: {str(e)}")
        st.exception(e)

else:
    # Initial state
    st.info("👆 Konfigurasi data source di sidebar untuk memulai")

    st.markdown("### 📖 Fitur Dashboard")
    st.markdown("""
    **Visualisasi:**
    - 🗺️ Peta interaktif dengan warna berdasarkan persentase realisasi
    - 📊 Pie chart proporsi potensi
    - 📈 Bar chart perbandingan potensi vs realisasi
    - 📋 Tabel monitoring dengan progress bar

    **Integrasi:**
    - ☁️ Google Sheets (real-time)
    - 📂 Upload file CSV/Excel
    - 🗺️ GeoJSON untuk batas administratif akurat

    **Fitur:**
    - ✅ Auto-refresh dari Google Sheets
    - ✅ Warna dinamis: Hijau (≥80%), Kuning (50-79%), Merah (<50%)
    - ✅ Wilayah tanpa data ditampilkan abu-abu
    - ✅ Popup detail di peta dengan progress bar
    """)

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>© 2025 BPJAMSOSTEK - Dashboard Monitoring Akuisisi Potensi Kabupaten Bogor</p>
    </div>
""", unsafe_allow_html=True)