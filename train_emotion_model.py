# train_emotion_model.py
import os
import numpy as np
import librosa
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from collections import Counter

# Emotion mapping for CREMA-D
crema_emotion_map = {
    'NEU': 'neutral',
    'HAP': 'happy',
    'SAD': 'sad',
    'ANG': 'angry',
    'FEAR': 'fear',
    'DISG': 'disgust'
}

# Emotion mapping for SAVEE
savee_emotion_map = {
    'a': 'angry',
    'd': 'disgust',
    'f': 'fear',
    'h': 'happy',
    'n': 'neutral',
    'sa': 'sad',
    'su': 'surprise'
}

def extract_features(file_path):
    y, sr = librosa.load(file_path, duration=3, sr=22050)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
    return np.mean(mfcc.T, axis=0)

def load_crema_d(folder):
    features, labels = [], []
    for file in os.listdir(folder):
        if file.endswith(".wav"):
            emotion_code = file.split("_")[2]
            emotion = crema_emotion_map.get(emotion_code)
            if emotion:
                path = os.path.join(folder, file)
                features.append(extract_features(path))
                labels.append(emotion)
    return features, labels

def load_savee(folder):
    features, labels = [], []
    for file in os.listdir(folder):
        if file.endswith(".wav"):
            parts = file.split("_")[1].replace(".wav", "")
            for key in savee_emotion_map:
                if parts.startswith(key):
                    emotion = savee_emotion_map[key]
                    path = os.path.join(folder, file)
                    features.append(extract_features(path))
                    labels.append(emotion)
                    break
    return features, labels

def main():
    crema_path = "datasets/crema-d"
    savee_path = "datasets/savee"

    print("🔍 Loading CREMA-D...")
    crema_X, crema_y = load_crema_d(crema_path)

    print("🔍 Loading SAVEE...")
    savee_X, savee_y = load_savee(savee_path)

    X = np.array(crema_X + savee_X)
    y = np.array(crema_y + savee_y)

    print("📊 Emotion distribution:", Counter(y))

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print("🧠 Training model...")
    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    print("🧪 Evaluation:")
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred))

    with open("emotion_model.pkl", "wb") as f:
        pickle.dump(model, f)

    print("✅ Model saved to emotion_model.pkl")

if __name__ == "__main__":
    main()
