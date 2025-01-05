import sys
import os
import streamlit as st

# Menambahkan folder induk ke Python Path agar dapat mengimpor file yang ada di luar folder public
sys.path.append(os.path.abspath(os.path.dirname(__file__)))  # Menambahkan root folder aplikasi ke path

# Mengimpor file yang berada di folder public
import login
import public.kantorpolisi as kantorpolisi  # Memperbaiki impor dengan menambahkan public di jalur impor
import public.laporan as laporan  # Sama seperti kantorpolisi
import public.riwayat as riwayat  # Mengimpor file riwayat.py
import public.profil as profil  # Mengimpor file profil.py


# Fungsi untuk navbar responsif
def navbar():
    st.sidebar.title("Lapor-yo!")
    
    # Menambahkan tombol logout di sidebar di atas menu lainnya
    if st.sidebar.button("Logout"):
        st.session_state['logged_in'] = False  # Set status login False
        st.session_state['page'] = 'Login'  # Arahkan ke halaman login
    
    # Menggunakan selectbox untuk menu yang lebih responsif
    menu_options = ["Profil", "Beranda", "Kantor Polisi", "Laporan", "Riwayat"]
    
    # Menggunakan st.selectbox di sidebar
    menu_option = st.sidebar.selectbox("Pilih Halaman:", menu_options)
    
    return menu_option

# Fungsi untuk halaman Beranda atau Dashboard
def main_content():
    st.title("Tentang Lapor-yo!")
    st.markdown(""" 
    **Lapor-yo!** adalah platform digital yang dirancang untuk mempermudah pelaporan tindakan kekerasan dan insiden serius lainnya. Misi kami adalah memberikan cara yang sederhana, mudah diakses, dan aman bagi individu untuk melaporkan kejadian tersebut, memastikan setiap laporan ditanggapi dengan serius dan segera.
    
    ### Fitur
    - **Pelaporan Mudah**: Pengguna dapat dengan cepat mengajukan laporan tentang kekerasan, termasuk deskripsi terperinci dan bukti multimedia seperti gambar dan video.
    - **Kerahasiaan**: Semua laporan ditangani dengan kerahasiaan maksimal untuk melindungi privasi dan keselamatan pelapor.
    - **Pembaruan Waktu Nyata**: Tetap mendapatkan informasi terkini tentang status laporan Anda.
    - **Akses ke Sumber Daya**: Terhubung dengan sumber daya dan layanan dukungan yang relevan untuk korban kekerasan.
    
    ### Informasi Hukum
    Sistem pelaporan ini mematuhi hukum dan peraturan yang relevan mengenai perlindungan privasi digital. Pengguna diharapkan untuk melaporkan insiden sesuai dengan hukum dan peraturan setempat. Dengan menggunakan platform ini, Anda setuju untuk mematuhi persyaratan hukum tersebut dan mengakui bahwa informasi yang Anda berikan akan digunakan untuk memfasilitasi respons yang sesuai terhadap laporan Anda.
    
    #### Referensi Hukum Penting:
    - Pemerintah: [**UU Perlindungan Data Pribadi Beri Perlindungan Hukum (UU ITE)**](https://www.mkri.id/index.php?page=web.Berita&id=18915)
    - Penting Kenali [**UU Perlindungan Data Pribadi di Indonesia**](https://bcafinance.co.id/Penting-Kenali-UU-Perlindungan-Data-Pribadi-di-Indonesia)
    """)

# Fungsi untuk halaman Kantor Polisi
def kantor_polisi():
    kantorpolisi.main()  # Panggil fungsi utama dari kantorpolisi.py

# Fungsi untuk halaman Laporan
def laporan_page():
    laporan.create_report_form()  # Panggil fungsi dari laporan.py

# Fungsi untuk halaman Riwayat
def riwayat_page():
    riwayat.show_report_history()  # Panggil fungsi untuk menampilkan riwayat laporan dari riwayat.py

# Fungsi untuk halaman Profil
def profil_page():
    profil.main()  # Panggil fungsi utama dari profil.py


# Fungsi utama untuk mengelola alur aplikasi
def main():
    # Inisialisasi variabel status sesi jika belum ditetapkan
    if "logged_in" not in st.session_state:
        st.session_state['logged_in'] = False
    if "page" not in st.session_state:
        st.session_state.page = "Login"

    # Periksa apakah pengguna sudah login
    if not st.session_state['logged_in']:
        st.session_state.page = "Login"  # Pastikan halaman login ditampilkan saat status login False
    
    # Buat menu navigasi
    menu_option = navbar()

    # Menangani rendering halaman berdasarkan status sesi
    if "page" in st.session_state:
        if st.session_state.page == "Login":
            login.main()  # Panggil halaman login
        elif menu_option == "Beranda":
            main_content()
        elif menu_option == "Kantor Polisi":
            kantor_polisi()  # Pindah ke halaman Kantor Polisi
        elif menu_option == "Laporan":
            laporan_page()  # Pindah ke halaman laporan
        elif menu_option == "Riwayat":
            riwayat_page()  # Pindah ke halaman riwayat
        elif menu_option == "Profil":
            profil_page()  # Pindah ke halaman profil

# Pastikan untuk menjalankan aplikasi hanya ketika di main thread
if __name__ == "__main__":
    main()
