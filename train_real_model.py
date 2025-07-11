import os
import numpy as np
import librosa
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.utils.class_weight import compute_class_weight
from collections import Counter

# Replace this with your actual dataset directory
RAVDESS_DIR = "ravdess-data"

emotion_map = {
    '01': 'neutral',
    '02': 'calm',
    '03': 'happy',
    '04': 'sad',
    '05': 'angry',
    '06': 'fearful',
    '07': 'disgust',
    '08': 'surprise'
}

def extract_features(file_path):
    y, sr = librosa.load(file_path, duration=3, sr=22050)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
    return np.mean(mfcc.T, axis=0)

X = []
y = []

for root, _, files in os.walk(RAVDESS_DIR):
    for file in files:
        if file.endswith(".wav"):
            emotion_code = file.split("-")[2]
            emotion = emotion_map.get(emotion_code)
            if emotion:
                file_path = os.path.join(root, file)
                features = extract_features(file_path)
                X.append(features)
                y.append(emotion)

print("Loaded samples:", len(X))
print("Class distribution:", Counter(y))

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    np.array(X), np.array(y), test_size=0.2, random_state=42, stratify=y
)

# Compute class weights
class_weights = compute_class_weight(class_weight="balanced", classes=np.unique(y_train), y=y_train)
class_weight_dict = dict(zip(np.unique(y_train), class_weights))

model = RandomForestClassifier(n_estimators=200, class_weight=class_weight_dict)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

# Save model only (no scaler needed)
with open("emotion_model.pkl", "wb") as f:
    pickle.dump(model, f)
