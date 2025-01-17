import pandas as pd
import numpy as np
import streamlit as st
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split

# Transformer Algorithm with Prediction
def transformer(data, prediction_months):
    urgency_map = {"Rendah": 0, "Sedang": 1, "Tinggi": 2}
    data['Tingkat_Urgen'] = data['Tingkat Urgensi'].map(urgency_map)
    data['Tanggal'] = pd.to_datetime(data['Tanggal'], format='%d/%m/%Y')
    one_hot = pd.get_dummies(data['Tingkat_Urgen'], prefix='Urgensi')
    data = pd.concat([data, one_hot], axis=1)

    # Prediction Model (e.g., Logistic Regression)
    features = ['Tingkat_Urgen', 'Urgensi_0', 'Urgensi_1', 'Urgensi_2']  # Example features for prediction
    target = 'Tingkat_Urgen'

    X = data[features]
    y = data[target]

    # Train a simple Logistic Regression model for prediction
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    # Making predictions for the entire dataset
    data['Prediksi_Tingkat_Urgen'] = model.predict(X)
    
    # Generate forecast for the selected duration (3 months or 12 months)
    forecast, total_forecast = generate_forecast(data, prediction_months)
    
    return data, forecast, total_forecast, model

# Function to generate forecast for 3 months or 12 months
def generate_forecast(data, months):
    forecast_data = {}
    data_grouped = data.groupby([pd.Grouper(key='Tanggal', freq='M'), 'Tingkat_Urgen']).size().unstack(fill_value=0)
    
    for urgency in data_grouped.columns:
        try:
            model = ExponentialSmoothing(data_grouped[urgency], trend='add', seasonal='add', seasonal_periods=12)
            model_fit = model.fit()
        except ValueError:
            model = ExponentialSmoothing(data_grouped[urgency], trend='add', seasonal=None)
            model_fit = model.fit()

        forecast = model_fit.forecast(steps=months)
        forecast_data[urgency] = np.maximum(np.round(forecast).astype(int), 0)  # Ensure no negative values
    
    forecast_df = pd.DataFrame(
        forecast_data, 
        index=pd.date_range(start=data['Tanggal'].max(), periods=months+1, freq='M')[1:]
    )

    # Now, transform the forecast to show total reports by urgency
    total_forecast = forecast_df.sum(axis=0).reset_index()
    total_forecast.columns = ['Tingkat Urgensi', 'Total Prediksi Laporan']
    
    return forecast_df, total_forecast

# Function to calculate MSE and MAE
def calculate_errors(actual, predicted):
    """
    Menghitung Mean Squared Error (MSE) dan Mean Absolute Error (MAE).

    Parameters:
    - actual: Data aktual (real observed values).
    - predicted: Data prediksi yang dihasilkan oleh model.

    Returns:
    - mse: Mean Squared Error.
    - mae: Mean Absolute Error.
    - actual: Potongan data aktual yang digunakan dalam perhitungan.
    - predicted: Potongan data prediksi yang digunakan dalam perhitungan.
    """
    min_length = min(len(actual), len(predicted))  # Sesuaikan panjang data aktual dan prediksi
    if min_length == 0:
        return None, None, [], []  # Return None jika tidak ada data untuk dibandingkan

    # Potong data aktual dan prediksi sesuai panjang minimum
    actual = actual[:min_length]
    predicted = predicted[:min_length]

    # Menghitung Mean Squared Error (MSE)
    mse = mean_squared_error(actual, predicted)

    # Menghitung Mean Absolute Error (MAE)
    mae = mean_absolute_error(actual, predicted)

    return mse, mae, actual, predicted

