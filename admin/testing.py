import pandas as pd
import numpy as np
import streamlit as st
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.metrics import mean_squared_error, mean_absolute_error

# Transformer Algorithm: Mengubah teks tingkat urgensi menjadi angka
def transformer(data):
    # Pemetaan tingkat urgensi
    urgency_map = {"Rendah": 0, "Sedang": 1, "Tinggi": 2}
    
    # Menerapkan pemetaan pada kolom yang berisi tingkat urgensi
    data['Tingkat_Urgen'] = data['Tingkat_Urgen'].map(urgency_map)
    
    return data

# Triple Exponential Smoothing (TES): Prediksi tingkat urgensi selama 3 bulan atau 1 tahun
def triple_exponential_smoothing(data, months=12):
    # Menghitung jumlah per bulan untuk setiap tingkat urgensi
    data_grouped = data.groupby([pd.Grouper(key='Tanggal', freq='M'), 'Tingkat_Urgen']).size().unstack(fill_value=0)
    
    # Model Holt-Winters (Triple Exponential Smoothing) dengan penanganan jika data tidak cukup musiman
    forecast_data = {}
    for urgency in data_grouped.columns:
        try:
            # Jika data cukup untuk musiman, gunakan model musiman
            model = ExponentialSmoothing(data_grouped[urgency], trend='add', seasonal='add', seasonal_periods=12)
            model_fit = model.fit()
        except ValueError:
            # Jika tidak cukup data musiman, hilangkan musiman dan hanya gunakan trend
            model = ExponentialSmoothing(data_grouped[urgency], trend='add', seasonal=None)
            model_fit = model.fit()
        
        # Prediksi untuk beberapa bulan ke depan
        forecast = model_fit.forecast(steps=months)  # Prediksi untuk beberapa bulan ke depan
        forecast_data[urgency] = forecast
    
    forecast_df = pd.DataFrame(forecast_data, index=pd.date_range(start=data['Tanggal'].max(), periods=months+1, freq='M')[1:])
    
    return forecast_df, data_grouped

# Menghitung MSE dan MAE
def calculate_metrics(forecast, actual_data):
    mse = mean_squared_error(actual_data, forecast)
    mae = mean_absolute_error(actual_data, forecast)
    return mse, mae

# Menambahkan rekap jumlah kriminal berdasarkan tingkat urgensi
def rekap_kriminal(data):
    # Menghitung jumlah kejadian kriminal berdasarkan tingkat urgensi
    rekap = data.groupby('Tingkat_Urgen').size().reset_index(name='Jumlah_Kejadian')
    return rekap

# Main function
def main():
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

            # Menghapus spasi di sekitar nama kolom dan mengubah nama kolom menjadi format standar
            data.columns = data.columns.str.strip()  # Menghapus spasi di sekitar nama kolom

            # Jika nama kolom sedikit berbeda, Anda bisa menggantinya
            data.rename(columns={'Tingkat Urgensi': 'Tingkat_Urgen', 'Tanggal Laporan': 'Tanggal'}, inplace=True)

            # Memastikan bahwa kolom yang diperlukan ada
            if 'Tingkat_Urgen' not in data.columns or 'Tanggal' not in data.columns:
                st.error("Kolom 'Tingkat_Urgen' dan 'Tanggal' harus ada dalam data.")
            else:
                # Terapkan Transformer untuk mengubah teks menjadi angka
                transformed_data = transformer(data)

                # Tampilkan rekap jumlah kriminal
                rekap = rekap_kriminal(transformed_data)
                st.write("Rekap Jumlah Kejadian Kriminal Berdasarkan Tingkat Urgensi:")
                st.dataframe(rekap)

                # Menambahkan keterangan tingkat urgensi
                st.write(""" 
                    **Keterangan Tingkat Urgensi:**
                    - 2: Tinggi
                    - 1: Sedang
                    - 0: Rendah
                """)

                # Terapkan Triple Exponential Smoothing untuk memprediksi
                forecast, actual_data_grouped = triple_exponential_smoothing(transformed_data)

                # Menampilkan hasil prediksi
                forecast.columns = [f'Prediksi Urgensi {col}' for col in forecast.columns]
                st.write("Prediksi tingkat urgensi untuk 12 bulan ke depan:")
                st.dataframe(forecast)

                # Menampilkan data aktual dan prediksi untuk debug
                st.write("Data aktual yang digunakan untuk menghitung MSE dan MAE:")
                st.write(actual_data_grouped)

                st.write("Data prediksi yang digunakan untuk menghitung MSE dan MAE:")
                st.write(forecast)
        
        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses file: {e}")
    else:
        st.info("Unggah file untuk melihat isi data.")

if __name__ == "__main__":
    main()
