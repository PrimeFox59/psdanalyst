import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import sqlite3
import io
from PIL import Image
import statsmodels.api as sm
from io import BytesIO

# --- Konfigurasi Halaman Streamlit ---
st.set_page_config(
    page_title="PSD Analyst",
    page_icon="icon.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Fungsi-fungsi Database ---
DB_FILE = 'aplikasi_db.sqlite'

def init_db():
    """Menginisialisasi database dan membuat tabel jika belum ada."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        password TEXT,
        role TEXT,
        status TEXT
    )
    """)
    
    # Create features table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS features (
        feature_name TEXT PRIMARY KEY,
        is_enabled INTEGER
    )
    """)
    
    # Insert default features if they don't exist
    default_features = {
        'Histogram': 1,
        'Boxplot': 1,
        'Scatter Plot': 1,
        'Heatmap': 1,
        'Uji Normalitas': 1,
        'Uji Hipotesis': 1,
        'Normalisasi Data': 1,
        'Bantuan': 1,
    }
    for feature, is_enabled in default_features.items():
        cursor.execute("SELECT 1 FROM features WHERE feature_name = ?", (feature,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO features (feature_name, is_enabled) VALUES (?, ?)", (feature, is_enabled))

    # Tambahkan user admin default
    cursor.execute("SELECT 1 FROM users WHERE id = 'Prime'")
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO users (id, password, role, status) VALUES (?, ?, ?, ?)", ('Prime', '666666', 'Admin', 'approved'))
    
    conn.commit()
    conn.close()

def add_user(user_id, password, role='User'):
    """Menambahkan pengguna baru ke tabel users."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    status = 'pending' if role == 'User' else 'approved'
    try:
        cursor.execute("INSERT INTO users (id, password, role, status) VALUES (?, ?, ?, ?)", (user_id, password, role, status))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def check_user(user_id, password):
    """Memeriksa kredensial pengguna."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ? AND password = ?", (user_id, password))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_status(user_id):
    """Mendapatkan status pengguna (pending/approved)."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM users WHERE id = ?", (user_id,))
    status = cursor.fetchone()
    conn.close()
    return status[0] if status else None

def get_user_role(user_id):
    """Mendapatkan peran pengguna (User/Admin)."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
    role = cursor.fetchone()
    conn.close()
    return role[0] if role else None

def approve_user(user_id):
    """Menyetujui pengguna baru."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET status = 'approved' WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    
def get_all_users():
    """Mendapatkan semua pengguna dari tabel users."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, role, status FROM users")
    users = cursor.fetchall()
    conn.close()
    return users
    
def delete_user(user_id):
    """Menghapus pengguna dari database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

def update_user_role(user_id, new_role):
    """Memperbarui peran pengguna."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
    conn.commit()
    conn.close()

def get_feature_status():
    """Mendapatkan status semua fitur dari database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT feature_name, is_enabled FROM features")
    features = cursor.fetchall()
    conn.close()
    return {feature: bool(is_enabled) for feature, is_enabled in features}

