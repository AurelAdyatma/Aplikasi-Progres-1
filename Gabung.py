import streamlit as st
import pandas as pd
import time
import hashlib
import random
import sqlite3
from datetime import datetime

# --- 1. KONFIGURASI HALAMAN & CSS ---
st.set_page_config(
    page_title="Getcareer - Database Version",
    page_icon="🚀",
    layout="wide",
    # Set to 'expanded' or remove the setting to keep it visible for navigation
    initial_sidebar_state="expanded" 
)

# Styling Custom Hijau Grab
st.markdown("""
<style>
    .main-header {font-size: 2.5rem; color: #00B14F; font-weight: 700;}
    .card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    .stButton>button {
        background-color: #00B14F;
        color: white;
        border-radius: 8px; 
        width: 100%;
    }
    .stButton>button:hover {background-color: #008f40;}
    /* Custom styling for sidebar navigation (Request 3) */
    .st-emotion-cache-1cypcdb {
        padding-top: 20px; /* Tambahkan padding agar navigasi tidak terlalu mepet ke atas */
    }
</style>
""", unsafe_allow_html=True)

# --- 2. DATABASE MANAGEMENT (SQLITE) ---

def init_db():
    """Membuat tabel database jika belum ada"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # Membuat tabel userdata dengan kolom: username, password, role, tanggal join
    c.execute('CREATE TABLE IF NOT EXISTS userdata(username TEXT PRIMARY KEY, password TEXT, role TEXT, join_date TEXT)')
    conn.commit()
    conn.close()

def add_userdata(username, password, role='seeker'):
    """Menambahkan user baru ke database"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    join_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        # HASHING password sudah dilakukan di luar fungsi ini
        c.execute('INSERT INTO userdata(username, password, role, join_date) VALUES (?,?,?,?)', 
                  (username, password, role, join_date))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False # Username sudah ada
    finally:
        conn.close()

