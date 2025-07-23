# models/lip_model.py
import torch
import torch.nn as nn
import cv2
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class SyncNet(nn.Module):
    """SyncNet architecture for lip-sync detection"""
    def __init__(self):
        super(SyncNet, self).__init__()
        # Face encoder
        self.face_encoder = nn.Sequential(
            nn.Conv3d(3, 32, kernel_size=(5, 7, 7), stride=(1, 2, 2), padding=(2, 3, 3)),
            nn.BatchNorm3d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool3d(kernel_size=(1, 3, 3), stride=(1, 2, 2), padding=(0, 1, 1)),
            
            nn.Conv3d(32, 64, kernel_size=(1, 5, 5), stride=(1, 2, 2), padding=(0, 2, 2)),
            nn.BatchNorm3d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool3d(kernel_size=(1, 3, 3), stride=(1, 2, 2), padding=(0, 1, 1)),
            
            nn.Conv3d(64, 128, kernel_size=(1, 3, 3), stride=(1, 2, 2), padding=(0, 1, 1)),
            nn.BatchNorm3d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool3d(kernel_size=(1, 3, 3), stride=(1, 2, 2), padding=(0, 1, 1)),
            
            nn.AdaptiveAvgPool3d((1, 1, 1))
        )
        
        # Audio encoder  
        self.audio_encoder = nn.Sequential(
            nn.Conv1d(13, 32, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm1d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool1d(kernel_size=3, stride=2, padding=1),
            
            nn.Conv1d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm1d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool1d(kernel_size=3, stride=2, padding=1),
            
            nn.Conv1d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool1d(1)
        )
        
        # Fusion layer
        self.fusion = nn.Sequential(
            nn.Linear(256, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(128, 1)
        )
        
    def forward(self, face, audio):
        face_feat = self.face_encoder(face).view(face.size(0), -1)
        audio_feat = self.audio_encoder(audio).view(audio.size(0), -1)
        combined = torch.cat([face_feat, audio_feat], dim=1)
        return self.fusion(combined)

class SyncNetWrapper:
    def __init__(self, model_path: Path):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = SyncNet().to(self.device)
        
        if model_path.exists():
            try:
                checkpoint = torch.load(model_path, map_location=self.device)
                # Handle different checkpoint formats
                if 'state_dict' in checkpoint:
                    self.model.load_state_dict(checkpoint['state_dict'])
                elif 'model_state_dict' in checkpoint:
                    self.model.load_state_dict(checkpoint['model_state_dict'])
                else:
                    self.model.load_state_dict(checkpoint)
                self.model.eval()
                logger.info(f"Loaded SyncNet model from {model_path}")
            except Exception as e:
                logger.warning(f"Failed to load SyncNet model: {e}. Using random weights.")
        else:
            logger.warning(f"SyncNet model not found at {model_path}. Using random weights.")
    
    def extract_mfcc_features(self, audio, sr, n_mfcc=13, n_fft=512, hop_length=160):
        """Extract MFCC features from audio signal"""
        import librosa
        
        # Extract MFCCs
        mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=n_mfcc, 
                                   n_fft=n_fft, hop_length=hop_length)
        return mfccs

    def predict(self, frames, audio, sr):
        try:
            # Sample frames uniformly (5 frames for sync detection)
            if len(frames) < 5:
                return 0.3  # Low sync score for insufficient frames
                
            frame_indices = np.linspace(0, len(frames)-1, 5, dtype=int)
            selected_frames = [frames[i] for i in frame_indices]
            
            # Process video frames
            face_frames = []
            for frame_path in selected_frames:
                img = cv2.imread(frame_path)
                if img is None:
                    continue
                # Resize to standard size
                img = cv2.resize(img, (224, 224))
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img = img.astype(np.float32) / 255.0
                face_frames.append(img)
            
            if len(face_frames) < 5:
                return 0.3
                
            # Convert to tensor [1, 3, T, H, W]
            face_tensor = torch.FloatTensor(face_frames).permute(3, 0, 1, 2).unsqueeze(0)
            face_tensor = face_tensor.to(self.device)
            
            # Extract audio features
            mfccs = self.extract_mfcc_features(audio, sr)
            # Ensure consistent time dimension
            target_frames = face_tensor.size(2)  # T dimension
            if mfccs.shape[1] > target_frames:
                mfccs = mfccs[:, :target_frames]
            elif mfccs.shape[1] < target_frames:
                # Pad or repeat
                repeat_factor = target_frames // mfccs.shape[1] + 1
                mfccs = np.tile(mfccs, (1, repeat_factor))[:, :target_frames]
            
            audio_tensor = torch.FloatTensor(mfccs).unsqueeze(0).to(self.device)
            
            # Run inference
            with torch.no_grad():
                output = self.model(face_tensor, audio_tensor)
                sync_score = torch.sigmoid(output).item()
            
            return sync_score
            
        except Exception as e:
            logger.error(f"Error in SyncNet prediction: {e}")
            return 0.5  # Default neutral score on error
