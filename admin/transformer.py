import json
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from sklearn.preprocessing import LabelEncoder
from datetime import datetime
import streamlit as st
from sklearn.utils.class_weight import compute_class_weight

# Membaca data dari file json/algoritma.json
def load_data():
    try:
        with open('json/algoritma.json', 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        st.error(f"Kesalahan membaca data JSON: {e}")
        return []

# Proses data untuk menjadi fitur yang dapat dipakai
def process_data(data):
    try:
        start_date = datetime.strptime("01/01/2024", "%d/%m/%Y").date()
        for entry in data:
            entry['Tanggal'] = (datetime.strptime(entry['Tanggal'], "%d/%m/%Y").date() - start_date).days
        
        le = LabelEncoder()
        urgensi_encoded = le.fit_transform([entry['Tingkat_Urgensi'] for entry in data])
        
        features = np.array([[entry['Tanggal']] for entry in data])  # Tanggal sebagai fitur
        labels = np.array(urgensi_encoded)  # Tingkat urgensi sebagai label
        
        return torch.tensor(features, dtype=torch.float32), torch.tensor(labels, dtype=torch.long), urgensi_encoded
    except Exception as e:
        st.error(f"Kesalahan saat memproses data: {e}")
        return None, None, None

# Model Transformer
class TransformerModel(nn.Module):
    def __init__(self, input_size, model_dim, num_classes, num_heads, num_layers):
        super(TransformerModel, self).__init__()
        self.embedding = nn.Linear(input_size, model_dim)
        self.transformer = nn.Transformer(
            d_model=model_dim,
            nhead=num_heads,
            num_encoder_layers=num_layers
        )
        self.fc_out = nn.Linear(model_dim, num_classes)

    def forward(self, x):
        x = self.embedding(x)
        x = x.unsqueeze(0)  # Tambahkan dimensi batch
        transformer_out = self.transformer(x, x)
        output = self.fc_out(transformer_out[-1, :, :])
        return output

# Fungsi untuk prediksi
def predict(model, input_data):
    model.eval()
    with torch.no_grad():
        output = model(input_data)
        _, predicted = torch.max(output, 1)
        return predicted

# Fungsi utama untuk Streamlit
def main():
    st.title('Prediksi Tingkat Urgensi Laporan')

    # Memuat data
    data = load_data()
    if not data:
        return

    X, y, urgensi_encoded = process_data(data)
    if X is None or y is None:
        return

    class_weights = compute_class_weight('balanced', classes=np.unique(urgensi_encoded), y=urgensi_encoded)
    class_weights = torch.tensor(class_weights, dtype=torch.float32)

    # Inisialisasi model
    input_size = X.shape[1]
    model_dim = 64
    num_classes = len(np.unique(urgensi_encoded))
    num_heads = 4
    num_layers = 2
    model = TransformerModel(input_size, model_dim, num_classes, num_heads, num_layers)

    # Menyiapkan loss function dan optimizer
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # Pelatihan model
    epochs = 10
    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        output = model(X)
        loss = criterion(output, y)
        loss.backward()
        optimizer.step()

    # Prediksi berdasarkan input tanggal
    input_date = st.date_input("Pilih Tanggal Laporan", min_value=datetime(2024, 1, 1))
    start_date = datetime.strptime("01/01/2024", "%d/%m/%Y").date()
    input_date_int = (input_date - start_date).days
    input_tensor = torch.tensor([[input_date_int]], dtype=torch.float32)
    predicted_urgency = predict(model, input_tensor)
    urgency_classes = ['Rendah', 'Sedang', 'Tinggi']
    predicted_class = urgency_classes[predicted_urgency.item()]
    st.write(f"Prediksi Tingkat Urgensi: {predicted_class}")