def login_user_db(username, password):
    """Mengecek login dari database"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # Password yang diinput sudah dalam bentuk hash
    c.execute('SELECT * FROM userdata WHERE username = ? AND password = ?', (username, password))
    data = c.fetchall()
    conn.close()
    return data

def view_all_users():
    """Untuk Dashboard Admin: Melihat semua user"""
    conn = sqlite3.connect('users.db')
    df = pd.read_sql_query("SELECT username, role, join_date FROM userdata", conn)
    conn.close()
    return df

# --- 3. SECURITY & UTILS ---

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# Panggil fungsi init_db sekali saat aplikasi jalan
init_db()
# Buat admin default jika belum ada (gunakan hash password)
if not login_user_db('admin', make_hashes('admin')):
    add_userdata('admin', make_hashes('admin'), 'admin')

# --- 4. SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None
if 'username' not in st.session_state:
    st.session_state['username'] = ""
if 'auth_mode' not in st.session_state:
    st.session_state['auth_mode'] = 'login' # Bisa 'login' atau 'register'
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'Home' # Halaman default setelah login
    
# --- 5. HALAMAN LOGIN & REGISTER (AUTH) ---

def auth_page():
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://cdn-icons-png.flaticon.com/512/2910/2910791.png", width=80)
        st.markdown("<h1 style='color:#00B14F;'>Selamat Datang di Getcareer</h1>", unsafe_allow_html=True)
        
        # Container untuk form agar rapi
        with st.container(border=True):
            
            # --- MODE LOGIN ---
            if st.session_state['auth_mode'] == 'login':
                st.subheader("Masuk Akun")
                username = st.text_input("Username", key="login_user")
                password = st.text_input("Password", type='password', key="login_pass")
                
                if st.button("Masuk 🚀", key="login_btn"):
                    hashed_pswd = make_hashes(password)
                    result = login_user_db(username, hashed_pswd)
                    
                    if result:
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = username
                        st.session_state['user_role'] = result[0][2] # Ambil kolom role
                        st.success(f"Selamat datang kembali, {username}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.warning("Username atau Password salah")
                
                st.markdown("---")
                st.write("Belum punya akun?")
                if st.button("Daftar Sekarang", key="to_register_btn"):
                    st.session_state['auth_mode'] = 'register'
                    st.rerun()

            # --- MODE REGISTER ---
            elif st.session_state['auth_mode'] == 'register':
                st.subheader("Buat Akun Baru")
                new_user = st.text_input("Buat Username", key="reg_user")
                new_password = st.text_input("Buat Password", type='password', key="reg_pass1")
                confirm_password = st.text_input("Ulangi Password", type='password', key="reg_pass2")
                
                if st.button("Daftar", key="register_btn"):
                    if new_password != confirm_password:
                        st.error("Password tidak sama!")
                    elif len(new_password) < 4:
                        st.warning("Password minimal 4 karakter")
                    else:
                        # Simpan ke Database
                        hashed_new_password = make_hashes(new_password)
                        if add_userdata(new_user, hashed_new_password):
                            st.success("✅ Akun berhasil dibuat! Silakan Login.")
                            time.sleep(2)
                            st.session_state['auth_mode'] = 'login' # Balikin ke halaman login
                            st.rerun()
                        else:
                            st.error("Username sudah digunakan, coba yang lain.")
                
                st.markdown("---")
                if st.button("Kembali ke Login", key="to_login_btn"):
                    st.session_state['auth_mode'] = 'login'
                    st.rerun()

# --- 6. DATA SIMULASI & NAVIGASI ---

@st.cache_data
def get_jobs():
    # Simulasi data lowongan
    data = []
    companies = ['Gojek', 'Tokopedia', 'Shopee', 'Traveloka', 'Grab', 'Amazon', 'Microsoft', 'Google']
    roles = ['Data Analyst', 'Software Engineer', 'Product Manager', 'UI/UX Designer', 'DevOps Engineer', 'Marketing Specialist', 'HR Recruiter']
    for i in range(50):
        data.append({
            "Posisi": random.choice(roles),
            "Perusahaan": random.choice(companies),
            "Gaji": f"Rp {random.randint(5,25)} Juta",
            "Lokasi": random.choice(['Jakarta', 'Remote', 'Bandung', 'Surabaya', 'Yogyakarta'])
        })
    return pd.DataFrame(data)

def draw_sidebar_nav():
    """Membuat sidebar navigasi untuk pengguna (Request 3)"""
    st.sidebar.title("Getcareer 🚀")
    st.sidebar.markdown(f"**Selamat datang, {st.session_state['username']}!**")
    
    st.sidebar.markdown("---")
    
    pages = {
        "Home": "🏠 Beranda",
        "SearchJobs": "🔍 Cari Pekerjaan",
        "Profile": "👤 Profil & CV",
    }
    
    # Menggunakan radio buttons untuk navigasi yang jelas
    selected_page = st.sidebar.radio(
        "Navigasi",
        options=list(pages.keys()),
        format_func=lambda x: pages[x],
        index=list(pages.keys()).index(st.session_state['current_page']),
        key="main_nav_radio"
    )
    st.session_state['current_page'] = selected_page
    
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout", key="sidebar_logout_btn"):
        st.session_state['logged_in'] = False
        st.session_state['current_page'] = 'Home'
        st.rerun()

# --- 7. HALAMAN UTAMA (KONTEN SETELAH LOGIN) ---

def home_page():
    draw_sidebar_nav()
    
    # Konten halaman utama yang lebih sederhana (Request 1 & 2)
    st.markdown(f"<h1 class='main-header'>Halo, {st.session_state['username']}!</h1>", unsafe_allow_html=True)
    st.markdown("Selamat datang kembali di **Getcareer**, platform pencarian kerja terdepan. Kami siap membantu Anda menemukan peluang terbaik.")
    
    st.markdown("---")
    st.subheader("Ayo Mulai Mencari!")
    st.markdown("""
    - **🔍 Cari Pekerjaan:** Kunjungi halaman **'Cari Pekerjaan'** di sidebar untuk memfilter dan menemukan lowongan.
    - **👤 Profil & CV:** Pastikan CV Anda terunggah di halaman **'Profil & CV'** agar siap melamar.
    """)

def search_jobs_page():
    """Halaman pencarian lowongan kerja (Request 1)"""
    draw_sidebar_nav()
    
    st.title("🔍 Cari Lowongan Kerja")
    st.info("Masukkan kriteria pencarian Anda dan tekan tombol 'Cari' untuk melihat hasilnya.")
    
    df = get_jobs()
    all_roles = ['Semua Posisi'] + sorted(df['Posisi'].unique().tolist())
    all_locations = ['Semua Lokasi'] + sorted(df['Lokasi'].unique().tolist())
    
    # Filter inputs
    col1, col2, col3 = st.columns([3, 2, 1])
    with col1:
        keyword = st.text_input("Kata Kunci (Posisi / Perusahaan)", placeholder="Contoh: Data Analyst, Gojek")
    with col2:
        role_filter = st.selectbox("Filter Posisi", all_roles)
    with col3:
        location_filter = st.selectbox("Filter Lokasi", all_locations)
        
    # --- Filtering Logic ---
    
    # Tombol untuk memicu pencarian (agar data tidak langsung muncul)
    if st.button("Cari Lowongan", key="execute_search"):
        
        # Lakukan proses filtering
        filtered_df = df.copy()
        
        if role_filter != 'Semua Posisi':
            filtered_df = filtered_df[filtered_df['Posisi'] == role_filter]
            
        if location_filter != 'Semua Lokasi':
            filtered_df = filtered_df[filtered_df['Lokasi'] == location_filter]
            
        if keyword:
            keyword = keyword.lower()
            filtered_df = filtered_df[
                filtered_df.apply(lambda row: keyword in row['Posisi'].lower() or keyword in row['Perusahaan'].lower(), axis=1)
            ]
            
        st.markdown("---")
        
        # Display results
        if not filtered_df.empty:
            st.subheader(f"Ditemukan {len(filtered_df)} Lowongan Tersedia:")
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.warning("Tidak ada lowongan yang ditemukan untuk kriteria tersebut.")

def profile_page():
    """Halaman profil dan upload CV (Request 2)"""
    draw_sidebar_nav()
    
    st.title("👤 Profil Pengguna")
    
    st.markdown("### Informasi Akun")
    with st.container(border=True):
        st.markdown(f"""
        - **Username:** `{st.session_state['username']}`
        - **Role:** `{st.session_state['user_role'].capitalize()}`
        - *Status:* Aktif
        """)
    
    st.markdown("---")
    
    st.markdown("### 📂 Upload Curriculum Vitae (CV) Anda")
    st.info("Pastikan Anda mengunggah CV terbaru dalam format PDF. File ini akan digunakan untuk melamar pekerjaan.")
    uploaded = st.file_uploader("Pilih file CV (Format PDF)", type="pdf")
    
    if uploaded:
        st.success(f"✅ CV Anda ({uploaded.name}) Berhasil diunggah ke server!")
        st.balloons()
        st.write("Anda sekarang siap untuk melamar pekerjaan!")

def admin_page():
    """Halaman dashboard admin"""
    st.sidebar.title("Admin Panel")
    if st.sidebar.button("Logout Admin"):
        st.session_state['logged_in'] = False
        st.session_state['current_page'] = 'Home'
        st.rerun()
        
    st.title("👮 Database Pengguna (Real-time)")
    st.info("Data ini diambil langsung dari file `users.db`")
    
    # Menampilkan isi database user yang baru daftar
    user_db = view_all_users()
    st.dataframe(user_db, use_container_width=True)
    
    st.metric("Total Pengguna Terdaftar", len(user_db))

# --- 8. MAIN CONTROL ---

def main():
    if st.session_state['logged_in']:
        if st.session_state['user_role'] == 'admin':
            admin_page()
        else:
            # User (Seeker) Navigation
            page = st.session_state['current_page']
            
            if page == 'Home':
                home_page()
            elif page == 'SearchJobs':
                search_jobs_page()
            elif page == 'Profile':
                profile_page()
            else:
                home_page() # Fallback
                
    else:
        auth_page()

if __name__ == '__main__':
    main()
