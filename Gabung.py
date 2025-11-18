import streamlit as st
import pandas as pd
import time
import hashlib
import random
import sqlite3
from datetime import datetime

# ==============================================================================
# 1. KONFIGURASI HALAMAN & CSS
# ==============================================================================

st.set_page_config(
    page_title="Getcareer - Platform Karier Terbaik",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {font-size: 2.5rem; color: #00B14F; font-weight: 700;}
    
    .stButton>button {
        background-color: #00B14F;
        color: white;
        border-radius: 8px; 
        font-weight: bold;
        padding: 10px;
        width: 100%;
    }
    .stButton>button:hover {background-color: #008f40;}
    
    .stContainer {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        padding: 15px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# 2. DATABASE MANAGEMENT (SQLITE)
# ==============================================================================

DB_NAME = 'users.db'

@st.cache_resource
def get_db_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute('CREATE TABLE IF NOT EXISTS userdata(username TEXT PRIMARY KEY, password TEXT, role TEXT, join_date TEXT)')
        conn.commit()
    except Exception as e:
        st.error(f"Error Database: {e}")
        
def add_userdata(username, password_hash, role='seeker'):
    conn = get_db_connection()
    c = conn.cursor()
    join_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        c.execute('INSERT INTO userdata(username, password, role, join_date) VALUES (?,?,?,?)', 
                  (username, password_hash, role, join_date))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        st.error(f"Error Database: {e}")
        return False

def login_user_db(username, password_hash):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM userdata WHERE username = ? AND password = ?', (username, password_hash))
    data = c.fetchall()
    return data

def view_all_users():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT username, role, join_date FROM userdata", conn)
    return df

# ==============================================================================
# 3. SECURITY, UTILS, & STATE INITIATION
# ==============================================================================

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def init_session_state():
    defaults = {
        'logged_in': False,
        'user_role': None,
        'username': "",
        'auth_mode': 'login', 
        'current_page': 'Home',
        'main_nav_radio': 'Home',
        'cv_uploaded_name': None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_db()
init_session_state()

if not login_user_db('admin', make_hashes('admin')):
    add_userdata('admin', make_hashes('admin'), 'admin')


# ==============================================================================
# 4. DATA SIMULASI & NAVIGASI
# ==============================================================================

@st.cache_data
def get_jobs():
    data = []
    companies = ['Gojek', 'Tokopedia', 'Shopee', 'Traveloka', 'Grab', 'Amazon', 'Microsoft', 'Google', 'Mandiri', 'Telkom']
    roles = ['Data Analyst', 'Software Engineer', 'Product Manager', 'UI/UX Designer', 'DevOps Engineer', 'Marketing Specialist', 'HR Recruiter', 'Cloud Architect', 'Cyber Security']
    for i in range(50):
        data.append({
            "ID": i + 1,
            "Posisi": random.choice(roles),
            "Perusahaan": random.choice(companies),
            "Gaji": f"Rp {random.randint(5,25)} Juta",
            "Lokasi": random.choice(['Jakarta', 'Remote', 'Bandung', 'Surabaya', 'Yogyakarta', 'Makassar']),
            "Tanggal Posting": (datetime.now() - pd.Timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
        })
    return pd.DataFrame(data).set_index('ID')

def navigate_to_page():
    st.session_state['current_page'] = st.session_state['main_nav_radio']
    
def draw_sidebar_nav():
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2910/2910791.png", width=50)
    st.sidebar.markdown(f"**Halo, {st.session_state['username']}!**")
    st.sidebar.markdown("---")
    
    pages = {
        "Home": "🏠 Beranda",
        "SearchJobs": "🔍 Cari Pekerjaan",
        "Profile": "👤 Profil & CV",
    }
    
    try:
        default_index = list(pages.keys()).index(st.session_state['current_page'])
    except ValueError:
        default_index = 0 

    st.sidebar.radio(
        "Navigasi Utama",
        options=list(pages.keys()),
        format_func=lambda x: pages[x],
        index=default_index,
        key="main_nav_radio",
        on_change=navigate_to_page
    )
    
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout", key="sidebar_logout_btn"):
        st.session_state['logged_in'] = False
        st.session_state['current_page'] = 'Home'
        st.session_state['main_nav_radio'] = 'Home'
        st.rerun()

# ==============================================================================
# 5. FUNGSI HALAMAN (VIEWS)
# ==============================================================================

def auth_page():
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://cdn-icons-png.flaticon.com/512/2910/2910791.png", width=80)
        st.markdown("<h1 style='color:#00B14F; text-align: center;'>Selamat Datang di Getcareer</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Temukan Karier Impian Anda Sekarang!</p>", unsafe_allow_html=True)
        
        with st.container(border=True):
            if st.session_state['auth_mode'] == 'login':
                st.subheader("Masuk Akun 🔑")
                with st.form("login_form"):
                    username = st.text_input("Username", key="login_user")
                    password = st.text_input("Password", type='password', key="login_pass")
                    submitted = st.form_submit_button("Masuk 🚀")

                    if submitted:
                        hashed_pswd = make_hashes(password)
                        result = login_user_db(username, hashed_pswd)
                        
                        if result:
                            st.session_state['logged_in'] = True
                            st.session_state['username'] = username
                            st.session_state['user_role'] = result[0][2] 
                            st.success(f"Selamat datang kembali, {username}!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Username atau Password salah")

                st.markdown("---")
                st.write("Belum punya akun?")
                if st.button("Daftar Sekarang", key="to_register_btn"):
                    st.session_state['auth_mode'] = 'register'
                    st.rerun()

            elif st.session_state['auth_mode'] == 'register':
                st.subheader("Buat Akun Baru 📝")

                with st.form("register_form"):
                    new_user = st.text_input("Buat Username", key="reg_user")
                    new_password = st.text_input("Buat Password (Min. 4 Karakter)", type='password', key="reg_pass1")
                    confirm_password = st.text_input("Ulangi Password", type='password', key="reg_pass2")
                    submitted = st.form_submit_button("Daftar 🤝")

                    if submitted:
                        if new_password != confirm_password:
                            st.error("❌ Password tidak sama!")
                        elif len(new_password) < 4:
                            st.warning("⚠️ Password minimal 4 karakter")
                        else:
                            hashed_new_password = make_hashes(new_password)
                            if add_userdata(new_user, hashed_new_password):
                                st.success("✅ Akun berhasil dibuat! Silakan Login.")
                                time.sleep(1)
                                st.session_state['auth_mode'] = 'login' 
                                st.rerun()
                            else:
                                st.error("❌ Username sudah digunakan, coba yang lain.")
                
                st.markdown("---")
                if st.button("Kembali ke Login", key="to_login_btn"):
                    st.session_state['auth_mode'] = 'login'
                    st.rerun()

def home_page():
    st.markdown(f"<h1 class='main-header'>Halo, {st.session_state['username']}! 👋</h1>", unsafe_allow_html=True)
    st.markdown("Selamat datang kembali di **Getcareer**, platform pencarian kerja terdepan. Kami siap membantu Anda menemukan peluang terbaik.")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Aksi Cepat")
        st.markdown("""
        <div class="stContainer">
        Cek <b>5 Lowongan Baru</b> yang sesuai dengan minat Anda.
        </div>
        """, unsafe_allow_html=True)

        if st.button("Lihat Lowongan Baru", key="go_search_home"):
            st.session_state['current_page'] = 'SearchJobs'
            st.session_state['main_nav_radio'] = 'SearchJobs'
            st.rerun()

    with col2:
        st.subheader("🛠️ Persiapan Profil")
        st.markdown("""
        <div class="stContainer">
        Pastikan data Anda sudah lengkap dan CV terbaru sudah terunggah.
        </div>
        """, unsafe_allow_html=True)
        if st.button("Perbarui Profil", key="go_profile_home"):
            st.session_state['current_page'] = 'Profile'
            st.session_state['main_nav_radio'] = 'Profile'
            st.rerun()

def search_jobs_page():
    st.title("🔍 Cari Lowongan Kerja")
    st.markdown("Gunakan filter di bawah ini untuk mempermudah pencarian Anda.")
    
    df = get_jobs()
    all_roles = ['Semua Posisi'] + sorted(df['Posisi'].unique().tolist())
    all_locations = ['Semua Lokasi'] + sorted(df['Lokasi'].unique().tolist())
    
    with st.container(border=True):
        st.subheader("Kriteria Pencarian")
        col1, col2, col3 = st.columns([3, 2, 2])
        with col1:
            keyword = st.text_input("Kata Kunci (Posisi / Perusahaan)", placeholder="Contoh: Data Analyst, Gojek")
        with col2:
            role_filter = st.selectbox("Filter Posisi", all_roles)
        with col3:
            location_filter = st.selectbox("Filter Lokasi", all_locations)
        
        search_clicked = st.button("Cari Lowongan", key="execute_search")

    if search_clicked:
        with st.spinner('Mencari data lowongan...'):
            time.sleep(1) 
            
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
        
        if not filtered_df.empty:
            st.subheader(f"Ditemukan {len(filtered_df)} Lowongan Tersedia:")
            st.dataframe(
                filtered_df, 
                use_container_width=True,
                column_config={
                    "Gaji": st.column_config.ProgressColumn("Gaji Estimasi", format="%f Juta", min_value=5, max_value=25),
                }
            )
        else:
            st.warning("Tidak ada lowongan yang ditemukan untuk kriteria tersebut. Coba kriteria lain.")

def profile_page():
    st.title("👤 Profil Pengguna & CV")
    
    col_info, col_cv = st.columns(2)
    
    with col_info:
        st.markdown("### Informasi Akun Anda")
        with st.container(border=True):
            st.markdown(f"""
            - **Username:** `{st.session_state['username']}`
            - **Role Akun:** `{st.session_state['user_role'].capitalize()}`
            - **Status:** **Aktif**
            """)
            st.caption("Untuk mengubah data, silakan hubungi Admin.")
        
        st.markdown("---")
        
    with col_cv:
        st.markdown("### 📂 Upload Curriculum Vitae (CV)")
        st.info("Pastikan Anda mengunggah CV terbaru dalam format **PDF**. File ini penting untuk proses melamar kerja.")
        
        uploaded = st.file_uploader("Pilih file CV (Format PDF)", type="pdf")
        
        if uploaded:
            st.session_state['cv_uploaded_name'] = uploaded.name
            st.success(f"✅ CV Anda ({uploaded.name}) Berhasil diunggah ke server! Anda siap melamar.")
            st.balloons()
        
        if st.session_state['cv_uploaded_name']:
            st.caption(f"CV saat ini: **{st.session_state['cv_uploaded_name']}**")
        else:
            st.caption("Belum ada CV yang diunggah.")

def admin_page():
    st.sidebar.title("👮 Admin Panel")
    if st.sidebar.button("Logout Admin"):
        st.session_state['logged_in'] = False
        st.session_state['current_page'] = 'Home'
        st.session_state['main_nav_radio'] = 'Home'
        st.rerun()
        
    st.title("Database Pengguna 📊")
    st.info("Data ini diambil langsung dari file `users.db`.")
    
    user_db = view_all_users()
    st.dataframe(user_db, use_container_width=True)
    
    col_metrics = st.columns(3)
    col_metrics[0].metric("Total Pengguna Terdaftar", len(user_db))
    col_metrics[1].metric("Total Seeker", len(user_db[user_db['role'] == 'seeker']))
    col_metrics[2].metric("Total Admin", len(user_db[user_db['role'] == 'admin']))


# ==============================================================================
# 6. MAIN CONTROL
# ==============================================================================

def main():
    if st.session_state['logged_in']:
        
        if st.session_state['user_role'] == 'admin':
            admin_page()
        else:
            draw_sidebar_nav() 

            page = st.session_state['current_page']
            
            if page == 'Home':
                home_page()
            elif page == 'SearchJobs':
                search_jobs_page()
            elif page == 'Profile':
                profile_page()
            else:
                home_page() 

    else:
        auth_page()

if __name__ == '__main__':
    main()
