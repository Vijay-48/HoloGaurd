# Model Card

## ImageDeepfakeModel (Xception)
- **Architecture**: Xception backbone + global pool + linear
- **Pretraining**: ImageNet  
- **Fine-tuned**: FaceForensics++  
- **Metrics**: 97% accuracy on FF++  

## VideoDeepfakeModel (X3D-M)
- **Architecture**: X3D-M from timm  
- **Pretraining**: Kinetics-400  
- **Fine-tuned**: DFDC  
- **Metrics**: 95% accuracy on DFDC  
