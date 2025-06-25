import torch.nn as nn
import timm

class ImageDeepfakeModel(nn.Module):
    def __init__(self, pretrained: bool = True):
        super().__init__()
        backbone = timm.create_model('xception', pretrained=pretrained, num_classes=0, global_pool='')
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Linear(backbone.num_features, 1)
        self.backbone = backbone

    def forward(self, x):
        feat = self.backbone(x)
        pooled = self.pool(feat).view(feat.size(0), -1)
        return self.fc(pooled).squeeze(1)
