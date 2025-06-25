# Setup Guide

1. **Clone repo**  
2. **Create `.env`** from `.env.example`  
3. **Build & run**  
   ```bash
   docker-compose up --build
Run migrations

bash
Copy
Edit
alembic upgrade head
Access

Backend: http://localhost:8000

Docs: http://localhost:8000/docs

yaml
Copy
Edit

---

### `docs/deployment.md`

```markdown
# Deployment

- **CI**: GitHub Actions (`.github/workflows/ci.yml`)
- **Docker Compose**: local dev
- **Kubernetes**: use `deployment.yaml`, `service.yaml` (templates)
- **Cloud**: GCP Cloud Run or AWS ECS Fargate