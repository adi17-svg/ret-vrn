# model_loader.py
import librosa
import numpy as np
import pickle

with open("emotion_model.pkl", "rb") as f:
    model = pickle.load(f)

def extract_features(file_path):
    y, sr = librosa.load(file_path, duration=3, sr=22050)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
    return np.mean(mfcc.T, axis=0).reshape(1, -1)

def predict_emotion(file_path):
    features = extract_features(file_path)
    prediction = model.predict(features)[0]
    return prediction
