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
    initial_sidebar_state="collapsed"
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

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return True
    return False

# Panggil fungsi init_db sekali saat aplikasi jalan
init_db()
# Buat admin default jika belum ada
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

# --- 5. HALAMAN LOGIN & REGISTER ---

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
                username = st.text_input("Username")
                password = st.text_input("Password", type='password')
                
                if st.button("Masuk 🚀"):
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
                if st.button("Daftar Sekarang"):
                    st.session_state['auth_mode'] = 'register'
                    st.rerun()

            # --- MODE REGISTER ---
            elif st.session_state['auth_mode'] == 'register':
                st.subheader("Buat Akun Baru")
                new_user = st.text_input("Buat Username")
                new_password = st.text_input("Buat Password", type='password')
                confirm_password = st.text_input("Ulangi Password", type='password')
                
                if st.button("Daftar"):
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
                if st.button("Kembali ke Login"):
                    st.session_state['auth_mode'] = 'login'
                    st.rerun()

# --- 6. HALAMAN UTAMA (KONTEN SETELAH LOGIN) ---

@st.cache_data
def get_jobs():
    # Simulasi data lowongan
    data = []
    companies = ['Gojek', 'Tokopedia', 'Shopee', 'Traveloka']
    roles = ['Data Analyst', 'Software Engineer', 'Product Manager', 'UI/UX']
    for i in range(50):
        data.append({
            "Posisi": random.choice(roles),
            "Perusahaan": random.choice(companies),
            "Gaji": f"Rp {random.randint(5,20)} Juta",
            "Lokasi": random.choice(['Jakarta', 'Remote', 'Bandung'])
        })
    return pd.DataFrame(data)

def home_page():
    # Sidebar Logout
    with st.sidebar:
        st.write(f"User: **{st.session_state['username']}**")
        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.rerun()
            
    st.title("💼 Lowongan Tersedia")
    df = get_jobs()
    st.dataframe(df, use_container_width=True)
    
    st.markdown("### 📂 Upload CV Anda")
    uploaded = st.file_uploader("Format PDF", type="pdf")
    if uploaded:
        st.success("CV Berhasil diunggah ke server!")

def admin_page():
    st.sidebar.title("Admin Panel")
    if st.sidebar.button("Logout Admin"):
        st.session_state['logged_in'] = False
        st.rerun()
        
    st.title("👮 Database Pengguna (Real-time)")
    st.info("Data ini diambil langsung dari file `users.db`")
    
    # Menampilkan isi database user yang baru daftar
    user_db = view_all_users()
    st.dataframe(user_db, use_container_width=True)
    
    st.metric("Total Pengguna Terdaftar", len(user_db))

# --- 7. MAIN CONTROL ---

def main():
    if st.session_state['logged_in']:
        if st.session_state['user_role'] == 'admin':
            admin_page()
        else:
            home_page()
    else:
        auth_page()

if __name__ == '__main__':
    main()