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
auth = firebase.auth()
db = firebase.database()

# Fungsi untuk menambahkan data profil
def add_profil(user_id, name, dob, phone, address):
    profil_data = {
        "name": name,
        "dob": dob,
        "phone": phone,
        "address": address
    }
    db.child("profil").child(user_id).set(profil_data)

# Fungsi untuk menampilkan profil berdasarkan user_id
def view_profil(user_id):
    profil = db.child("profil").child(user_id).get()
    return profil.val()

# Fungsi untuk memperbarui data profil
def update_profil(user_id, name, dob, phone, address):
    profil_data = {
        "name": name,
        "dob": dob,
        "phone": phone,
        "address": address
    }
    db.child("profil").child(user_id).update(profil_data)

# Streamlit App
def main():
    st.title("Profil Pengguna")
    
    # Memeriksa status login
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        st.warning("Silakan login terlebih dahulu.")
        return
    
    user_id = st.session_state['user']['localId']
    
    # Memeriksa apakah ada data profil di Firebase
    profil_data = view_profil(user_id)
    
    if profil_data:
        # Jika ada data profil, hanya tampilkan menu 'Lihat Profil' dan 'Update Profil'
        menu = ["Lihat Profil", "Update Profil"]
    else:
        # Jika belum ada data profil, tampilkan menu 'Tambah Profil'
        menu = ["Tambah Profil", "Lihat Profil", "Update Profil"]

    choice = st.sidebar.selectbox("Pilih Menu", menu)

    if choice == "Tambah Profil":
        st.subheader("Tambah Profil Pengguna")
        
        # Input data profil
        name = st.text_input("Nama")
        dob = st.date_input("Tanggal Lahir", min_value=datetime(1924, 1, 1))
        phone = st.text_input("Nomor Telepon")
        address = st.text_area("Alamat")
        
        # Cek apakah tombol "Simpan" ditekan
        if st.button("Simpan"):
            if name and phone and address:  # Memastikan input tidak kosong
                add_profil(user_id, name, dob.strftime("%Y-%m-%d"), phone, address)
                st.success("Profil berhasil disimpan!")
                st.session_state.added_profil = True  # Set session state to track if profil is added
            else:
                st.error("Harap isi semua field.")

    elif choice == "Lihat Profil":
        st.subheader("Lihat Profil Pengguna")
        
        if profil_data:
            # Menampilkan data profil seperti form, tapi read-only
            st.text_input("Nama", profil_data['name'], disabled=True)
            st.date_input("Tanggal Lahir", datetime.strptime(profil_data['dob'], "%Y-%m-%d"), disabled=True)
            st.text_input("Nomor Telepon", profil_data['phone'], disabled=True)
            st.text_area("Alamat", profil_data['address'], disabled=True)
        else:
            st.write("Tidak ada data profil pengguna.")

    elif choice == "Update Profil":
        st.subheader("Update Profil Pengguna")
        
        if profil_data:
            # Menampilkan data profil yang dapat diperbarui
            name = st.text_input("Nama", profil_data['name'])
            dob = st.date_input("Tanggal Lahir", datetime.strptime(profil_data['dob'], "%Y-%m-%d"))
            phone = st.text_input("Nomor Telepon", profil_data['phone'])
            address = st.text_area("Alamat", profil_data['address'])
            
            if st.button("Perbarui"):
                update_profil(user_id, name, dob.strftime("%Y-%m-%d"), phone, address)
                st.success("Profil berhasil diperbarui!")

if __name__ == "__main__":
    main()
