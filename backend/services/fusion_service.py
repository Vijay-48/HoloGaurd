import numpy as np
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class FusionService:
    def __init__(self):
        # Weights for different modalities based on their reliability
        self.modality_weights = {
            "vision": 0.4,      # Visual features are quite reliable
            "lip_sync": 0.3,    # Lip-sync is important for video deepfakes
            "physiological": 0.3  # rPPG signals can be telling
        }
        
        # Confidence thresholds
        self.confidence_thresholds = {
            "high": 0.8,
            "medium": 0.6,
            "low": 0.4
        }
    
    def calculate_confidence(self, scores: Dict[str, Any]) -> float:
        """Calculate overall confidence based on score consistency"""
        valid_scores = []
        for key, result in scores.items():
            if isinstance(result, dict) and "score" in result:
                valid_scores.append(result["score"])
        
        if len(valid_scores) < 2:
            return 0.5  # Low confidence with single modality
        
        # Calculate variance - lower variance means higher confidence
        score_variance = np.var(valid_scores)
        confidence = max(0.3, 1.0 - score_variance)
        return min(confidence, 1.0)
    
    def weighted_fusion(self, scores: Dict[str, Any]) -> float:
        """Weighted fusion of multiple modality scores"""
        weighted_sum = 0.0
        total_weight = 0.0
        
        for modality, result in scores.items():
            if isinstance(result, dict) and "score" in result:
                weight = self.modality_weights.get(modality, 0.2)
                score = result["score"]
                
                # Adjust weight based on modality reliability
                if modality == "vision" and result.get("prediction") != "unknown":
                    weight *= 1.2  # Boost vision if it's confident
                elif modality == "physiological" and result.get("prediction") == "unknown":
                    weight *= 0.5  # Reduce weight if rPPG failed
                
                weighted_sum += score * weight
                total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.5
    
    def determine_prediction(self, fused_score: float, confidence: float) -> str:
        """Determine final prediction with confidence consideration"""
        # Adjust threshold based on confidence
        if confidence > self.confidence_thresholds["high"]:
            threshold = 0.5
        elif confidence > self.confidence_thresholds["medium"]:
            threshold = 0.55  # Slightly higher threshold for medium confidence
        else:
            threshold = 0.6   # Higher threshold for low confidence
        
        return "fake" if fused_score > threshold else "real"
    
    def fuse_scores(self, scores: dict) -> dict:
        """Main fusion method combining all modality scores"""
        try:
            # Calculate weighted fusion score
            fused_score = self.weighted_fusion(scores)
            
            # Calculate confidence
            confidence = self.calculate_confidence(scores)
            
            # Determine final prediction
            prediction = self.determine_prediction(fused_score, confidence)
            
            # Prepare detailed results
            result = {
                "overall_score": fused_score,
                "overall_prediction": prediction, 
                "confidence": confidence,
                "fusion_method": "weighted_ensemble",
                "modality_weights": self.modality_weights
            }
            
            # Add individual modality contributions
            for modality, modality_result in scores.items():
                if isinstance(modality_result, dict):
                    result[f"{modality}_contribution"] = (
                        modality_result.get("score", 0.0) * 
                        self.modality_weights.get(modality, 0.2)
                    )
            
            logger.info(f"Fusion result: score={fused_score:.3f}, prediction={prediction}, confidence={confidence:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"Error in score fusion: {e}")
            # Fallback to simple average
            vals = [v["score"] for v in scores.values() if isinstance(v, dict) and "score" in v]
            avg = sum(vals) / len(vals) if vals else 0.5
            return {
                "overall_score": avg,
                "overall_prediction": "fake" if avg > 0.5 else "real",
                "confidence": 0.3,  # Low confidence due to error
                "fusion_method": "simple_average"
            }
