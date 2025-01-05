import pandas as pd
import numpy as np
import streamlit as st
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# Transformer Algorithm: Mengubah teks tingkat urgensi menjadi angka
def transformer(data):
    # Pemetaan tingkat urgensi
    urgency_map = {"Rendah": 0, "Sedang": 1, "Tinggi": 2}
    
    # Menerapkan pemetaan pada kolom yang berisi tingkat urgensi
    data['Tingkat_Urgen'] = data['Tingkat_Urgen'].map(urgency_map)
    
    return data

# Triple Exponential Smoothing (TES): Prediksi tingkat urgensi harian selama 12 bulan
def triple_exponential_smoothing(data, days=365):
    # Menghitung jumlah per hari untuk setiap tingkat urgensi
    data_grouped = data.groupby([pd.Grouper(key='Tanggal', freq='D'), 'Tingkat_Urgen']).size().unstack(fill_value=0)
    
    # Model Holt-Winters (Triple Exponential Smoothing) dengan penanganan jika data tidak cukup musiman
    forecast_data = {}
    for urgency in data_grouped.columns:
        try:
            # Jika data cukup untuk musiman, gunakan model musiman
            model = ExponentialSmoothing(data_grouped[urgency], trend='add', seasonal='add', seasonal_periods=365)
            model_fit = model.fit()
        except ValueError:
            # Jika tidak cukup data musiman, hilangkan musiman dan hanya gunakan trend
            model = ExponentialSmoothing(data_grouped[urgency], trend='add', seasonal=None)
            model_fit = model.fit()
        
        # Prediksi untuk beberapa hari ke depan
        forecast = model_fit.forecast(steps=days)  # Prediksi untuk beberapa hari ke depan
        forecast_data[urgency] = forecast
    
    forecast_df = pd.DataFrame(forecast_data, index=pd.date_range(start=data['Tanggal'].max(), periods=days+1, freq='D')[1:])
    
    return forecast_df

# Streamlit UI
st.title("Analisis Data Laporan Kekerasan")

# Widget untuk unggah file
uploaded_file = st.file_uploader("Pilih file", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        # Deteksi tipe file berdasarkan ekstensi
        if uploaded_file.name.endswith(".csv"):
            data = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".xlsx"):
            data = pd.read_excel(uploaded_file)
        else:
            st.error("Format file tidak didukung. Harap unggah file .csv atau .xlsx.")

        # Menampilkan nama kolom untuk memverifikasi kolom yang ada
        st.write("Nama kolom dalam data yang diunggah:", data.columns)

        # Menghapus spasi di sekitar nama kolom dan mengubah nama kolom menjadi format standar
        data.columns = data.columns.str.strip()  # Menghapus spasi di sekitar nama kolom

        # Jika nama kolom sedikit berbeda, Anda bisa menggantinya
        data.rename(columns={'Tingkat Urgensi': 'Tingkat_Urgen', 'Tanggal Laporan': 'Tanggal'}, inplace=True)

        # Menampilkan nama kolom setelah perubahan
        st.write("Nama kolom setelah perubahan:", data.columns)

        # Memastikan bahwa kolom yang diperlukan ada
        if 'Tingkat_Urgen' not in data.columns or 'Tanggal' not in data.columns:
            st.error("Kolom 'Tingkat_Urgen' dan 'Tanggal' harus ada dalam data.")
        else:
            # Terapkan Transformer untuk mengubah teks menjadi angka
            transformed_data = transformer(data)
            st.write("Data setelah transformasi:")
            st.dataframe(transformed_data.head())

            # Terapkan Triple Exponential Smoothing untuk memprediksi
            forecast = triple_exponential_smoothing(transformed_data)
            st.write("Prediksi tingkat urgensi untuk 12 bulan ke depan (per hari):")
            st.dataframe(forecast)
        
            # Unduh kembali data setelah transformasi
            csv = transformed_data.to_csv(index=False).encode('utf-8')
            st.download_button("Unduh file CSV setelah transformasi", csv, "data_transformed.csv", "text/csv")
    
    except Exception as e:
        st.error(f"Terjadi kesalahan saat memproses file: {e}")
else:
    st.info("Unggah file untuk melihat isi data.")
