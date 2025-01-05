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

# Fungsi untuk menampilkan riwayat laporan
def show_report_history():
    st.title("Riwayat Laporan")

    # Mendapatkan informasi pengguna yang login
    user = st.session_state.get("user")
    if not user:
        st.warning("Silakan login untuk melihat riwayat laporan.")
        return

    email = user.get("email")
    role = user.get("role")

    report_list = []

    # Logika untuk peran admin atau public
    if role == "admin":
        # Mengambil semua laporan dari semua pengguna
        users_data = db.child("users").get()
        if users_data.each():
            for user_data in users_data.each():
                user_reports = user_data.val().get("laporan", {})
                for report_id, report in user_reports.items():
                    report_list.append(report)
    else:
        # Mengambil laporan pengguna yang sedang login
        user_reports = db.child("users").child(email.replace(".", "_")).child("laporan").get()
        if user_reports.each():
            for report in user_reports.each():
                report_list.append(report.val())

    # Menampilkan laporan jika ada
    if report_list:
        # Menyiapkan data untuk tabel dengan kolom lengkap
        table_data = []
        for data in report_list:
            gambar_html = f'<a href="{data.get("gambar_url", "")}" target="_blank"><img src="{data.get("gambar_url", "")}" width="400"></a>' if data.get("gambar_url") else "Tidak ada gambar"
            video_html = f'<video width="200" controls><source src="{data.get("video_url", "")}" type="video/mp4"></video>' if data.get("video_url") else "Tidak ada video"

            # Menambahkan kolom Urgensi dan Status
            table_data.append({
                "Username": data.get('username', ''),
                "NIK": data.get('nik', ''),
                "Nomor HP": data.get('nomor_hp', ''),
                "Usia": data.get('usia', ''),
                "Tanggal Laporan": data.get('tanggal', ''),
                "Lokasi": data.get('lokasi', ''),
                "Jenis Kekerasan": data.get('jenis_kekerasan', ''),
                "Deskripsi": data.get('deskripsi', ''),
                "Nama Kantor Polisi": data.get('kantor_polisi', ''),
                "Urgensi": data.get('urgensi', ''),  # Menampilkan kolom Urgensi
                "Status": data.get('status', ''),  # Menampilkan kolom Status
                "Gambar": gambar_html,
                "Video": video_html
            })

        # Membuat DataFrame dan menampilkan tabel
        df = pd.DataFrame(table_data)
        st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.write("Tidak ada laporan yang ditemukan.")

# Simulasi login untuk testing
if __name__ == "__main__":
    # Contoh data login (dapat diganti sesuai kebutuhan)
    st.session_state["user"] = {
        "email": "test@example.com",
        "role": "public",  # "admin" atau "public"
        "username": "Test User"
    }
    show_report_history()
