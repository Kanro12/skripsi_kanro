import streamlit as st
import pyrebase
import pandas as pd

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
db = firebase.database()

# Fungsi untuk menampilkan riwayat laporan (hanya public)
def show_report_history():
    st.title("Riwayat Laporan Pengguna Public")

    # Mendapatkan informasi pengguna yang login
    user = st.session_state.get("user")
    if not user:
        st.warning("Silakan login untuk melihat riwayat laporan.")
        return

    report_list = []

    # Mengambil data semua pengguna
    users_data = db.child("users").get()
    if users_data.each():
        for user_data in users_data.each():
            user_info = user_data.val()
            user_role = user_info.get("role", "public")  # Default role public jika tidak ditemukan
            if user_role == "public":  # Hanya ambil laporan pengguna dengan role public
                user_reports = user_info.get("laporan", {})
                for report_id, report in user_reports.items():
                    report["email"] = user_data.key().replace("_", ".")  # Tambahkan email pengguna
                    report_list.append(report)

    # Menampilkan laporan jika ada
    if report_list:
        # Menyiapkan data untuk tabel
        table_data = []
        for data in report_list:
            gambar_html = (
                f'<a href="{data.get("gambar_url", "")}" target="_blank"><img src="{data.get("gambar_url", "")}" width="100"></a>' 
                if data.get("gambar_url") 
                else "Tidak ada gambar"
            )
            video_html = (
                f'<video width="100" controls><source src="{data.get("video_url", "")}" type="video/mp4">Your browser does not support the video tag.</video>' 
                if data.get("video_url") 
                else "Tidak ada video"
            )

            table_data.append({
                "Username": data.get('username', ''),
                "Email": data.get("email", ""),
                "NIK": data.get('nik', ''),
                "Nomor HP": data.get('nomor_hp', ''),
                "Usia": data.get('usia', ''),
                "Tanggal Laporan": data.get('tanggal', ''),
                "Lokasi": data.get('lokasi', ''),
                "Jenis Kekerasan": data.get('jenis_kekerasan', ''),
                "Deskripsi": data.get('deskripsi', ''),
                "Nama Kantor Polisi": data.get('kantor_polisi', ''),
                "Gambar": gambar_html,
                "Video": video_html
            })

        # Membuat DataFrame dan menampilkan tabel
        df = pd.DataFrame(table_data)
        st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.info("Tidak ada laporan yang ditemukan dari pengguna public.")
