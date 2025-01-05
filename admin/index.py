import streamlit as st
import pyrebase
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from admin import laporan, user  # Mengimpor laporan dan user.py yang ada di folder admin

# Konfigurasi Firebase
firebaseConfig = {
    "apiKey": "AIzaSyADwagZsQxhQBQpwvubO9ulz7QHruJyVkM",
    "authDomain": "lapor-cde21.firebaseapp.com",
    "databaseURL": "https://lapor-cde21-default-rtdb.firebaseio.com",
    "projectId": "lapor-cde21",
    "storageBucket": "lapor-cde21.appspot.com",
    "messagingSenderId": "89266309551",
    "appId": "1:89266309551:web:b9f1dc04ac75721922c75a",
    "measurementId": "G-4NRHYVEE7Y"
}

firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

# Fungsi untuk mengambil data statistik dari Firebase
def get_user_count_by_role(role):
    try:
        users = db.child("users").get().val()
        if users:
            return sum(1 for user in users.values() if user.get("role") == role)
        return 0
    except Exception as e:
        st.error(f"Kesalahan saat mengambil data pengguna berdasarkan role: {e}")
        return 0

def get_report_count():
    try:
        users = db.child("users").get().val()
        if users:
            return sum(len(user.get("laporan", {})) for user in users.values())
        return 0
    except Exception as e:
        st.error(f"Kesalahan saat mengambil data laporan: {e}")
        return 0

def create_stat_card(title, value, color):
    st.markdown(
        f"""
        <div style="background-color: {color}; padding: 20px; border-radius: 8px; text-align: center; 
        color: white; font-size: 16px; font-weight: bold; margin: 5px;">
            <p style="margin: 0;">{title}</p>
            <h2 style="margin: 5px 0;">{value}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

# Fungsi utama
def main():
    menu = [
        "Dashboard", "Laporan", "Pengguna", "Edit Laporan", 
        "Tentang", "Triple Exponential Smoothing", "Algoritma Transformer", "Testing", "Keluar"
    ]
    choice = st.sidebar.selectbox("Pilih Menu", menu)

    if choice == "Dashboard":
        st.title("Dashboard Admin")
        st.subheader("Control Panel")
        total_admin = get_user_count_by_role("Admin")
        total_public = get_user_count_by_role("Public")
        total_reports = get_report_count()

        # Tampilkan statistik
        col1, col2 = st.columns(2)
        with col1:
            create_stat_card("Admin", total_admin, "#28A745")
        with col2:
            create_stat_card("Public", total_public, "#FFC107")
        create_stat_card("Total Laporan", total_reports, "#17A2B8")

    elif choice == "Laporan":
        try:
            laporan.show_report_history()
        except Exception as e:
            st.error(f"Kesalahan saat menampilkan laporan: {e}")

    elif choice == "Pengguna":
        try:
            user.main()
        except Exception as e:
            st.error(f"Kesalahan saat menampilkan pengguna: {e}")

    elif choice == "Edit Laporan":
        try:
            from admin import editlaporan
            editlaporan.main()
        except Exception as e:
            st.error(f"Kesalahan saat memanggil editlaporan.py: {e}")

    elif choice == "Triple Exponential Smoothing":
        try:
            from admin import tes
            tes.main()
        except Exception as e:
            st.error(f"Kesalahan saat memanggil tes.py: {e}")

    elif choice == "Algoritma Transformer":
        try:
            from admin import transformer
            transformer.main()
        except Exception as e:
            st.error(f"Kesalahan saat memanggil transformer.py: {e}")

    elif choice == "Testing":
        try:
            from admin import testing
            testing.main()
        except Exception as e:
            st.error(f"Kesalahan saat memanggil testing.py: {e}")

    elif choice == "Tentang":
        st.title("Tentang")
        
        # Latar Belakang
        st.subheader("Latar Belakang")
        st.write("""
        Aplikasi ini dikembangkan untuk membantu instansi, organisasi, atau pemerintah dalam 
        mengelola laporan masyarakat terkait kejadian kekerasan atau masalah lainnya. 
        Dengan adanya aplikasi ini, proses pencatatan, pengelolaan, hingga penyelesaian laporan 
        menjadi lebih cepat, terstruktur, dan terintegrasi.
        """)

        # Tujuan Utama
        st.subheader("Tujuan Utama")
        st.write("""
        - Mempermudah pengelolaan laporan dari masyarakat.
        - Menyediakan alat analitik yang membantu dalam pengambilan keputusan berdasarkan data laporan.
        - Meningkatkan transparansi dalam penanganan laporan.
        - Memberikan akses mudah kepada admin untuk memonitor data laporan dan pengguna.
        """)

        # Fitur Utama
        st.subheader("Fitur Utama")
        st.write("""
        - **Dashboard:** Menyediakan statistik utama, seperti jumlah laporan, pengguna berdasarkan peran 
          (Admin/Public), dan laporan lainnya.
        - **Manajemen Laporan:** Menampilkan dan mengedit laporan yang diajukan oleh pengguna.
        - **Manajemen Pengguna:** Memantau pengguna yang terdaftar di sistem, termasuk peran mereka.
        - **Algoritma:** Implementasi algoritma seperti *Triple Exponential Smoothing* dan Transformer 
          untuk analisis data.
        - **Integrasi Firebase:** Aplikasi ini menggunakan Firebase untuk mengelola database, autentikasi, 
          dan penyimpanan data secara real-time.
        """)

        # Keunggulan
        st.subheader("Keunggulan")
        st.write("""
        - **Mudah Digunakan:** Antarmuka aplikasi dirancang agar intuitif bagi pengguna dengan berbagai 
          tingkat keahlian.
        - **Real-time Data:** Data laporan dan pengguna dapat diperbarui dan dilihat secara langsung.
        - **Keamanan Data:** Sistem menggunakan Firebase untuk memastikan data tersimpan dengan aman 
          dan terenkripsi.
        - **Fleksibel:** Aplikasi dapat diadaptasi untuk berbagai jenis laporan sesuai kebutuhan pengguna.
        """)

        # Siapa yang Bisa Menggunakan?
        st.subheader("Siapa yang Bisa Menggunakan?")
        st.write("""
        - **Administrator:** Bertugas untuk memantau seluruh data laporan dan pengguna.
        - **Masyarakat Umum:** Menggunakan aplikasi ini untuk melaporkan kejadian tertentu yang membutuhkan 
          tindak lanjut.
        - **Analisis Data:** Pengguna yang bertugas menganalisis data laporan dengan algoritma yang tersedia.
        """)

        # Pengembang
        st.subheader("Pengembang")
        st.write("""
        Aplikasi ini dikembangkan oleh tim yang bertujuan untuk memberikan solusi berbasis teknologi 
        dalam pengelolaan data laporan masyarakat. Jika ada pertanyaan atau masukan, silakan hubungi 
        tim pengembang melalui email atau kontak yang tercantum.
        """)

    elif choice == "Keluar":
        st.session_state['logged_in'] = False
        st.session_state['page'] = 'Login'
        st.rerun()

if __name__ == "__main__":
    main()
