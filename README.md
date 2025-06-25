HALOGAURD

````markdown
Deepfake Detector

A system to detect deepfakes using image and video analysis.

---

1. Prerequisites

Install system tools

```bash
# Ubuntu / Debian
sudo apt update
sudo apt install -y python3 python3-venv python3-pip ffmpeg
````

Clone the repo

```bash
git clone https://github.com/your-org/deepfake-detector.git
cd deepfake-detector
```

Create `.env`

```bash
cp .env.example .env
# Edit .env with real values:
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/deepfake
# SECRET_KEY=some-long-random-string
```

---

2. Python Virtual Environment & Dependencies

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
cd ..
```

---

3. Data Pipeline

Download datasets

```bash
cd data_pipeline
python3 download_datasets.py
```

This saves FF++ and DFDC zips to `~/datasets/deepfake/`.

Unzip archives

```bash
unzip ~/datasets/deepfake/FaceForensicspp.zip -d ~/datasets/deepfake/FFpp
unzip ~/datasets/deepfake/DFDC.zip -d ~/datasets/deepfake/DFDC
```

Extract frames

```bash
python3 preprocess_frames.py \
  --videos_dir ~/datasets/deepfake/FFpp/videos \
  --output_dir ~/datasets/deepfake/frames/ffpp \
  --fps 1

python3 preprocess_frames.py \
  --videos_dir ~/datasets/deepfake/DFDC/videos \
  --output_dir ~/datasets/deepfake/frames/dfdc \
  --fps 1
```

Extract audio (for lip-sync models)

```bash
python3 extract_audio.py \
  --videos_dir ~/datasets/deepfake/FFpp/videos \
  --output_dir ~/datasets/deepfake/audio/ffpp
```

Train image model

```bash
python3 train_models.py \
  --data_dir ~/datasets/deepfake/frames/ffpp \
  --epochs 5 \
  --batch_size 32
```

Weights will be saved to:

```
pretrained_models/image_model/xception_ffpp_v1.pt
```

Train video model

```bash
python3 train_video_model.py \
  --data_dir ~/datasets/deepfake/DFDC/videos \
  --epochs 3 \
  --batch_size 8
```

Weights saved to:

```
pretrained_models/video_model/x3d_ffdc_v1.pt
```

---

4. Populate `pretrained_models/`

Ensure the following files exist:

```plaintext
pretrained_models/
├── image_model/xception_ffpp_v1.pt
├── video_model/x3d_ffdc_v1.pt
├── syncnet/syncnet.pth         # download from SyncNet repo
└── rppg/pulse_cnn.onnx         # export from DeepFakesON-Phys
```

---

5. Database Setup

Run Postgres

Option 1: Local install

Ensure Postgres is running and matches `.env` credentials.

Option 2: Docker

```bash
docker run -d --name deepfake-db -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=deepfake -p 5432:5432 postgres:13
```

Create tables

```bash
cd backend
alembic upgrade head
cd ..
```

Or start the backend to auto-create tables.

---

6. Running the Backend

```bash
cd backend
source .venv/bin/activate
uvicorn main:app --reload
```

Verify

* API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
* Health check: `GET http://localhost:8000/`

---

7. Running Tests

```bash
cd backend
source .venv/bin/activate
pytest -q
```

This runs:

* `tests/test_api.py`: API integration
* `tests/test_services.py`: VisionService unit tests
* `tests/test_utils.py`: Frame extraction

---

8. Docker Compose (Local Dev)

```bash
docker-compose up --build
```

* Backend: [http://localhost:8000](http://localhost:8000)
* Postgres DB: port 5432

---

9. CI/CD

GitHub Actions workflow (`.github/workflows/ci.yml`) includes:

* Code checkout
* Postgres setup
* Dependency installation
* Alembic migrations
* Test execution with `pytest`

---

10. Frontend Integration

Point your frontend (e.g. Loveable.dev UI) to:

REST Endpoints

* `POST /detect/image`
* `POST /detect/video`
* `GET /history/`
* `POST /auth/signup`
* `POST /auth/token`

WebSocket

```
ws://localhost:8000/detect/stream
```

```

---

Let me know if you'd like me to generate this as a downloadable file or if you'd like any sections customized!
```
