import streamlit as st
import pyrebase
from datetime import datetime

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

# Fungsi untuk menampilkan seluruh profil pengguna
def view_all_profiles():
    profils = db.child("profil").get()
    return profils.val()

# Fungsi utama untuk menampilkan profil admin
def main():
    st.title("Daftar Profil Pengguna")

    # Pastikan pengguna sudah login dan memiliki role admin
    if 'role' not in st.session_state or st.session_state['role'] != 'Admin':
        st.error("Anda tidak memiliki akses ke halaman ini.")
        return

    profils = view_all_profiles()

    if profils:
        
        # Menampilkan setiap profil
        for user_id, profil in profils.items():
            st.write(f"### Profil {profil['name']}")
            st.text_input("Nama", profil['name'], disabled=True, key=f"name_{user_id}")
            st.date_input("Tanggal Lahir", datetime.strptime(profil['dob'], "%Y-%m-%d"), disabled=True, key=f"dob_{user_id}")
            st.text_input("Nomor Telepon", profil['phone'], disabled=True, key=f"phone_{user_id}")
            st.text_area("Alamat", profil['address'], disabled=True, key=f"address_{user_id}")
            st.write("---")
    else:
        st.write("Tidak ada data profil pengguna.")

if __name__ == "__main__":
    main()
