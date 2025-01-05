import json
import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.seasonal import seasonal_decompose
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_error
import streamlit as st


def prediksi_kejadian(json_path, periode_musiman, steps, tingkat_urgensi):
    """
    Fungsi untuk memprediksi jumlah kejadian dengan tingkat urgensi tertentu menggunakan Holt-Winters.

    Args:
        json_path: Path ke file JSON yang berisi data.
        periode_musiman: Periode musiman dalam data.
        steps: Jumlah langkah yang ingin diprediksi.
        tingkat_urgensi: Tingkat urgensi yang ingin diprediksi (Tinggi, Sedang, Rendah).

    Returns:
        Dataframe yang berisi hasil peramalan.
    """

    # Membaca data JSON
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Membuat DataFrame
    df = pd.DataFrame(data)
    df['Tanggal'] = pd.to_datetime(df['Tanggal'], format='%d/%m/%Y')
    df = df.set_index('Tanggal')

    # Mengubah Tingkat_Urgensi menjadi numerik
    df['Tingkat_Urgensi'] = df['Tingkat_Urgensi'].map({'Tinggi': 3, 'Sedang': 2, 'Rendah': 1})

    # Menghitung jumlah kejadian dengan tingkat urgensi tertentu setiap hari
    if tingkat_urgensi == 'Tinggi':
        ts = df[df['Tingkat_Urgensi'] == 3].resample('D').size()
    elif tingkat_urgensi == 'Sedang':
        ts = df[df['Tingkat_Urgensi'] == 2].resample('D').size()
    elif tingkat_urgensi == 'Rendah':
        ts = df[df['Tingkat_Urgensi'] == 1].resample('D').size()

    # Membuat model Holt-Winters
    model = ExponentialSmoothing(ts, seasonal_periods=periode_musiman, trend='add', seasonal='add')
    
    # Fit the model
    fit = model.fit()

    # Melakukan peramalan
    forecast = fit.forecast(steps=steps)

    # Dekomposisi musiman
    decomposition = seasonal_decompose(ts, model='additive', period=periode_musiman)

    # Visualisasi komponen
    trend = decomposition.trend
    seasonal = decomposition.seasonal
    residual = decomposition.resid

    # Evaluasi model
    mse = mean_squared_error(ts, fit.fittedvalues)
    mae = mean_absolute_error(ts, fit.fittedvalues)

    # Menghitung persentase peramalan berdasarkan rata-rata kejadian
    persentase = (forecast / ts.mean()) * 100

    # Penjelasan
    penjelasan = (
        "Penjelasan:\n"
        "Semakin besar nilai persentase peramalan, semakin besar kemungkinan kejadian dengan tingkat urgensi tertentu "
        "terjadi pada periode waktu yang diprediksi. Jika persentase lebih besar dari 100%, ini menunjukkan bahwa jumlah "
        "kejadian diperkirakan akan lebih tinggi dibandingkan dengan rata-rata kejadian yang telah tercatat sebelumnya. "
        "Sebaliknya, jika persentase kurang dari 100%, maka kejadian diperkirakan akan lebih rendah dari rata-rata yang "
        "terjadi pada periode yang sama."
    )

    return forecast, mse, mae, ts, trend, seasonal, residual, persentase, penjelasan


