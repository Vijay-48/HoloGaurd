# System Architecture

1. **Frontend (Loveable.dev)**  
2. **FastAPI Backend**  
   - **Routes**: `/auth`, `/detect/image`, `/detect/video`, `/detect/stream`, `/history`
   - **Services**: Vision, LipSync, RPPG, Fusion, Explain
   - **Models**: Image (Xception), Video (X3D), SyncNet
3. **Database**: Postgres (Users, ScanHistory)
4. **Data Pipeline**:  
   - Download ➔ Preprocess ➔ Train
5. **Deployment**: Docker Compose, Kubernetes
