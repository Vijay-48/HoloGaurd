import torch.nn as nn
import timm

class VideoDeepfakeModel(nn.Module):
    def __init__(self, pretrained: bool = True):
        super().__init__()
        # Use ResNet3D or create a simple temporal model since X3D is not available in timm
        # This is a simplified temporal model for video analysis
        self.backbone = timm.create_model('resnet18', pretrained=pretrained, num_classes=0, global_pool='')
        self.temporal_conv = nn.Conv3d(512, 256, kernel_size=(3, 1, 1), padding=(1, 0, 0))
        self.temporal_pool = nn.AdaptiveAvgPool3d((1, 1, 1))
        self.classifier = nn.Linear(256, 1)
        self.dropout = nn.Dropout(0.5)
        
    def forward(self, x):
        # x shape: [batch, channels, time, height, width]
        batch_size, channels, time_steps, height, width = x.shape
        
        # Process each frame through backbone
        x = x.permute(0, 2, 1, 3, 4)  # [batch, time, channels, height, width]
        x = x.contiguous().view(batch_size * time_steps, channels, height, width)
        
        # Extract spatial features
        spatial_features = self.backbone(x)  # [batch*time, features, h, w]
        
        # Reshape back to include temporal dimension
        _, feat_dim, feat_h, feat_w = spatial_features.shape
        spatial_features = spatial_features.view(batch_size, time_steps, feat_dim, feat_h, feat_w)
        spatial_features = spatial_features.permute(0, 2, 1, 3, 4)  # [batch, features, time, h, w]
        
        # Apply temporal convolution
        temporal_features = self.temporal_conv(spatial_features)
        
        # Global pooling
        pooled = self.temporal_pool(temporal_features).view(batch_size, -1)
        
        # Classification
        x = self.dropout(pooled)
        return self.classifier(x).squeeze(1)