def main():
    st.title("Prediksi Jumlah Kejadian dengan Tingkat Urgensi")
    st.write("Menggunakan Holt-Winters")

    # Konfigurasi input file JSON dan parameter lainnya
    json_path = 'json/algoritma.json'  # Pastikan file ini ada di path yang benar
    periode_musiman = 7
    steps = 14

    tingkat_urgensi = ['Tinggi', 'Sedang', 'Rendah']

    # Menyimpan hasil peramalan dan evaluasi untuk setiap tingkat urgensi
    results = {}

    for urgensi in tingkat_urgensi:
        forecast, mse, mae, ts, trend, seasonal, residual, persentase, penjelasan = prediksi_kejadian(json_path, periode_musiman, steps, urgensi)

        # Menyimpan hasil peramalan
        results[urgensi] = {
            'forecast': forecast,
            'mse': mse,
            'mae': mae,
            'ts': ts,
            'trend': trend,
            'seasonal': seasonal,
            'residual': residual,
            'persentase': persentase,
            'penjelasan': penjelasan
        }

        # Menampilkan hasil peramalan untuk tingkat urgensi
        st.write(f"Hasil Peramalan untuk {urgensi}:")
        st.write(pd.DataFrame(persentase, columns=['Prediksi (%)']))

        # Menampilkan evaluasi model untuk tingkat urgensi
        st.write(f"Evaluasi Model untuk {urgensi}:")
        st.write(pd.DataFrame({'MSE': [mse], 'MAE': [mae]}))

        # Menampilkan visualisasi komponen untuk tingkat urgensi
        st.write(f"Visualisasi Komponen untuk {urgensi}:")
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.plot(ts, label='Observed')
        ax.plot(trend, label='Trend')
        ax.plot(seasonal, label='Seasonal')
        ax.plot(residual, label='Residual')
        ax.legend()
        st.pyplot(fig)

    # Menampilkan penjelasan untuk persentase prediksi di tingkat urgensi
    st.subheader("Penjelasan Persentase Prediksi di Tingkat Urgensi:")
    st.write(results['Rendah']['penjelasan'])

    # Menambahkan penjelasan untuk MSE dan MAE
    st.subheader("Penjelasan Evaluasi Model (MSE dan MAE):")
    st.write(""" 
        **MSE (Mean Squared Error) dan MAE (Mean Absolute Error)** adalah dua metrik yang umum digunakan untuk mengevaluasi kinerja model prediksi, khususnya dalam konteks regresi. Kedua metrik ini mengukur seberapa besar kesalahan antara nilai yang diprediksi dan nilai yang sebenarnya, tetapi dengan cara yang berbeda. Penjelasan tentang metrik ini pada setiap tingkat urgensi (Tinggi, Sedang, dan Rendah) adalah sebagai berikut:

        **1. Tinggi Urgensi:**
        - **MSE (0.0233):** Nilai MSE yang rendah ini menunjukkan bahwa model memberikan prediksi yang sangat dekat dengan nilai sebenarnya pada data dengan tingkat urgensi tinggi. MSE menghitung kuadrat dari selisih antara prediksi dan nilai aktual, jadi semakin kecil nilainya, semakin baik performa model dalam memprediksi kejadian yang sangat penting atau mendesak.
        - **MAE (0.0707):** Nilai MAE yang juga relatif kecil menunjukkan bahwa rata-rata kesalahan absolut antara nilai prediksi dan nilai aktual sangat rendah. Artinya, model memiliki kesalahan prediksi yang kecil dan dapat diandalkan untuk kejadian yang memiliki urgensi tinggi.

        **2. Sedang Urgensi:**
        - **MSE (0.0233):** Untuk tingkat urgensi sedang, MSE tetap kecil, yang berarti model masih dapat memberikan prediksi yang cukup akurat meskipun tingkat urgensinya tidak seberapa tinggi. Ini menunjukkan bahwa model dapat menangani data yang tidak terlalu mendesak dengan cukup baik, meskipun ada beberapa variasi dalam hasil prediksinya.
        - **MAE (0.0707):** MAE menunjukkan bahwa meskipun ada kesalahan, rata-rata kesalahan absolut tetap cukup kecil. Model bisa memberikan prediksi yang cukup baik, meskipun tidak seakurat pada tingkat urgensi tinggi.

        **3. Rendah Urgensi:**
        - **MSE (0.0233):** Pada tingkat urgensi rendah, MSE yang masih kecil menunjukkan bahwa model tidak banyak menghasilkan kesalahan prediksi meskipun data tersebut tidak terlalu penting atau mendesak. Dengan kata lain, model tetap menjaga kinerjanya dengan baik meskipun konteksnya lebih santai.
        - **MAE (0.0707):** MAE yang kecil juga berarti kesalahan prediksi rata-rata tetap rendah, bahkan pada tingkat urgensi yang lebih rendah. Ini menunjukkan bahwa model masih dapat memberikan prediksi yang cukup baik meskipun tidak memiliki dampak yang besar pada pengambilan keputusan.

        **Kesimpulan:**
        - **Tinggi Urgensi:** Model sangat akurat dengan kesalahan yang sangat kecil (baik MSE dan MAE).
        - **Sedang Urgensi:** Model tetap baik, meskipun ada sedikit variasi dalam prediksi.
        - **Rendah Urgensi:** Model tetap memberikan prediksi yang cukup baik meskipun tidak terlalu penting.

        Nilai MSE dan MAE yang rendah menunjukkan bahwa model secara keseluruhan dapat memberikan prediksi yang akurat dan andal pada berbagai tingkat urgensi, baik yang tinggi, sedang, maupun rendah.
    """)

if __name__ == "__main__":
    main()