def update_feature_status(feature_name, is_enabled):
    """Memperbarui status fitur di database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE features SET is_enabled = ? WHERE feature_name = ?", (int(is_enabled), feature_name))
    conn.commit()
    conn.close()
    
# --- Fungsi Halaman Login dan Register ---
def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            logo_image = Image.open("gambarlogo.png")
            st.image(logo_image, use_container_width=True)
        except FileNotFoundError:
            st.error("File 'gambarlogo.png' tidak ditemukan. Pastikan file ada di folder yang sama.")

    st.subheader("Login")
    
    user_id = st.text_input("ID Pengguna")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        user = check_user(user_id, password)
        if user:
            user_status = get_user_status(user_id)
            if user_status == 'approved':
                st.session_state['logged_in'] = True
                st.session_state['user_id'] = user_id
                st.session_state['user_role'] = get_user_role(user_id)
                st.success(f"Login berhasil! Selamat datang, {user_id}.")
                st.rerun()
            elif user_status == 'pending':
                st.warning("Akun Anda belum disetujui oleh admin. Mohon tunggu.")
            else:
                st.error("Status akun tidak valid. Hubungi admin.")
        else:
            st.error("ID Pengguna atau Password salah.")
    
    st.markdown("---")
    
    # --- Tambahan: Login sebagai Guest ---
    if st.button("Login sebagai Tamu"):
        st.session_state['logged_in'] = True
        st.session_state['user_id'] = 'Guest'
        st.session_state['user_role'] = 'User'
        st.success("Berhasil masuk sebagai Guest!")
        st.rerun()

    # --- Tombol "Buat Akun Baru"
    if st.button("Buat Akun Baru"):
        st.session_state['page'] = 'register' 
        st.rerun()

def register_page():
    st.title("Pendaftaran Akun Baru")
    
    user_id = st.text_input("Masukkan ID Pengguna")
    password = st.text_input("Masukkan Password", type="password")
    password_confirm = st.text_input("Konfirmasi Password", type="password")
    
    if st.button("Daftar"):
        if password != password_confirm:
            st.error("Password tidak cocok.")
        elif not user_id or not password:
            st.error("ID Pengguna dan Password tidak boleh kosong.")
        else:
            if add_user(user_id, password):
                st.success("Pendaftaran berhasil! Akun Anda sedang menunggu persetujuan admin.")
                st.info("Silakan kembali ke halaman login.")
                st.session_state['page'] = 'login'
                st.rerun()
            else:
                st.error("ID Pengguna sudah ada. Silakan pilih ID lain.")
                
    st.markdown("---")
    if st.button("Kembali ke Login"):
        st.session_state['page'] = 'login'
        st.rerun()

# --- Fungsi Halaman Utama Aplikasi ---
def show_main_app():
    col1, col2, col3 = st.columns(3)
    with col1:
        # Menampilkan gambar logo
        try:
            logo_image = Image.open("gambarlogo.png")
            st.image(logo_image, width=300)
        except FileNotFoundError:
            st.error("File 'gambarlogo.png' tidak ditemukan. Pastikan file ada di folder yang sama.")
    
    st.markdown("---")
    st.sidebar.markdown(f"Selamat datang, **{st.session_state['user_id']}**!")

    # --- Sidebar for Data Input and Manipulation ---
    st.sidebar.header("📁 Input Data")
    data_source = st.sidebar.radio("Pilih metode input data:", ["Upload File", "Input Manual"])

    if 'df' not in st.session_state:
        st.session_state['df'] = None
    
    if data_source == "Upload File":
        # Perbarui file uploader untuk mendukung CSV, XLS, dan XLSX
        uploaded_file = st.sidebar.file_uploader("Upload file CSV atau Excel", type=["csv", "xlsx", "xls"])
        
        if uploaded_file is not None:
            # Deteksi jenis file berdasarkan ekstensinya
            file_extension = uploaded_file.name.split('.')[-1]
            
            if file_extension == 'csv':
                st.sidebar.subheader("Pengaturan File CSV")
                separator_option = st.sidebar.selectbox("Pemisah (Delimiter):", [',', ';', '\t'], key="separator_select")
                encoding_option = st.sidebar.selectbox("Encoding:", ['utf-8', 'latin1', 'ISO-8859-1', 'cp1252'], key="encoding_select")
                
                try:
                    st.session_state['df'] = pd.read_csv(uploaded_file, sep=separator_option, encoding=encoding_option)
                    st.sidebar.success("File CSV berhasil diunggah dan dibaca!")
                except Exception as e:
                    st.sidebar.error(f"Error saat membaca file CSV: {e}. Coba ganti opsi 'Pemisah' atau 'Encoding'.")

            elif file_extension in ['xlsx', 'xls']:
                st.sidebar.subheader("Pengaturan File Excel")
                try:
                    # Baca semua sheet untuk mendapatkan nama sheet
                    excel_file = pd.ExcelFile(uploaded_file)
                    sheet_names = excel_file.sheet_names
                    
                    selected_sheet = st.sidebar.selectbox("Pilih Sheet:", sheet_names, key="sheet_select")
                    st.session_state['df'] = pd.read_excel(excel_file, sheet_name=selected_sheet)
                    st.sidebar.success(f"File Excel berhasil diunggah dan sheet '{selected_sheet}' berhasil dibaca!")
                except Exception as e:
                    st.sidebar.error(f"Error saat membaca file Excel: {e}. Pastikan format file benar.")
            
            else:
                st.sidebar.warning("Format file tidak didukung.")

    else: # data_source == "Input Manual"
        st.sidebar.info("Gunakan editor dan tombol di sidebar untuk input data manual.")

        if 'manual_df' not in st.session_state:
            st.session_state['manual_df'] = pd.DataFrame({
                'Grup': ['Sample1', 'Sample2', 'Sample3', 'Sample4', 'Sample5'],
                'A': [10.2, 10.5, 10.4, 10.3, 10.6],
                'B': [11.3, 11.1, 11.2, 11.0, 11.4]
            })
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("⚙️ Atur Data Manual")
        
        if st.sidebar.button("➕ Tambah Baris"):
            current_cols = st.session_state['manual_df'].columns
            new_row = {col: 'new_sample' if st.session_state['manual_df'][col].dtype == 'object' else 0 for col in current_cols}
            st.session_state['manual_df'] = pd.concat([st.session_state['manual_df'], pd.DataFrame([new_row])], ignore_index=True)
            st.rerun()
        
        new_col_name = st.sidebar.text_input("Nama Kolom Baru:", placeholder="e.g., C")
        if st.sidebar.button("➕ Tambah Kolom"):
            if new_col_name and new_col_name not in st.session_state['manual_df'].columns:
                st.session_state['manual_df'][new_col_name] = [0.0] * len(st.session_state['manual_df'])
                st.sidebar.success(f"Kolom '{new_col_name}' berhasil ditambahkan.")
                st.rerun()
            elif new_col_name in st.session_state['manual_df'].columns:
                st.sidebar.warning(f"Kolom '{new_col_name}' sudah ada.")
            else:
                st.sidebar.warning("Nama kolom tidak boleh kosong.")
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("✏️ Ganti Nama Kolom")
        current_cols_options = st.session_state['manual_df'].columns.tolist()
        col_to_rename = st.sidebar.selectbox("Pilih Kolom yang Akan Diganti:", current_cols_options, key="rename_select")
        new_col_name_input = st.sidebar.text_input("Nama Kolom Baru:", placeholder="Nama baru", key="rename_input")

        if st.sidebar.button("✅ Ganti Nama"):
            if new_col_name_input and new_col_name_input not in current_cols_options:
                st.session_state['manual_df'] = st.session_state['manual_df'].rename(columns={col_to_rename: new_col_name_input})
                st.sidebar.success(f"Nama kolom '{col_to_rename}' berhasil diganti menjadi '{new_col_name_input}'.")
                st.rerun()
            elif new_col_name_input in current_cols_options:
                st.sidebar.warning(f"Nama '{new_col_name_input}' sudah digunakan. Pilih nama lain.")
            else:
                st.sidebar.warning("Nama baru tidak boleh kosong.")
        
        st.session_state['df'] = st.session_state['manual_df']

    # Log out button
    if st.sidebar.button("Keluar"):
        st.session_state['logged_in'] = False
        st.session_state['user_id'] = None
        st.session_state['user_role'] = None
        st.session_state['df'] = None  # Clear data on logout
        st.rerun()

    # --- Main Content with Tabs ---
    if st.session_state['df'] is not None:
        
        # Dapatkan status fitur dari database
        feature_status = get_feature_status()
        
        # Buat daftar tab secara dinamis
        tabs_list = ["📝 Input Data", "🛠️ Analisis Data"]
        if feature_status.get('Bantuan', True): # Tampilkan tab Bantuan jika diaktifkan
            tabs_list.append("❓ Bantuan")
        if st.session_state['user_role'] == 'Admin':
            tabs_list.append("⚙️ Admin Setting")

        # Buat tab
        tabs = st.tabs(tabs_list)
        
        # Menggunakan loop dan if untuk menghindari error unpacking
        tab_mapping = {name: i for i, name in enumerate(tabs_list)}

        with tabs[tab_mapping["📝 Input Data"]]:
            st.header("Input Data")
            
            col_data, col_desc = st.columns(2)

            with col_data:
                if data_source == "Input Manual":
                    st.subheader("Data Manual")
                    edited_df = st.data_editor(st.session_state['df'], num_rows="dynamic", use_container_width=True)
                    st.session_state['df'] = edited_df
                else:
                    st.subheader("Data yang Diunggah")
                    st.dataframe(st.session_state['df'], use_container_width=True)

            with col_desc:
                st.subheader("Statistik Deskriptif")
                st.dataframe(st.session_state['df'].describe(), use_container_width=True)

            st.markdown("---")
            
            with st.expander("📈 Visualisasi Data"):
                st.write("Visualisasi Data:")
                numeric_cols = st.session_state['df'].select_dtypes(include=np.number).columns.tolist()
                
                if not numeric_cols:
                    st.warning("Tidak ada kolom numerik untuk divisualisasikan.")
                else:
                    enabled_plot_options = []
                    if feature_status['Histogram']:
                        enabled_plot_options.append("Histogram")
                    if feature_status['Boxplot']:
                        enabled_plot_options.append("Boxplot")
                    if feature_status['Scatter Plot']:
                        enabled_plot_options.append("Scatter Plot")
                    if feature_status['Heatmap']:
                        enabled_plot_options.append("Heatmap")

                    if not enabled_plot_options:
                        st.warning("Tidak ada fitur visualisasi yang diaktifkan oleh admin.")
                    else:
                        plot_type = st.selectbox("Pilih Jenis Grafik:", enabled_plot_options)
                        
                        if plot_type != "Heatmap":
                            plot_mode = st.radio("Pilih Tampilan Grafik:", ["Grafik Terpisah", "Satu Grafik"])
                        else:
                            plot_mode = "Satu Grafik"
                        
                        st.subheader("Pengaturan Ukuran Grafik")
                        if plot_type == "Heatmap":
                            plot_width = st.slider("Lebar Grafik", 4, 20, 10, key="plot_width_heatmap")
                            plot_height = st.slider("Tinggi Grafik", 3, 15, 8, key="plot_height_heatmap")
                        elif plot_mode == "Grafik Terpisah":
                            plot_width = st.slider("Lebar Grafik", 4, 15, 8, key="plot_width_general")
                            plot_height = st.slider("Tinggi Grafik", 3, 10, 5, key="plot_height_general")
                        else: # Satu Grafik
                            plot_width = st.slider("Lebar Grafik", 4, 20, 15, key="plot_width_single")
                            plot_height = st.slider("Tinggi Grafik", 3, 15, 8, key="plot_height_single")

                        if plot_type == "Heatmap":
                            if len(numeric_cols) < 2:
                                st.warning("Diperlukan setidaknya dua kolom numerik untuk membuat Heatmap.")
                            else:
                                st.markdown("#### Heatmap Korelasi")
                                
                                selected_cols = st.multiselect(
                                    "Pilih kolom numerik untuk heatmap:",
                                    options=numeric_cols,
                                    default=numeric_cols
                                )

                                if selected_cols:
                                    df_selected = st.session_state['df'][selected_cols].copy()
                                    corr_matrix = df_selected.corr()

                                    fig, ax = plt.subplots(figsize=(plot_width, plot_height))
                                    sns.heatmap(
                                        corr_matrix,
                                        annot=True,
                                        cmap='coolwarm',
                                        fmt=".2f",
                                        linewidths=.5,
                                        ax=ax
                                    )
                                    ax.set_title("Matriks Korelasi Heatmap", fontsize=16)
                                    st.pyplot(fig)

                                    buf = BytesIO()
                                    fig.savefig(buf, format="png", bbox_inches="tight")
                                    st.download_button(
                                        label="⬇️ Unduh Heatmap (PNG)",
                                        data=buf.getvalue(),
                                        file_name="heatmap_korelasi.png",
                                        mime="image/png"
                                    )

                                    st.markdown("---")
                                    st.subheader("📋 Matriks Korelasi")
                                    st.dataframe(corr_matrix.style.background_gradient(cmap='coolwarm'), use_container_width=True)
                                else:
                                    st.info("✅ Silakan pilih minimal dua kolom untuk membuat Heatmap.")
                        
                        elif plot_mode == "Grafik Terpisah":
                            if plot_type == "Histogram":
                                for col in numeric_cols:
                                    st.markdown(f"#### Distribusi untuk Kolom: **{col}**")
                                    fig, ax = plt.subplots(figsize=(plot_width, plot_height))
                                    st.session_state['df'][col].hist(ax=ax, bins=20, edgecolor='black')
                                    ax.set_title(f'Histogram untuk {col}')
                                    ax.set_xlabel(col)
                                    ax.set_ylabel('Frekuensi')
                                    st.pyplot(fig)
                            
                            elif plot_type == "Boxplot":
                                for col in numeric_cols:
                                    st.markdown(f"#### Boxplot untuk Kolom: **{col}**")
                                    fig, ax = plt.subplots(figsize=(plot_width, plot_height))
                                    sns.boxplot(y=st.session_state['df'][col], ax=ax)
                                    ax.set_title(f'Boxplot untuk {col}')
                                    ax.set_ylabel(col)
                                    st.pyplot(fig)
                            
                            elif plot_type == "Scatter Plot":
                                if len(numeric_cols) < 2:
                                    st.warning("Diperlukan setidaknya dua kolom numerik untuk membuat Scatter Plot.")
                                else:
                                    x_col = st.selectbox("Pilih Kolom untuk Sumbu X:", numeric_cols, key="x_col")
                                    y_col = st.selectbox("Pilih Kolom untuk Sumbu Y:", numeric_cols, key="y_col")
                                    
                                    st.markdown(f"#### Scatter Plot: {y_col} vs {x_col}")
                                    fig, ax = plt.subplots(figsize=(plot_width, plot_height))
                                    sns.scatterplot(data=st.session_state['df'], x=x_col, y=y_col, ax=ax)
                                    ax.set_title(f'Scatter Plot {y_col} vs {x_col}')
                                    ax.set_xlabel(x_col)
                                    ax.set_ylabel(y_col)
                                    st.pyplot(fig)
                        
                        else: # plot_mode == "Satu Grafik"
                            if plot_type == "Histogram":
                                st.markdown("#### Histogram Semua Kolom dalam Satu Grafik")
                                fig, ax = plt.subplots(figsize=(plot_width, plot_height))
                                st.session_state['df'][numeric_cols].hist(ax=ax)
                                fig.suptitle("Histogram Semua Kolom", fontsize=16)
                                st.pyplot(fig)

                            elif plot_type == "Boxplot":
                                st.markdown("#### Boxplot Semua Kolom dalam Satu Grafik")
                                fig, ax = plt.subplots(figsize=(plot_width, plot_height))
                                sns.boxplot(data=st.session_state['df'][numeric_cols], ax=ax)
                                ax.set_title('Boxplot Semua Kolom')
                                st.pyplot(fig)

                            elif plot_type == "Scatter Plot":
                                st.markdown("#### Pairplot / Scatter Plot Matrix")
                                st.info("Visualisasi ini menunjukkan hubungan antara semua pasangan kolom numerik.")
                                fig = sns.pairplot(st.session_state['df'][numeric_cols])
                                st.pyplot(fig)

        with tabs[tab_mapping["🛠️ Analisis Data"]]:
            st.header("Fitur Analisis Data")
            
            numeric_cols = st.session_state['df'].select_dtypes(include=np.number).columns.tolist()
            if not numeric_cols:
                st.warning("Data tidak memiliki kolom numerik. Silakan periksa tab 'Input Data' untuk memasukkan data yang valid.")
            
            enabled_analysis_options = []
            if feature_status['Normalisasi Data']:
                enabled_analysis_options.append("Normalisasi Data")
            if feature_status['Uji Hipotesis']:
                enabled_analysis_options.append("Uji Hipotesis")
            if feature_status['Uji Normalitas']:
                enabled_analysis_options.append("Uji Normalitas")

            if not enabled_analysis_options:
                st.warning("Tidak ada fitur analisis yang diaktifkan oleh admin.")
            else:
                analysis_type = st.radio("Pilih jenis analisis:", enabled_analysis_options)
        
                if analysis_type == "Uji Hipotesis":
                    st.subheader("🔬 Pilih Jenis Uji Hipotesis")
                    test_type = st.selectbox("Jenis Uji:", [
                        "Uji-t 1 Sampel", "Uji-t 2 Sampel (Independent)", "Uji-t Paired",
                        "Uji-z 1 Sampel", "Uji Proporsi 1 Sampel", "Uji Proporsi 2 Sampel",
                        "Uji Varians (F-Test)", "ANOVA 1 Arah",
                        "Mann-Whitney U", "Wilcoxon Signed-Rank"
                    ])
                    
                    alpha = st.slider("Tingkat Signifikansi (α):", 0.01, 0.10, 0.05, 0.01)
            
                    if test_type == "Uji-t 1 Sampel":
                        if numeric_cols:
                            column = st.selectbox("Kolom yang diuji:", numeric_cols)
                            mu = st.number_input("Masukkan nilai rata-rata populasi (μ₀):", value=0.0)
                            t_stat, p_val = stats.ttest_1samp(st.session_state['df'][column].dropna(), mu, nan_policy='omit')
                            st.info(f"**Hasil Uji-t 1 Sampel:**")
                            st.write(f"t-statistik = `{t_stat:.4f}`")
                            st.write(f"p-value = `{p_val:.4f}`")
                            if p_val < alpha:
                                st.success(f"**Kesimpulan:** Tolak H₀ (Terdapat perbedaan signifikan) karena p-value < α ({alpha}).")
                            else:
                                st.error(f"**Kesimpulan:** Gagal tolak H₀ (Tidak ada perbedaan signifikan) karena p-value ≥ α ({alpha}).")
                        else:
                            st.warning("Tidak ada kolom numerik yang tersedia.")
            
                    elif test_type == "Uji-t 2 Sampel (Independent)":
                        if len(numeric_cols) >= 2:
                            col1 = st.selectbox("Pilih kolom grup 1:", numeric_cols, key='ttest_ind_1')
                            col2 = st.selectbox("Pilih kolom grup 2:", numeric_cols, key='ttest_ind_2')
                            if col1 != col2:
                                t_stat, p_val = stats.ttest_ind(st.session_state['df'][col1].dropna(), st.session_state['df'][col2].dropna(), nan_policy='omit')
                                st.info(f"**Hasil Uji-t 2 Sampel:**")
                                st.write(f"t-statistik = `{t_stat:.4f}`")
                                st.write(f"p-value = `{p_val:.4f}`")
                                if p_val < alpha:
                                    st.success(f"**Kesimpulan:** Tolak H₀ (Ada perbedaan rata-rata signifikan) karena p-value < α ({alpha}).")
                                else:
                                    st.error(f"**Kesimpulan:** Gagal tolak H₀ (Tidak ada perbedaan rata-rata signifikan) karena p-value ≥ α ({alpha}).")
                            else:
                                st.warning("Pilih dua kolom yang berbeda.")
                        else:
                            st.warning("Diperlukan setidaknya dua kolom numerik.")
            
                    elif test_type == "Uji-t Paired":
                        if len(numeric_cols) >= 2:
                            col1 = st.selectbox("Pilih kolom pertama:", numeric_cols, key='ttest_paired_1')
                            col2 = st.selectbox("Pilih kolom kedua:", numeric_cols, key='ttest_paired_2')
                            if col1 != col2:
                                t_stat, p_val = stats.ttest_rel(st.session_state['df'][col1].dropna(), st.session_state['df'][col2].dropna())
                                st.info(f"**Hasil Uji-t Paired:**")
                                st.write(f"t-statistik = `{t_stat:.4f}`")
                                st.write(f"p-value = `{p_val:.4f}`")
                                if p_val < alpha:
                                    st.success(f"**Kesimpulan:** Tolak H₀ (Ada perbedaan signifikan antar pasangan) karena p-value < α ({alpha}).")
                                else:
                                    st.error(f"**Kesimpulan:** Gagal tolak H₀ (Tidak ada perbedaan signifikan antar pasangan) karena p-value ≥ α ({alpha}).")
                            else:
                                st.warning("Pilih dua kolom yang berbeda.")
                        else:
                            st.warning("Diperlukan setidaknya dua kolom numerik.")
            
                    elif test_type == "Uji-z 1 Sampel":
                        if numeric_cols:
                            column = st.selectbox("Kolom yang diuji:", numeric_cols)
                            mu = st.number_input("Masukkan nilai rata-rata populasi (μ₀):", value=0.0)
                            sigma = st.number_input("Masukkan standar deviasi populasi (σ):", value=1.0)
                            data_to_test = st.session_state['df'][column].dropna()
                            n = len(data_to_test)
                            if n > 0 and sigma > 0:
                                x_bar = np.mean(data_to_test)
                                z = (x_bar - mu) / (sigma / np.sqrt(n))
                                p_val = 2 * (1 - stats.norm.cdf(abs(z)))
                                st.info(f"**Hasil Uji-z 1 Sampel:**")
                                st.write(f"z-statistik = `{z:.4f}`")
                                st.write(f"p-value = `{p_val:.4f}`")
                                if p_val < alpha:
                                    st.success(f"**Kesimpulan:** Tolak H₀ karena p-value < α ({alpha}).")
                                else:
                                    st.error(f"**Kesimpulan:** Gagal tolak H₀ karena p-val > α ({alpha}).")
                            else:
                                st.warning("Data atau standar deviasi tidak valid.")
                        else:
                            st.warning("Tidak ada kolom numerik yang tersedia.")
            
                    elif test_type == "Uji Proporsi 1 Sampel":
                        x = st.number_input("Jumlah sukses (x):", min_value=0, step=1)
                        n = st.number_input("Jumlah total sampel (n):", min_value=1, step=1)
                        p0 = st.number_input("Proporsi populasi (p₀):", min_value=0.0, max_value=1.0, value=0.5)
                        if n > 0 and p0 > 0 and p0 < 1:
                            p_hat = x / n
                            se = np.sqrt(p0 * (1 - p0) / n)
                            if se > 0:
                                z = (p_hat - p0) / se
                                p_val = 2 * (1 - stats.norm.cdf(abs(z)))
                                st.info(f"**Hasil Uji Proporsi 1 Sampel:**")
                                st.write(f"z-statistik = `{z:.4f}`")
                                st.write(f"p-value = `{p_val:.4f}`")
                                if p_val < alpha:
                                    st.success(f"**Kesimpulan:** Tolak H₀ karena p-value < α ({alpha}).")
                                else:
                                    st.error(f"**Kesimpulan:** Gagal tolak H₀ karena p-val > α ({alpha}).")
                            else:
                                st.warning("Nilai standar error tidak valid.")
                        else:
                            st.warning("Nilai input tidak valid.")
            
                    elif test_type == "Uji Proporsi 2 Sampel":
                        x1 = st.number_input("Jumlah sukses grup 1:", min_value=0, step=1)
                        n1 = st.number_input("Jumlah sampel grup 1:", min_value=1, step=1)
                        x2 = st.number_input("Jumlah sukses grup 2:", min_value=0, step=1)
                        n2 = st.number_input("Jumlah sampel grup 2:", min_value=1, step=1)
                        if n1 > 0 and n2 > 0 and (x1+x2) > 0 and (n1+n2) > (x1+x2):
                            p1 = x1 / n1
                            p2 = x2 / n2
                            p_pool = (x1 + x2) / (n1 + n2)
                            se_pool = np.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
                            if se_pool > 0:
                                z = (p1 - p2) / se_pool
                                p_val = 2 * (1 - stats.norm.cdf(abs(z)))
                                st.info(f"**Hasil Uji Proporsi 2 Sampel:**")
                                st.write(f"z-statistik = `{z:.4f}`")
                                st.write(f"p-value = `{p_val:.4f}`")
                                if p_val < alpha:
                                    st.success(f"**Kesimpulan:** Tolak H₀ karena p-value < α ({alpha}).")
                                else:
                                    st.error(f"**Kesimpulan:** Gagal tolak H₀ karena p-val > α ({alpha}).")
                            else:
                                st.warning("Nilai standar error tidak valid.")
                        else:
                            st.warning("Nilai input tidak valid.")
            
                    elif test_type == "Uji Varians (F-Test)":
                        if len(numeric_cols) >= 2:
                            col1 = st.selectbox("Pilih kolom grup 1:", numeric_cols, key='ftest_1')
                            col2 = st.selectbox("Pilih kolom grup 2:", numeric_cols, key='ftest_2')
                            if col1 != col2:
                                data1 = st.session_state['df'][col1].dropna()
                                data2 = st.session_state['df'][col2].dropna()
                                var1 = np.var(data1, ddof=1)
                                var2 = np.var(data2, ddof=1)
                                
                                if var1 == 0 or var2 == 0:
                                    st.warning("Salah satu varian adalah nol. Uji F tidak dapat dilakukan.")
                                else:
                                    if var1 >= var2:
                                        f_stat = var1 / var2
                                        dfn = len(data1) - 1
                                        dfd = len(data2) - 1
                                    else:
                                        f_stat = var2 / var1
                                        dfn = len(data2) - 1
                                        dfd = len(data1) - 1
            
                                    p_val = 2 * min(stats.f.cdf(f_stat, dfn, dfd), 1 - stats.f.cdf(f_stat, dfn, dfd))
                                    st.info(f"**Hasil Uji Varians (F-Test):**")
                                    st.write(f"F-statistik = `{f_stat:.4f}`, df1 = `{dfn}`, df2 = `{dfd}`")
                                    st.write(f"p-value = `{p_val:.4f}`")
                                    if p_val < alpha:
                                        st.success(f"**Kesimpulan:** Tolak H₀ (Terdapat perbedaan varians) karena p-value < α ({alpha}).")
                                    else:
                                        st.error(f"**Kesimpulan:** Gagal tolak H₀ (Tidak ada perbedaan varians) karena p-value ≥ α ({alpha}).")
                            else:
                                st.warning("Pilih dua kolom yang berbeda.")
                        else:
                            st.warning("Diperlukan setidaknya dua kolom numerik.")
            
                    elif test_type == "ANOVA 1 Arah":
                        cols = st.multiselect("Pilih kolom numerik:", numeric_cols)
                        if len(cols) > 1:
                            samples = [st.session_state['df'][col].dropna() for col in cols]
                            f_stat, p_val = stats.f_oneway(*samples)
                            st.info(f"**Hasil ANOVA 1 Arah:**")
                            st.write(f"F-statistik = `{f_stat:.4f}`")
                            st.write(f"p-value = `{p_val:.4f}`")
                            if p_val < alpha:
                                st.success(f"**Kesimpulan:** Tolak H₀ (Ada perbedaan rata-rata signifikan) karena p-value < α ({alpha}).")
                            else:
                                st.error(f"**Kesimpulan:** Gagal tolak H₀ (Tidak ada perbedaan rata-rata signifikan) karena p-value ≥ α ({alpha}).")
                        else:
                            st.warning("Pilih setidaknya dua kolom.")
            
                    elif test_type == "Mann-Whitney U":
                        if len(numeric_cols) >= 2:
                            col1 = st.selectbox("Pilih kolom grup 1:", numeric_cols, key='mann_whitney_1')
                            col2 = st.selectbox("Pilih kolom grup 2:", numeric_cols, key='mann_whitney_2')
                            if col1 != col2:
                                u_stat, p_val = stats.mannwhitneyu(st.session_state['df'][col1].dropna(), st.session_state['df'][col2].dropna(), alternative='two-sided')
                                st.info(f"**Hasil Uji Mann-Whitney U:**")
                                st.write(f"U-statistik = `{u_stat:.4f}`")
                                st.write(f"p-value = `{p_val:.4f}`")
                                if p_val < alpha:
                                    st.success(f"**Kesimpulan:** Tolak H₀ (Ada perbedaan distribusi) karena p-value < α ({alpha}).")
                                else:
                                    st.error(f"**Kesimpulan:** Gagal tolak H₀ (Tidak ada perbedaan distribusi) karena p-value ≥ α ({alpha}).")
                            else:
                                st.warning("Pilih dua kolom yang berbeda.")
                        else:
                            st.warning("Diperlukan setidaknya dua kolom numerik.")
            
                    elif test_type == "Wilcoxon Signed-Rank":
                        if len(numeric_cols) >= 2:
                            col1 = st.selectbox("Pilih kolom pertama:", numeric_cols, key='wilcoxon_1')
                            col2 = st.selectbox("Pilih kolom kedua:", numeric_cols, key='wilcoxon_2')
                            if col1 != col2:
                                w_stat, p_val = stats.wilcoxon(st.session_state['df'][col1].dropna(), st.session_state['df'][col2].dropna())
                                st.info(f"**Hasil Uji Wilcoxon Signed-Rank:**")
                                st.write(f"W-statistik = `{w_stat:.4f}`")
                                st.write(f"p-value = `{p_val:.4f}`")
                                if p_val < alpha:
                                    st.success(f"**Kesimpulan:** Tolak H₀ (Ada perbedaan distribusi antar pasangan) karena p-value < α ({alpha}).")
                                else:
                                    st.error(f"**Kesimpulan:** Gagal tolak H₀ (Tidak ada perbedaan distribusi antar pasangan) karena p-value ≥ α ({alpha}).")
                            else:
                                st.warning("Pilih dua kolom yang berbeda.")
                        else:
                            st.warning("Diperlukan setidaknya dua kolom numerik.")
                
                elif analysis_type == "Uji Normalitas":
                    st.subheader("🧪 Uji Normalitas Data")
                    if numeric_cols:
                        column = st.selectbox("Pilih kolom untuk uji normalitas:", numeric_cols)
                        test_method = st.selectbox("Pilih metode uji:", [
                            "Shapiro-Wilk", 
                            "Kolmogorov-Smirnov", 
                            "Anderson-Darling", 
                            "Ryan-Joiner", 
                            "D'Agostino's K²"
                        ])
                        
                        data_to_test = st.session_state['df'][column].dropna()
                        
                        if data_to_test.empty:
                            st.warning("Kolom yang dipilih tidak memiliki data.")
                        else:
                            if test_method == "Shapiro-Wilk":
                                stat, p_val = stats.shapiro(data_to_test)
                                st.info(f"**Hasil Uji Shapiro-Wilk:**")
                                st.write(f"W-statistik = `{stat:.4f}`")
                                st.write(f"p-value = `{p_val:.4f}`")
                                if p_val > 0.05:
                                    st.success("**Kesimpulan:** Data **normal** (Gagal tolak H₀) karena p-value > 0.05.")
                                else:
                                    st.error("**Kesimpulan:** Data **tidak normal** (Tolak H₀) karena p-value ≤ 0.05.")

                            elif test_method == "Ryan-Joiner":
                                st.info("Catatan: Fungsi bawaan Python untuk Ryan-Joiner tidak tersedia. "
                                    "Kami menggunakan Uji Shapiro-Wilk, yang memberikan hasil sangat mirip.")
                                stat, p_val = stats.shapiro(data_to_test)
                                st.info(f"**Hasil Uji Ryan-Joiner (menggunakan Shapiro-Wilk):**")
                                st.write(f"W-statistik = `{stat:.4f}`")
                                st.write(f"p-value = `{p_val:.4f}`")
                                if p_val > 0.05:
                                    st.success("**Kesimpulan:** Data **normal** (Gagal tolak H₀) karena p-value > 0.05.")
                                else:
                                    st.error("**Kesimpulan:** Data **tidak normal** (Tolak H₀) karena p-value ≤ 0.05.")

                            elif test_method == "Kolmogorov-Smirnov":
                                mean = data_to_test.mean()
                                std = data_to_test.std()
                                stat, p_val = stats.kstest(data_to_test, 'norm', args=(mean, std))
                                st.info(f"**Hasil Uji Kolmogorov-Smirnov:**")
                                st.write(f"D-statistik = `{stat:.4f}`")
                                st.write(f"p-value = `{p_val:.4f}`")
                                if p_val > 0.05:
                                    st.success("**Kesimpulan:** Data **normal** (Gagal tolak H₀) karena p-value > 0.05.")
                                else:
                                    st.error("**Kesimpulan:** Data **tidak normal** (Tolak H₀) karena p-value ≤ 0.05.")

                            elif test_method == "Anderson-Darling":
                                result = stats.anderson(data_to_test, dist='norm')
                                st.info(f"**Hasil Uji Anderson-Darling:**")
                                st.write(f"A-statistik = `{result.statistic:.4f}`")
                                st.write("Nilai Kritis:")
                                
                                for i in range(len(result.critical_values)):
                                    st.write(f"  - Tingkat Signifikansi: {result.significance_level[i]}% -> Nilai Kritis: {result.critical_values[i]:.4f}")
                                
                                st.write("---")
                                is_normal = True
                                for i in range(len(result.critical_values)):
                                    if result.statistic > result.critical_values[i]:
                                        is_normal = False
                                        break
                                
                                if is_normal:
                                    st.success("**Kesimpulan:** Data **normal** (A-statistik < nilai kritis pada semua tingkat signifikansi yang diuji).")
                                else:
                                    st.error("**Kesimpulan:** Data **tidak normal** (A-statistik > nilai kritis pada tingkat signifikansi terkecil).")

                            elif test_method == "D'Agostino's K²":
                                stat, p_val = stats.normaltest(data_to_test)
                                st.info(f"**Hasil Uji D'Agostino's K²:**")
                                st.write(f"K²-statistik = `{stat:.4f}`")
                                st.write(f"p-value = `{p_val:.4f}`")
                                if p_val > 0.05:
                                    st.success("**Kesimpulan:** Data **normal** (Gagal tolak H₀) karena p-value > 0.05.")
                                else:
                                    st.error("**Kesimpulan:** Data **tidak normal** (Tolak H₀) karena p-value ≤ 0.05.")
                            
                            st.markdown("---")
                            st.subheader("Visualisasi Q-Q Plot")
                            
                            st.subheader("Pengaturan Ukuran Grafik")
                            plot_width = st.slider("Lebar Grafik", 4, 15, 8, key="plot_width_qq")
                            plot_height = st.slider("Tinggi Grafik", 3, 10, 5, key="plot_height_qq")

                            fig, ax = plt.subplots(figsize=(plot_width, plot_height))
                            sm.qqplot(data_to_test, line='s', ax=ax)
                            ax.set_title(f"Q-Q Plot untuk Kolom '{column}'")
                            st.pyplot(fig)
            
                    else:
                        st.warning("Tidak ada kolom numerik yang tersedia.")
            
                elif analysis_type == "Normalisasi Data":
                    st.subheader("🔄 Normalisasi & Transformasi Data")
                    if numeric_cols:
                        column_to_normalize = st.selectbox("Pilih kolom untuk diproses:", numeric_cols)
                        transform_method = st.selectbox("Pilih metode:", ["Min-Max Scaling", "Standardize (Z-Score)", "Box-Cox Transform", "Log Transform"])

                        st.markdown("---")
                        if st.button("Lakukan Transformasi"):
                            original_data = st.session_state['df'][column_to_normalize].dropna()
                            
                            if original_data.empty:
                                st.warning("Kolom yang dipilih tidak memiliki data.")
                            else:
                                transformed_data = None
                                method_name = ""

                                if transform_method == "Min-Max Scaling":
                                    min_val = original_data.min()
                                    max_val = original_data.max()
                                    if max_val - min_val == 0:
                                        st.error("Kolom memiliki nilai konstan, tidak dapat di-Min-Max Scaling.")
                                    else:
                                        transformed_data = (original_data - min_val) / (max_val - min_val)
                                        method_name = "Min-Max Scaling"
                                
                                elif transform_method == "Standardize (Z-Score)":
                                    mean_val = original_data.mean()
                                    std_val = original_data.std()
                                    if std_val == 0:
                                        st.error("Kolom memiliki standar deviasi nol, tidak dapat di-Standardize.")
                                    else:
                                        transformed_data = (original_data - mean_val) / std_val
                                        method_name = "Standardize (Z-Score)"

                                elif transform_method == "Log Transform":
                                    if (original_data <= 0).any():
                                        st.error("Log Transform hanya dapat digunakan pada data dengan nilai positif.")
                                    else:
                                        transformed_data = np.log(original_data)
                                        method_name = "Log Transform"
                                
                                elif transform_method == "Box-Cox Transform":
                                    if (original_data <= 0).any():
                                        st.error("Box-Cox Transform hanya dapat digunakan pada data dengan nilai positif.")
                                    else:
                                        try:
                                            transformed_data, _ = stats.boxcox(original_data)
                                            method_name = "Box-Cox Transform"
                                        except Exception as e:
                                            st.error(f"Gagal melakukan Box-Cox Transform: {e}")
                                            transformed_data = None

                                if transformed_data is not None:
                                    st.info(f"Data berhasil diproses dengan **{method_name}**.")
                                    
                                    col_original, col_transformed = st.columns(2)
                                    with col_original:
                                        st.subheader("Data Asli")
                                        st.write(original_data)
                                    with col_transformed:
                                        st.subheader("Data Hasil Transformasi")
                                        st.write(transformed_data)
                                        
                                    st.markdown("---")
                                    st.subheader("Perbandingan Distribusi")
                                    
                                    st.subheader("Pengaturan Ukuran Grafik")
                                    plot_width = st.slider("Lebar Grafik", 4, 15, 12, key="plot_width_norm")
                                    plot_height = st.slider("Tinggi Grafik", 3, 10, 5, key="plot_height_norm")
                                    
                                    fig, ax = plt.subplots(ncols=2, figsize=(plot_width, plot_height))
                                    
                                    sns.histplot(original_data, kde=True, ax=ax[0])
                                    ax[0].set_title(f"Distribusi Asli: '{column_to_normalize}'")
                                    
                                    sns.histplot(transformed_data, kde=True, ax=ax[1])
                                    ax[1].set_title(f"Distribusi Setelah {method_name}")
                                    
                                    st.pyplot(fig)
                    else:
                        st.warning("Tidak ada kolom numerik yang tersedia.")
        
        if feature_status.get('Bantuan', True):
            with tabs[tab_mapping["❓ Bantuan"]]:
                st.header("❓ Panduan Penggunaan Aplikasi")
                st.write("Aplikasi ini membantu Anda melakukan analisis data statistik dengan cepat. Berikut adalah panduan untuk setiap fitur yang tersedia, dengan fokus pada penggunaan di **industri manufaktur foundry dan machining**.")
                
                tab_normality, tab_normalization, tab_hypothesis = st.tabs(["Uji Normalitas", "Normalisasi Data", "Uji Hipotesis"])
                
                with tab_normality:
                    st.subheader("Uji Normalitas")
                    st.write("Uji ini digunakan untuk memeriksa apakah data Anda memiliki **distribusi normal (pola sebaran kurva lonceng)**. Normalitas adalah asumsi dasar untuk banyak uji statistik. Data yang normal menunjukkan bahwa proses produksi Anda **stabil** dan variasi yang terjadi masih wajar.")
                    
                    st.markdown("---")
                    st.markdown("#### Kapan Digunakan?")
                    st.markdown("- Untuk memverifikasi apakah data kualitas produk (misalnya, dimensi, kekerasan, berat) dari suatu proses mengikuti pola yang bisa diprediksi.")
                    st.markdown("- Sebelum menggunakan uji parametrik seperti Uji-t atau ANOVA.")
                    st.markdown("- Untuk mengetahui apakah ada faktor khusus yang mempengaruhi hasil, seperti *tools* yang aus atau mesin yang tidak stabil.")

                    st.markdown("---")
                    st.markdown("#### Contoh Kasus di Manufaktur")
                    st.markdown("Anda mengukur **dimensi tebal** (spesifikasi 5 ± 0.1 mm) dari 30 produk coran. Dengan Uji Normalitas, Anda bisa tahu apakah sebaran data ini mengikuti kurva lonceng yang ideal. Jika ya, berarti proses Anda terkendali dan variasi acak.")

                    st.markdown("---")
                    st.markdown("#### Cara Menginterpretasi Hasil")
                    st.markdown("- **p-value > 0.05**: Data Anda dianggap **Normal**. Ini kabar baik! Anda bisa melanjutkan ke analisis statistik lain yang membutuhkan asumsi normalitas.")
                    st.markdown("- **p-value ≤ 0.05**: Data Anda **Tidak Normal**. Artinya ada kemungkinan besar variasi yang terjadi tidak hanya acak. Anda perlu menyelidiki lebih dalam penyebabnya (misalnya, perubahan bahan baku, operator baru, atau masalah pada mesin).")
                    st.markdown("Perhatikan juga **Q-Q Plot**. Jika titik-titik data mengikuti garis lurus, itu adalah konfirmasi visual bahwa data Anda normal.")

                with tab_normalization:
                    st.subheader("Normalisasi & Transformasi Data")
                    st.write("Fitur ini digunakan untuk **mengatur ulang data Anda** agar lebih mudah dianalisis. Ini seperti menyamakan satuan data sehingga Anda bisa membandingkan berbagai jenis data secara adil. Tujuannya adalah untuk mempersiapkan data Anda agar lebih cocok untuk analisis lanjutan.")
                    
                    st.markdown("---")
                    st.markdown("#### Metode dan Kapan Menggunakannya")
                    st.markdown("- **Min-Max Scaling**: Mengubah semua nilai data ke dalam rentang **0 sampai 1**. Cocok untuk membandingkan data dari kolom yang memiliki satuan berbeda (misalnya, **berat** dalam kg dan **kekerasan** dalam HRC).")
                    st.markdown("- **Standardize (Z-Score)**: Mengubah data sehingga memiliki rata-rata **0** dan standar deviasi **1**. Ideal jika data Anda sudah normal dan Anda ingin mengidentifikasi *outlier* (data yang sangat ekstrem).")
                    st.markdown("- **Log Transform**: Menggunakan logaritma untuk data yang sebarannya **miring ke kanan** (nilai kecil banyak, nilai besar sedikit). Contoh: data tentang **jumlah cacat** produk per hari, yang biasanya cenderung memiliki banyak hari dengan cacat nol atau sedikit.")
                    st.markdown("- **Box-Cox Transform**: Metode yang lebih canggih untuk mengubah data menjadi lebih normal. Hanya bisa digunakan pada data dengan nilai positif.")

                with tab_hypothesis:
                    st.subheader("Uji Hipotesis")
                    st.write("Uji ini adalah jantung dari analisis statistik inferensial. Tujuannya adalah untuk **mengambil keputusan tentang populasi** berdasarkan data sampel yang Anda miliki.")
                    
                    st.markdown("---")
                    st.markdown("#### Memahami p-value")
                    st.markdown("- **Analogi Sederhana**: p-value adalah **peluang mendapatkan hasil data Anda (atau hasil yang lebih ekstrem) jika hipotesis awal kita (H₀) itu benar**. Hipotesis awal (H₀) biasanya menyatakan 'tidak ada perbedaan' atau 'tidak ada hubungan'.")
                    st.markdown("- **Contoh**: Jika p-value 0.02, artinya ada peluang 2% bahwa perbedaan yang Anda lihat hanya kebetulan. Karena peluangnya kecil, kita yakin perbedaan itu **nyata**.")
                    st.markdown("- **Aturan Praktis**: Bandingkan p-value dengan tingkat signifikansi **α (alpha)**. Nilai standar adalah **α = 0.05** (5%).")
                    st.markdown("   - **p-value < 0.05**: **Tolak H₀**. Ada perbedaan yang signifikan.")
                    st.markdown("   - **p-value ≥ 0.05**: **Gagal Tolak H₀**. Tidak ada cukup bukti untuk menyatakan adanya perbedaan.")

                    st.markdown("---")
                    st.markdown("#### Panduan Berdasarkan Jenis Uji (dengan Contoh Manufaktur)")
                    
                    st.markdown("##### Uji-t 1 Sampel")
                    st.write("- **Tujuan:** Membandingkan rata-rata dari satu kelompok sampel dengan nilai target atau nilai spesifikasi.")
                    st.write("- **Contoh:** Apakah rata-rata **dimensi diameter** produk dari *batch* hari ini (sampel) sesuai dengan spesifikasi target sebesar **100.5 mm**?")

                    st.markdown("##### Uji-t 2 Sampel (Independent)")
                    st.write("- **Tujuan:** Membandingkan rata-rata dari dua kelompok data yang **tidak berhubungan**.")
                    st.write("- **Contoh:** Apakah ada perbedaan rata-rata **kekerasan** produk yang diproduksi oleh **Mesin A** dan **Mesin B**?")

                    st.markdown("##### Uji-t Paired")
                    st.write("- **Tujuan:** Membandingkan rata-rata dari dua kelompok data yang **berpasangan atau berhubungan**.")
                    st.write("- **Contoh:** Apakah ada perubahan signifikan pada **kekasaran permukaan** produk **sebelum** dan **sesudah** proses *polishing*?")
                    
                    st.markdown("##### Uji Varians (F-Test)")
                    st.write("- **Tujuan:** Membandingkan **konsistensi atau variabilitas (sebaran)** dari dua kelompok data.")
                    st.write("- **Contoh:** Apakah **Mesin A** menghasilkan produk dengan **konsistensi berat** yang sama dengan **Mesin B**? Jika p-value rendah, artinya salah satu mesin memiliki variasi yang lebih besar (kurang konsisten).")

                    st.markdown("##### ANOVA 1 Arah")
                    st.write("- **Tujuan:** Membandingkan rata-rata dari **tiga kelompok data atau lebih**.")
                    st.write("- **Contoh:** Apakah ada perbedaan signifikan pada rata-rata **kekuatan tarik** untuk produk yang diproduksi dengan **tiga jenis paduan logam** yang berbeda?")
                    
                    st.markdown("##### Uji Non-Parametrik")
                    st.write("- **Tujuan:** Digunakan sebagai alternatif ketika data Anda **tidak berdistribusi normal**.")
                    st.markdown("* **Mann-Whitney U:** Alternatif untuk Uji-t 2 Sampel.")
                    st.markdown("* **Wilcoxon Signed-Rank:** Alternatif untuk Uji-t Paired.")

        if st.session_state['user_role'] == 'Admin':
            with tabs[tab_mapping["⚙️ Admin Setting"]]:
                st.header("⚙️ Pengaturan Admin")
                
                users = get_all_users()
                df_users = pd.DataFrame(users, columns=['ID', 'Role', 'Status'])
                
                st.markdown("---")
                st.subheader("🔧 Kelola Fitur Aplikasi")
                
                ordered_features = ['Histogram', 'Boxplot', 'Scatter Plot', 'Heatmap', 'Uji Normalitas', 'Uji Hipotesis', 'Normalisasi Data', 'Bantuan']
                
                for feature in ordered_features:
                    is_enabled = feature_status.get(feature, False)
                    is_enabled_bool = st.checkbox(f"Aktifkan **{feature}**", value=is_enabled, key=f'feature_{feature}')
                    if is_enabled_bool != is_enabled:
                        update_feature_status(feature, is_enabled_bool)
                        st.info(f"Status fitur '{feature}' berhasil diperbarui.")
                        st.rerun()

                pending_users = df_users[df_users['Status'] == 'pending']
                st.markdown("---")
                st.subheader("📥 Permintaan Pengguna Baru")
                if not pending_users.empty:
                    st.info("Berikut adalah daftar pengguna baru yang menunggu persetujuan Anda.")
                    for index, row in pending_users.iterrows():
                        col_id, col_btn = st.columns([0.8, 0.2])
                        with col_id:
                            st.write(f"ID: **{row['ID']}**")
                        with col_btn:
                            if st.button("Setujui", key=f"approve_{row['ID']}"):
                                approve_user(row['ID'])
                                st.success(f"Pengguna '{row['ID']}' berhasil disetujui.")
                                st.rerun()
                else:
                    st.success("Tidak ada permintaan pengguna baru saat ini.")
                
                approved_users = df_users[df_users['Status'] == 'approved']
                st.markdown("---")
                st.subheader("👥 Kelola Pengguna Terdaftar")
                if not approved_users.empty:
                    df_approved_display = approved_users.drop(columns=['Status'])
                    st.dataframe(df_approved_display, use_container_width=True)

                    st.markdown("---")
                    st.subheader("Ubah Role Pengguna")
                    user_id_to_manage = st.selectbox("Pilih ID Pengguna:", approved_users['ID'].tolist())
                    
                    if user_id_to_manage:
                        current_role = approved_users[approved_users['ID'] == user_id_to_manage]['Role'].iloc[0]
                        new_role = st.selectbox("Pilih Role Baru:", ['User', 'Admin'], index=['User', 'Admin'].index(current_role))
                        if st.button("Ubah Role", key='change_role'):
                            if user_id_to_manage and new_role:
                                update_user_role(user_id_to_manage, new_role)
                                st.success(f"Role pengguna '{user_id_to_manage}' berhasil diubah menjadi '{new_role}'.")
                                st.rerun()

                    st.markdown("---")
                    st.subheader("Hapus Pengguna")
                    user_id_to_delete = st.selectbox("Pilih ID Pengguna yang akan dihapus:", approved_users['ID'].tolist(), key='delete_user')
                    
                    if st.button("Hapus Pengguna", key='delete_button'):
                        if user_id_to_delete and user_id_to_delete != st.session_state['user_id']:
                            delete_user(user_id_to_delete)
                            st.success(f"Pengguna '{user_id_to_delete}' berhasil dihapus.")
                            st.rerun()
                        elif user_id_to_delete == st.session_state['user_id']:
                            st.error("Anda tidak bisa menghapus akun Anda sendiri.")
                        else:
                            st.warning("Pilih pengguna yang akan dihapus.")
                else:
                    st.info("Tidak ada pengguna terdaftar yang tersedia.")

    else:
        st.warning("Silakan upload file CSV/Excel terlebih dahulu atau gunakan input manual.")

# --- Bagian Utama Aplikasi ---
if __name__ == '__main__':
    init_db()

    # Initial state
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['user_id'] = None
        st.session_state['user_role'] = None
        st.session_state['page'] = 'login'

    # Display pages based on state
    if not st.session_state['logged_in']:
        if st.session_state['page'] == 'register':
            register_page()
        else:
            login_page()
    else:
        show_main_app()