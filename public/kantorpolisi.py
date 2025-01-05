import streamlit as st
import json
import os

# Membaca data JSON dari file
def load_data():
    with open('json/data.json', 'r') as file:
        data = json.load(file)
    return data

# Menampilkan data polsek
def display_polsek(polsek_data):
    for polsek in polsek_data:
        st.subheader(polsek['nama'])
        st.write(f"**Alamat**: {polsek['alamat']}")
        st.write(f"**Telepon**: {polsek['telepon']}")
        st.write(f"**Website**: {polsek.get('website', 'Tidak tersedia')}")
        st.write(f"**Sosial Media**: {polsek.get('sosmed', 'Tidak tersedia')}")

        # Menampilkan gambar dengan use_container_width
        gambar_url = polsek['gambar']
        if gambar_url.startswith("http"):
            try:
                # Menampilkan gambar dari URL eksternal
                st.image(gambar_url, use_container_width=True)
            except Exception as e:
                st.warning(f"Gambar tidak dapat dimuat dari URL: {gambar_url}")
        else:
            # Cek apakah file gambar lokal tersedia
            if os.path.exists(gambar_url):
                st.image(gambar_url, use_container_width=True)
            else:
                st.warning(f"Gambar lokal tidak ditemukan: {gambar_url}")

        st.markdown("---")

# Membuat tampilan Streamlit
def main():
    st.title("Daftar Polsek Jakarta Utara")
    st.write("Berikut adalah daftar Polsek di Jakarta Utara beserta informasi terkait:")

    # Load data JSON
    data = load_data()
    
    # Menampilkan polsek
    display_polsek(data['polsek'])

if __name__ == "__main__":
    main()
