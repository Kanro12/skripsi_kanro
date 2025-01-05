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

# Fungsi untuk memuat laporan hanya dari pengguna dengan role 'public'
def load_public_reports():
    report_list = []
    users_data = db.child("users").get()
    if users_data.each():
        for user_data in users_data.each():
            user_info = user_data.val()
            user_role = user_info.get("role", "public")  # Default role adalah public
            if user_role == "public":  # Hanya ambil data pengguna dengan role public
                user_reports = user_info.get("laporan", {})
                for report_id, report in user_reports.items():
                    report["email"] = user_data.key().replace("_", ".")  # Tambahkan email pengguna
                    report["id"] = report_id  # Tambahkan ID laporan
                    report_list.append(report)
    return report_list

# Fungsi utama
def main():
    st.title("Manajemen Data Laporan")

    # Tombol untuk menyegarkan tampilan tabel
    if st.button("Refresh Tabel"):
        st.session_state.reports = load_public_reports()

    # Muat data laporan jika belum ada di session state
    if "reports" not in st.session_state:
        st.session_state.reports = load_public_reports()

    report_list = st.session_state.reports

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
                "Email": data.get('email', ''),
                "Username": data.get('username', ''),
                "NIK": data.get('nik', ''),
                "Nomor HP": data.get('nomor_hp', ''),
                "Usia": data.get('usia', ''),
                "Tanggal Laporan": data.get('tanggal', ''),
                "Lokasi": data.get('lokasi', ''),
                "Jenis Kekerasan": data.get('jenis_kekerasan', ''),
                "Deskripsi": data.get('deskripsi', ''),
                "Nama Kantor Polisi": data.get('kantor_polisi', ''),
                "Urgensi": data.get('urgensi', ''),
                "Status": data.get('status', 'sedang diproses'),
                "Gambar": gambar_html,
                "Video": video_html
            })

        # Membuat DataFrame dan menampilkan tabel
        df = pd.DataFrame(table_data)
        st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)

        # Pilih laporan berdasarkan ID untuk diedit
        report_id = st.selectbox(
            "Pilih laporan berdasarkan ID untuk diedit:",
            [report.get("id", "") for report in report_list]
        )

        # Tampilkan data laporan yang dipilih berdasarkan ID
        selected_report = next(report for report in report_list if report.get("id", "") == report_id)

        # Form untuk edit data
        with st.form("edit_form"):
            username_input = st.text_input("Username", value=selected_report["username"])
            nik = st.text_input("NIK", value=selected_report["nik"])
            nomor_hp = st.text_input("Nomor HP", value=selected_report["nomor_hp"])
            usia = st.number_input("Usia", value=int(selected_report["usia"]))
            tanggal = st.text_input("Tanggal Laporan", value=selected_report["tanggal"])
            lokasi = st.text_input("Lokasi", value=selected_report["lokasi"])
            jenis_kekerasan = st.text_input("Jenis Kekerasan", value=selected_report["jenis_kekerasan"])
            deskripsi = st.text_area("Deskripsi", value=selected_report["deskripsi"])
            kantor_polisi = st.text_input("Nama Kantor Polisi", value=selected_report["kantor_polisi"])
            urgensi = st.selectbox("Urgensi", ["Tinggi", "Sedang", "Rendah"], index=["Tinggi", "Sedang", "Rendah"].index(selected_report.get("urgensi", "Sedang")))
            status = st.selectbox("Status", ["sedang diproses", "diproses", "diterima", "ditolak"], index=["sedang diproses", "diproses", "diterima", "ditolak"].index(selected_report.get("status", "sedang diproses")))

            # Tombol submit untuk update data
            submitted = st.form_submit_button("Update Data")
            if submitted:
                # Update data di session state
                for report in report_list:
                    if report["id"] == report_id:
                        report.update({
                            "username": username_input,
                            "nik": nik,
                            "nomor_hp": nomor_hp,
                            "usia": usia,
                            "tanggal": tanggal,
                            "lokasi": lokasi,
                            "jenis_kekerasan": jenis_kekerasan,
                            "deskripsi": deskripsi,
                            "kantor_polisi": kantor_polisi,
                            "urgensi": urgensi,
                            "status": status
                        })
                        break

                # Update data di database Firebase
                db.child("users").child(selected_report["email"].replace(".", "_")).child("laporan").child(report_id).update({
                    "username": username_input,
                    "nik": nik,
                    "nomor_hp": nomor_hp,
                    "usia": usia,
                    "tanggal": tanggal,
                    "lokasi": lokasi,
                    "jenis_kekerasan": jenis_kekerasan,
                    "deskripsi": deskripsi,
                    "kantor_polisi": kantor_polisi,
                    "urgensi": urgensi,
                    "status": status
                })
                st.success(f"Data laporan dengan ID {report_id} berhasil diperbarui!")
    else:
        st.info("Tidak ada laporan yang ditemukan di database.")

if __name__ == "__main__":
    main()
