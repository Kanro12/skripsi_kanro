import streamlit as st
import json
from datetime import datetime
import pyrebase

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

# Inisialisasi Firebase
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()
storage = firebase.storage()

# Fungsi untuk memuat data JSON kantor polisi
def load_polsek_data():
    with open('json/data.json', 'r') as file:
        data = json.load(file)
    return data['polsek']

# Fungsi untuk meng-upload gambar dan video ke Firebase Storage
def upload_file_to_storage(file, folder_name):
    file_path = f"{folder_name}/{file.name}"
    storage.child(file_path).put(file)
    url = storage.child(file_path).get_url(None)  # Passing `None` as the token
    return url

# Fungsi untuk membuat form input laporan
def create_report_form():
    st.title('Tambahkan Laporan Baru')

    # Mendapatkan informasi pengguna yang login
    user = st.session_state.get("user")
    if not user:
        st.warning("Silakan login untuk membuat laporan.")
        return

    email = user.get("email")
    role = user.get("role")

    # Input fields untuk laporan
    username = st.text_input('Username', value=user.get("username", ""))
    nik = st.text_input('NIK')
    nomor_hp = st.text_input('Nomor HP')
    usia = st.number_input('Usia', min_value=0)

    # Menentukan kategori usia berdasarkan input
    if usia < 13:
        kategori_usia = 'Anak-anak'
    elif 13 <= usia < 18:
        kategori_usia = 'Remaja'
    elif 18 <= usia < 60:
        kategori_usia = 'Dewasa'
    else:
        kategori_usia = 'Lansia'

    if usia:
        st.write(f'**Kategori Usia:** {kategori_usia}')

    tanggal = st.date_input('Tanggal', min_value=datetime.today())
    lokasi = st.text_input('Lokasi')
    jenis_kekerasan = st.selectbox('Jenis Kekerasan', ['Fisik', 'Psikis', 'Seksual', 'Ekonomi', 'Lainnya'])
    deskripsi = st.text_area('Deskripsi')

    gambar = st.file_uploader("Gambar", type=["jpg", "jpeg", "png"])
    video = st.file_uploader("Video", type=["mp4", "avi", "mov"])

    # Memuat data Polsek
    polsek_data = load_polsek_data()
    kantor_polisi_names = ["Kantor Polisi"] + [polsek['nama'] for polsek in polsek_data]
    kantor_polisi = st.selectbox('Nama Kantor Polisi', kantor_polisi_names)

    # Mengirim laporan
    if st.button('Kirim Laporan'):
        gambar_url = None
        if gambar:
            gambar_url = upload_file_to_storage(gambar, "laporan/gambar")

        video_url = None
        if video:
            video_url = upload_file_to_storage(video, "laporan/video")

        report_data = {
            "username": username,
            "nik": nik,
            "nomor_hp": nomor_hp,
            "usia": usia,
            "tanggal": tanggal.strftime("%d/%m/%Y"),
            "lokasi": lokasi,
            "jenis_kekerasan": jenis_kekerasan,
            "deskripsi": deskripsi,
            "kantor_polisi": kantor_polisi,
            "gambar_url": gambar_url if gambar else None,
            "video_url": video_url if video else None
        }

        try:
            # Menyimpan laporan di bawah pengguna yang login
            db.child("users").child(email.replace(".", "_")).child("laporan").push(report_data)

            # Menyimpan laporan di lokasi global "update_data"
            db.child("update_data").push(report_data)

            # Menampilkan pesan laporan terkirim
            st.success("Laporan berhasil dikirim!")

            # Reset form setelah pengiriman laporan
            st.session_state['form_submitted'] = True
            st.rerun()

        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")

# Menjalankan fungsi untuk membuat laporan
if __name__ == "__main__":
    # Simulasi login untuk testing
    st.session_state["user"] = {
        "email": "test@example.com",
        "role": "public",
        "username": "Test User"
    }

    create_report_form()
