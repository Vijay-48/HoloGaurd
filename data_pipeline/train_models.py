#!/usr/bin/env python3
# data_pipeline/train_models.py
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import torchvision.transforms as T
from pathlib import Path
from models.image_model import ImageDeepfakeModel

class ImageDataset(Dataset):
    def __init__(self, root_dir, transform):
        self.samples = list(Path(root_dir).rglob("*.jpg"))
        self.transform = transform
    def __len__(self): return len(self.samples)
    def __getitem__(self, idx):
        path = self.samples[idx]
        label = 1 if "fake" in path.parts else 0
        img = T.ToTensor()(T.Resize((224,224))(T.Image.open(path).convert("RGB")))
        return self.transform(img), torch.tensor(label, dtype=torch.float32)

def train_image_model(data_dir, epochs=5, batch_size=32, lr=1e-4):
    transform = T.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
    dataset = ImageDataset(data_dir, transform)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    model = ImageDeepfakeModel().to("cuda")
    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        for x, y in loader:
            x, y = x.to("cuda"), y.to("cuda")
            optimizer.zero_grad()
            logits = model(x)
            loss = criterion(logits, y)
            loss.backward(); optimizer.step()
            total_loss += loss.item()
        print(f"Epoch {epoch+1}/{epochs} loss: {total_loss/len(loader):.4f}")
    torch.save(model.state_dict(), "pretrained_models/vit_deepfake.pt")
    print("Training complete. Weights saved.")
