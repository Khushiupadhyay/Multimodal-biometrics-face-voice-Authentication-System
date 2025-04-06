import os
import numpy as np
import cv2
import torch
import torchaudio
import sounddevice as sd
import soundfile as sf
import librosa
from scipy.spatial.distance import cosine
from model import ECAPA_TDNN
from insightface.app import FaceAnalysis

# Initialize voice model
voice_model = ECAPA_TDNN(input_size=80)
voice_model.eval()

# Use ArcFace for face recognition
face_analyzer = FaceAnalysis(name='buffalo_l')
face_analyzer.prepare(ctx_id=0)

def extract_face_features(face_path):
    """Extract face embeddings using ArcFace"""
    try:
        img = cv2.imread(face_path)
        if img is None:
            print("❌ ERROR: Could not read the image!")
            return None

        faces = face_analyzer.get(img)
        if len(faces) == 0:
            print("❌ ERROR: No face detected!")
            return None

        return faces[0].normed_embedding  # ArcFace Embedding
    except Exception as e:
        print(f"❌ ERROR during face extraction: {str(e)}")
        return None

def compare_faces(new_face_path, stored_embedding_path):
    """Compare face embeddings and return similarity score"""
    try:
        new_embedding = extract_face_features(new_face_path)
        if new_embedding is None:
            return 0.0

        stored_embedding = np.load(stored_embedding_path)
        similarity = np.dot(stored_embedding, new_embedding)

        # Normalize score to 0-1 range, assuming similarity is typically between 0 and 1
        # but can sometimes be slightly higher
        normalized_score = min(max(similarity, 0.0), 1.0)
        return normalized_score
    except Exception as e:
        print(f"❌ ERROR during face comparison: {str(e)}")
        return 0.0

def record_audio(filename, phrase, duration=5, samplerate=16000):
    """Record audio from microphone"""
    try:
        dir_path = os.path.dirname(filename)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

        print("Recording... Please say the given phrase.")
        audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='float32')
        sd.wait()

        sf.write(filename, audio, samplerate)
        print(f"✅ Recording saved at {filename}.")
        return True
    except Exception as e:
        print(f"❌ ERROR during audio recording: {str(e)}")
        return False

def extract_voice_features(audio_path):
    """Extract voice embeddings using the ECAPA-TDNN model"""
    try:
        waveform, sample_rate = torchaudio.load(audio_path)
        waveform = waveform.mean(dim=0, keepdim=True)

        resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
        waveform = resampler(waveform)

        mel_transform = torchaudio.transforms.MelSpectrogram(
            sample_rate=16000,
            n_mels=80,
            n_fft=400,
            hop_length=160
        )
        
        mel_spectrogram = mel_transform(waveform)
        mel_spectrogram = mel_spectrogram.unsqueeze(0) if mel_spectrogram.dim() == 2 else mel_spectrogram

        with torch.no_grad():
            embedding = voice_model(mel_spectrogram)

        return embedding.squeeze().numpy()
    except Exception as e:
        print(f"❌ ERROR during voice feature extraction: {str(e)}")
        return np.zeros(256)  # Return zero embedding in case of error

def compare_voices(stored_embedding_path, new_audio_path):
    """Compare voice embeddings and return similarity score"""
    try:
        stored_embedding = np.load(stored_embedding_path)
        new_embedding = extract_voice_features(new_audio_path)

        # Calculate cosine similarity (1 - cosine distance)
        similarity = 1 - cosine(stored_embedding, new_embedding)
        
        # Normalize score to 0-1 range
        normalized_score = min(max(similarity, 0.0), 1.0)
        return normalized_score
    except Exception as e:
        print(f"❌ ERROR during voice comparison: {str(e)}")
        return 0.0