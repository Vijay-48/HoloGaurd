import torch.nn as nn
import timm

class VideoDeepfakeModel(nn.Module):
    def __init__(self, pretrained: bool = True):
        super().__init__()
        self.model = timm.create_model('x3d_m', pretrained=pretrained, num_classes=1)

    def forward(self, x):
        return self.model(x).squeeze(1)
