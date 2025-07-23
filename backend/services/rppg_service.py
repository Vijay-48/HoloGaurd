import onnxruntime as ort
import cv2, numpy as np, time
import mediapipe as mp
from scipy.signal import butter, filtfilt
from pathlib import Path
from utils.config import get_settings
import logging

logger = logging.getLogger(__name__)
mp_face = mp.solutions.face_mesh.FaceMesh(static_image_mode=False)
settings = get_settings()

class RPPGService:
    def __init__(self):
        self.onnx_model = None
        model_path = Path(settings.RPPG_MODEL_PATH) if hasattr(settings, 'RPPG_MODEL_PATH') else Path("pretrained_models/pulse_cnn.onnx")
        
        if model_path.exists():
            try:
                self.onnx_model = ort.InferenceSession(str(model_path))
                logger.info(f"Loaded rPPG ONNX model from {model_path}")
            except Exception as e:
                logger.warning(f"Failed to load rPPG ONNX model: {e}. Using fallback method.")
        else:
            logger.warning(f"rPPG ONNX model not found at {model_path}. Using fallback method.")

    def extract_face_roi(self, frame):
        """Extract face ROI using MediaPipe"""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = mp_face.process(rgb)
        
        if not results.multi_face_landmarks:
            return None
            
        landmarks = results.multi_face_landmarks[0].landmark
        h, w, _ = rgb.shape
        
        # Define face ROI points (forehead, cheeks)
        roi_points = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288]
        points = np.array([[landmarks[i].x * w, landmarks[i].y * h] for i in roi_points], np.int32)
        
        # Create mask
        mask = np.zeros(rgb.shape[:2], np.uint8)
        cv2.fillConvexPoly(mask, points, 255)
        
        # Extract ROI
        roi = cv2.bitwise_and(rgb, rgb, mask=mask)
        return roi, mask

    def preprocess_for_onnx(self, frames):
        """Preprocess frames for ONNX model input"""
        processed_frames = []
        
        for frame in frames:
            # Resize to model input size (assuming 64x64)
            resized = cv2.resize(frame, (64, 64))
            # Normalize
            normalized = resized.astype(np.float32) / 255.0
            processed_frames.append(normalized)
        
        # Convert to NCHW format [1, C, T, H, W]
        batch = np.array(processed_frames).transpose(3, 0, 1, 2)  # [C, T, H, W]
        batch = np.expand_dims(batch, axis=0)  # [1, C, T, H, W]
        return batch

    async def detect_physiological(self, frame_paths: list) -> dict:
        start = time.time()
        
        try:
            # Sample frames for processing (max 30 frames)
            if len(frame_paths) > 30:
                indices = np.linspace(0, len(frame_paths)-1, 30, dtype=int)
                sampled_paths = [frame_paths[i] for i in indices]
            else:
                sampled_paths = frame_paths
            
            face_rois = []
            rgb_signals = []
            
            for fp in sampled_paths:
                img = cv2.imread(fp)
                if img is None:
                    continue
                    
                # Extract face ROI
                roi_result = self.extract_face_roi(img)
                if roi_result is None:
                    continue
                    
                roi, mask = roi_result
                face_rois.append(roi)
                
                # Extract average RGB signal
                mean_rgb = cv2.mean(roi, mask=mask)[:3]
                rgb_signals.append(mean_rgb)
            
            if len(face_rois) < 5:
                return {"prediction": "unknown", "score": 0.0, "processing_time": time.time() - start}
            
            # Use ONNX model if available
            if self.onnx_model is not None:
                try:
                    # Preprocess for ONNX model
                    input_batch = self.preprocess_for_onnx(face_rois)
                    input_name = self.onnx_model.get_inputs()[0].name
                    
                    # Run ONNX inference
                    output = self.onnx_model.run(None, {input_name: input_batch})
                    physiological_score = float(output[0][0])  # Assuming single output
                    
                    prediction = "physio_present" if physiological_score > 0.5 else "absent"
                    return {
                        "prediction": prediction,
                        "score": physiological_score,
                        "processing_time": time.time() - start
                    }
                    
                except Exception as e:
                    logger.error(f"ONNX model inference failed: {e}. Falling back to signal processing.")
            
            # Fallback to signal processing method
            signals = np.array([np.mean(signal) for signal in rgb_signals])
            
            # Apply bandpass filter for heart rate range (0.75-2.5 Hz @ 30fps)
            if len(signals) >= 10:
                try:
                    b, a = butter(1, [0.75/15, 2.5/15], btype='band')  # Adjusted for sampling rate
                    filtered_signal = filtfilt(b, a, signals)
                    power = float(np.var(filtered_signal))
                    
                    # Normalize power to probability
                    physiological_score = min(max(power / 2.0, 0.0), 1.0)
                except Exception as e:
                    logger.error(f"Signal processing failed: {e}")
                    physiological_score = 0.3
            else:
                physiological_score = 0.3
            
            prediction = "physio_present" if physiological_score > 0.5 else "absent"
            return {
                "prediction": prediction,
                "score": physiological_score,
                "processing_time": time.time() - start
            }
            
        except Exception as e:
            logger.error(f"Error in rPPG detection: {e}")
            return {"prediction": "unknown", "score": 0.0, "processing_time": time.time() - start}
