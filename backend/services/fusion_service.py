class FusionService:
    def fuse_scores(self, scores: dict) -> dict:
        vals = [v["score"] for v in scores.values() if isinstance(v, dict)]
        avg = sum(vals)/len(vals) if vals else 0.0
        return {"overall_score": avg, "overall_prediction": "fake" if avg>0.5 else "real", "confidence": avg}