# Streamlit App
def main():
    st.title("Analisis Data Laporan Kekerasan")

    uploaded_file = st.file_uploader("Unggah file Excel", type=["xlsx", "csv"])
    prediction_months = st.selectbox("Pilih durasi prediksi (dalam bulan):", [3, 12])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                data = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(".xlsx"):
                data = pd.read_excel(uploaded_file)

            data.columns = data.columns.str.strip()
            if 'Tingkat Urgensi' not in data.columns or 'Tanggal' not in data.columns:
                st.error("Kolom 'Tanggal' dan 'Tingkat Urgensi' harus ada.")
            else:
                transformed_data, forecast, total_forecast, model = transformer(data, prediction_months)

                st.subheader("Hasil Prediksi")
                st.write("Data setelah transformasi dan prediksi:")
                st.dataframe(transformed_data)

                st.subheader(f"Hasil Prediksi untuk {prediction_months} Bulan ke Depan (Triple Exponential Smoothing)")
                forecast.columns = [f'Prediksi Tingkat Urgensi {col}' for col in forecast.columns]
                st.dataframe(forecast)

                st.subheader(f"Hasil Prediksi untuk {prediction_months} Bulan ke Depan (Transformer)")
                st.dataframe(total_forecast)

                # Calculate total forecast for Triple Exponential Smoothing
                total_smoothing_forecast = forecast.sum(axis=1).sum()  # Total sum of all urgencies

                # Calculate total forecast for Transformer (Total Prediksi Laporan)
                total_transformer_forecast = total_forecast['Total Prediksi Laporan'].sum()

                # Tabel Total Prediksi Laporan
                tabel_total_prediksi = pd.DataFrame({
                    "Model": ["Triple Exponential Smoothing", "Transformer"],
                    "Total Prediksi Laporan (12 bulan ke depan)": [total_smoothing_forecast, total_transformer_forecast]
                })
                st.subheader("Tabel Total Prediksi Laporan")
                st.table(tabel_total_prediksi)

                st.subheader("Perhitungan Error Metrics")
                data_grouped = transformed_data.groupby([pd.Grouper(key='Tanggal', freq='M'), 'Tingkat_Urgen']).size().unstack(fill_value=0)

                if len(data_grouped) > 0:
                    actual_data = data_grouped.iloc[-min(prediction_months, len(data_grouped)):].sum(axis=1).values
                    predicted_smoothing = forecast.sum(axis=1).values[:len(actual_data)]

                    # Triple Exponential Smoothing
                    mse_smoothing, mae_smoothing, actual_smoothing, predicted_smoothing = calculate_errors(actual_data, predicted_smoothing)
                    if mse_smoothing is not None:
                        st.write(f"**Triple Exponential Smoothing:**")
                        st.write(f"Mean Squared Error (MSE): {mse_smoothing}")
                        st.write(f"Mean Absolute Error (MAE): {mae_smoothing}")
                        st.line_chart(
                            pd.DataFrame({"Aktual": actual_smoothing, "Prediksi (Smoothing)": predicted_smoothing})
                        )

                        # Tabel MSE dan MAE untuk Triple Exponential Smoothing
                        mse_mae_data_smoothing = pd.DataFrame({
                            "Model": ["Triple Exponential Smoothing"],
                            "Mean Squared Error (MSE)": [mse_smoothing],
                            "Mean Absolute Error (MAE)": [mae_smoothing]
                        })
                        st.table(mse_mae_data_smoothing)

                    # Transformer
                    predicted_transformer = total_forecast['Total Prediksi Laporan'].values[:len(actual_data)]
                    mse_transformer, mae_transformer, actual_transformer, predicted_transformer = calculate_errors(actual_data, predicted_transformer)
                    if mse_transformer is not None:
                        st.write(f"**Transformer:**")
                        st.write(f"Mean Squared Error (MSE): {mse_transformer}")
                        st.write(f"Mean Absolute Error (MAE): {mae_transformer}")
                        st.line_chart(
                            pd.DataFrame({"Aktual": actual_transformer, "Prediksi (Transformer)": predicted_transformer})
                        )

                        # Tabel MSE dan MAE untuk Transformer
                        mse_mae_data_transformer = pd.DataFrame({
                            "Model": ["Transformer"],
                            "Mean Squared Error (MSE)": [mse_transformer],
                            "Mean Absolute Error (MAE)": [mae_transformer]
                        })
                        st.table(mse_mae_data_transformer)

                        # Penjelasan Model Terbaik
                        st.subheader("Model Terbaik Berdasarkan MSE dan MAE")
                        if mse_transformer < mse_smoothing and mae_transformer < mae_smoothing:
                            st.success("Model Transformer memiliki performa terbaik berdasarkan nilai MSE dan MAE.")
                        elif mse_smoothing < mse_transformer and mae_smoothing < mae_transformer:
                            st.success("Model Triple Exponential Smoothing memiliki performa terbaik berdasarkan nilai MSE dan MAE.")
                        else:
                            st.warning("Kedua model memiliki keunggulan pada metrik tertentu. Analisis lebih lanjut diperlukan.")

        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses file: {e}")

if __name__ == "__main__":
    main()
