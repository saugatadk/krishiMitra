"""
U2-Net: Going Deeper with Nested U-Structure for Salient Object Detection
Qin et al. (Pattern Recognition 2020)
Implementation includes RSU-7, RSU-6, RSU-5, RSU-4, RSU-4F, full U2NET, and U2NETP (compact).
Includes automated weights manager with local caching and offline fallback.
"""

import os
import urllib.request
import logging
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import cv2
from pathlib import Path

logger = logging.getLogger(__name__)

# Standard U2-Net Pretrained Weights URLs
U2NET_URLS = [
    "https://huggingface.co/akhaliq/CLIPasso/resolve/main/u2net.pth",
    "https://huggingface.co/flashingtt/U-2-Net/resolve/main/u2net.pth",
]


class REBNCONV(nn.Module):
    """Convolution + BatchNorm2d + ReLU block with dilation support."""
    def __init__(self, in_ch=3, out_ch=3, dirate=1):
        super(REBNCONV, self).__init__()
        self.conv_s1 = nn.Conv2d(in_ch, out_ch, 3, padding=dirate, dilation=dirate)
        self.bn_s1 = nn.BatchNorm2d(out_ch)
        self.relu_s1 = nn.ReLU(inplace=True)

    def forward(self, x):
        return self.relu_s1(self.bn_s1(self.conv_s1(x)))


def _upsample_like(src, tar):
    return F.interpolate(src, size=tar.shape[2:], mode='bilinear', align_corners=False)


class RSU7(nn.Module):
    """Residual U-block with 7 levels."""
    def __init__(self, in_ch=3, mid_ch=12, out_ch=3):
        super(RSU7, self).__init__()
        self.rebnconvin = REBNCONV(in_ch, out_ch, dirate=1)

        self.rebnconv1 = REBNCONV(out_ch, mid_ch, dirate=1)
        self.pool1 = nn.MaxPool2d(2, stride=2, ceil_mode=True)

        self.rebnconv2 = REBNCONV(mid_ch, mid_ch, dirate=1)
        self.pool2 = nn.MaxPool2d(2, stride=2, ceil_mode=True)

        self.rebnconv3 = REBNCONV(mid_ch, mid_ch, dirate=1)
        self.pool3 = nn.MaxPool2d(2, stride=2, ceil_mode=True)

        self.rebnconv4 = REBNCONV(mid_ch, mid_ch, dirate=1)
        self.pool4 = nn.MaxPool2d(2, stride=2, ceil_mode=True)

        self.rebnconv5 = REBNCONV(mid_ch, mid_ch, dirate=1)
        self.pool5 = nn.MaxPool2d(2, stride=2, ceil_mode=True)

        self.rebnconv6 = REBNCONV(mid_ch, mid_ch, dirate=1)
        self.rebnconv7 = REBNCONV(mid_ch, mid_ch, dirate=2)

        self.rebnconv6d = REBNCONV(mid_ch * 2, mid_ch, dirate=1)
        self.rebnconv5d = REBNCONV(mid_ch * 2, mid_ch, dirate=1)
        self.rebnconv4d = REBNCONV(mid_ch * 2, mid_ch, dirate=1)
        self.rebnconv3d = REBNCONV(mid_ch * 2, mid_ch, dirate=1)
        self.rebnconv2d = REBNCONV(mid_ch * 2, mid_ch, dirate=1)
        self.rebnconv1d = REBNCONV(mid_ch * 2, out_ch, dirate=1)

    def forward(self, x):
        hx = x
        hxin = self.rebnconvin(hx)

        h1 = self.rebnconv1(hxin)
        hx = self.pool1(h1)

        h2 = self.rebnconv2(hx)
        hx = self.pool2(h2)

        h3 = self.rebnconv3(hx)
        hx = self.pool3(h3)

        h4 = self.rebnconv4(hx)
        hx = self.pool4(h4)

        h5 = self.rebnconv5(hx)
        hx = self.pool5(h5)

        h6 = self.rebnconv6(hx)
        h7 = self.rebnconv7(h6)

        h6d = self.rebnconv6d(torch.cat((h7, h6), 1))
        h6dup = _upsample_like(h6d, h5)

        h5d = self.rebnconv5d(torch.cat((h6dup, h5), 1))
        h5dup = _upsample_like(h5d, h4)

        h4d = self.rebnconv4d(torch.cat((h5dup, h4), 1))
        h4dup = _upsample_like(h4d, h3)

        h3d = self.rebnconv3d(torch.cat((h4dup, h3), 1))
        h3dup = _upsample_like(h3d, h2)

        h2d = self.rebnconv2d(torch.cat((h3dup, h2), 1))
        h2dup = _upsample_like(h2d, h1)

        h1d = self.rebnconv1d(torch.cat((h2dup, h1), 1))
        return h1d + hxin


class RSU6(nn.Module):
    """Residual U-block with 6 levels."""
    def __init__(self, in_ch=3, mid_ch=12, out_ch=3):
        super(RSU6, self).__init__()
        self.rebnconvin = REBNCONV(in_ch, out_ch, dirate=1)

        self.rebnconv1 = REBNCONV(out_ch, mid_ch, dirate=1)
        self.pool1 = nn.MaxPool2d(2, stride=2, ceil_mode=True)

        self.rebnconv2 = REBNCONV(mid_ch, mid_ch, dirate=1)
        self.pool2 = nn.MaxPool2d(2, stride=2, ceil_mode=True)

        self.rebnconv3 = REBNCONV(mid_ch, mid_ch, dirate=1)
        self.pool3 = nn.MaxPool2d(2, stride=2, ceil_mode=True)

        self.rebnconv4 = REBNCONV(mid_ch, mid_ch, dirate=1)
        self.pool4 = nn.MaxPool2d(2, stride=2, ceil_mode=True)

        self.rebnconv5 = REBNCONV(mid_ch, mid_ch, dirate=1)
        self.rebnconv6 = REBNCONV(mid_ch, mid_ch, dirate=2)

        self.rebnconv5d = REBNCONV(mid_ch * 2, mid_ch, dirate=1)
        self.rebnconv4d = REBNCONV(mid_ch * 2, mid_ch, dirate=1)
        self.rebnconv3d = REBNCONV(mid_ch * 2, mid_ch, dirate=1)
        self.rebnconv2d = REBNCONV(mid_ch * 2, mid_ch, dirate=1)
        self.rebnconv1d = REBNCONV(mid_ch * 2, out_ch, dirate=1)

    def forward(self, x):
        hx = x
        hxin = self.rebnconvin(hx)

        h1 = self.rebnconv1(hxin)
        hx = self.pool1(h1)

        h2 = self.rebnconv2(hx)
        hx = self.pool2(h2)

        h3 = self.rebnconv3(hx)
        hx = self.pool3(h3)

        h4 = self.rebnconv4(hx)
        hx = self.pool4(h4)

        h5 = self.rebnconv5(hx)
        h6 = self.rebnconv6(h5)

        h5d = self.rebnconv5d(torch.cat((h6, h5), 1))
        h5dup = _upsample_like(h5d, h4)

        h4d = self.rebnconv4d(torch.cat((h5dup, h4), 1))
        h4dup = _upsample_like(h4d, h3)

        h3d = self.rebnconv3d(torch.cat((h4dup, h3), 1))
        h3dup = _upsample_like(h3d, h2)

        h2d = self.rebnconv2d(torch.cat((h3dup, h2), 1))
        h2dup = _upsample_like(h2d, h1)

        h1d = self.rebnconv1d(torch.cat((h2dup, h1), 1))
        return h1d + hxin


class RSU5(nn.Module):
    """Residual U-block with 5 levels."""
    def __init__(self, in_ch=3, mid_ch=12, out_ch=3):
        super(RSU5, self).__init__()
        self.rebnconvin = REBNCONV(in_ch, out_ch, dirate=1)

        self.rebnconv1 = REBNCONV(out_ch, mid_ch, dirate=1)
        self.pool1 = nn.MaxPool2d(2, stride=2, ceil_mode=True)

        self.rebnconv2 = REBNCONV(mid_ch, mid_ch, dirate=1)
        self.pool2 = nn.MaxPool2d(2, stride=2, ceil_mode=True)

        self.rebnconv3 = REBNCONV(mid_ch, mid_ch, dirate=1)
        self.pool3 = nn.MaxPool2d(2, stride=2, ceil_mode=True)

        self.rebnconv4 = REBNCONV(mid_ch, mid_ch, dirate=1)
        self.rebnconv5 = REBNCONV(mid_ch, mid_ch, dirate=2)

        self.rebnconv4d = REBNCONV(mid_ch * 2, mid_ch, dirate=1)
        self.rebnconv3d = REBNCONV(mid_ch * 2, mid_ch, dirate=1)
        self.rebnconv2d = REBNCONV(mid_ch * 2, mid_ch, dirate=1)
        self.rebnconv1d = REBNCONV(mid_ch * 2, out_ch, dirate=1)

    def forward(self, x):
        hx = x
        hxin = self.rebnconvin(hx)

        h1 = self.rebnconv1(hxin)
        hx = self.pool1(h1)

        h2 = self.rebnconv2(hx)
        hx = self.pool2(h2)

        h3 = self.rebnconv3(hx)
        hx = self.pool3(h3)

        h4 = self.rebnconv4(hx)
        h5 = self.rebnconv5(h4)

        h4d = self.rebnconv4d(torch.cat((h5, h4), 1))
        h4dup = _upsample_like(h4d, h3)

        h3d = self.rebnconv3d(torch.cat((h4dup, h3), 1))
        h3dup = _upsample_like(h3d, h2)

        h2d = self.rebnconv2d(torch.cat((h3dup, h2), 1))
        h2dup = _upsample_like(h2d, h1)

        h1d = self.rebnconv1d(torch.cat((h2dup, h1), 1))
        return h1d + hxin


class RSU4(nn.Module):
    """Residual U-block with 4 levels."""
    def __init__(self, in_ch=3, mid_ch=12, out_ch=3):
        super(RSU4, self).__init__()
        self.rebnconvin = REBNCONV(in_ch, out_ch, dirate=1)

        self.rebnconv1 = REBNCONV(out_ch, mid_ch, dirate=1)
        self.pool1 = nn.MaxPool2d(2, stride=2, ceil_mode=True)

        self.rebnconv2 = REBNCONV(mid_ch, mid_ch, dirate=1)
        self.pool2 = nn.MaxPool2d(2, stride=2, ceil_mode=True)

        self.rebnconv3 = REBNCONV(mid_ch, mid_ch, dirate=1)
        self.rebnconv4 = REBNCONV(mid_ch, mid_ch, dirate=2)

        self.rebnconv3d = REBNCONV(mid_ch * 2, mid_ch, dirate=1)
        self.rebnconv2d = REBNCONV(mid_ch * 2, mid_ch, dirate=1)
        self.rebnconv1d = REBNCONV(mid_ch * 2, out_ch, dirate=1)

    def forward(self, x):
        hx = x
        hxin = self.rebnconvin(hx)

        h1 = self.rebnconv1(hxin)
        hx = self.pool1(h1)

        h2 = self.rebnconv2(hx)
        hx = self.pool2(h2)

        h3 = self.rebnconv3(hx)
        h4 = self.rebnconv4(h3)

        h3d = self.rebnconv3d(torch.cat((h4, h3), 1))
        h3dup = _upsample_like(h3d, h2)

        h2d = self.rebnconv2d(torch.cat((h3dup, h2), 1))
        h2dup = _upsample_like(h2d, h1)

        h1d = self.rebnconv1d(torch.cat((h2dup, h1), 1))
        return h1d + hxin


class RSU4F(nn.Module):
    """Residual U-block with dilated convolutions (no pooling)."""
    def __init__(self, in_ch=3, mid_ch=12, out_ch=3):
        super(RSU4F, self).__init__()
        self.rebnconvin = REBNCONV(in_ch, out_ch, dirate=1)

        self.rebnconv1 = REBNCONV(out_ch, mid_ch, dirate=1)
        self.rebnconv2 = REBNCONV(mid_ch, mid_ch, dirate=2)
        self.rebnconv3 = REBNCONV(mid_ch, mid_ch, dirate=4)
        self.rebnconv4 = REBNCONV(mid_ch, mid_ch, dirate=8)

        self.rebnconv3d = REBNCONV(mid_ch * 2, mid_ch, dirate=4)
        self.rebnconv2d = REBNCONV(mid_ch * 2, mid_ch, dirate=2)
        self.rebnconv1d = REBNCONV(mid_ch * 2, out_ch, dirate=1)

    def forward(self, x):
        hx = x
        hxin = self.rebnconvin(hx)

        h1 = self.rebnconv1(hxin)
        h2 = self.rebnconv2(h1)
        h3 = self.rebnconv3(h2)
        h4 = self.rebnconv4(h3)

        h3d = self.rebnconv3d(torch.cat((h4, h3), 1))
        h2d = self.rebnconv2d(torch.cat((h3d, h2), 1))
        h1d = self.rebnconv1d(torch.cat((h2d, h1), 1))
        return h1d + hxin


class U2NET(nn.Module):
    """Full U2-Net Architecture with 11 Stages and Multi-Level Saliency Fusion."""
    def __init__(self, in_ch=3, out_ch=1):
        super(U2NET, self).__init__()

        # Encoder stages
        self.stage1 = RSU7(in_ch, 32, 64)
        self.pool12 = nn.MaxPool2d(2, stride=2, ceil_mode=True)

        self.stage2 = RSU6(64, 32, 128)
        self.pool23 = nn.MaxPool2d(2, stride=2, ceil_mode=True)

        self.stage3 = RSU5(128, 64, 256)
        self.pool34 = nn.MaxPool2d(2, stride=2, ceil_mode=True)

        self.stage4 = RSU4(256, 128, 512)
        self.pool45 = nn.MaxPool2d(2, stride=2, ceil_mode=True)

        self.stage5 = RSU4F(512, 256, 512)
        self.pool56 = nn.MaxPool2d(2, stride=2, ceil_mode=True)

        self.stage6 = RSU4F(512, 256, 512)

        # Decoder stages
        self.stage5d = RSU4F(1024, 256, 512)
        self.stage4d = RSU4(1024, 128, 256)
        self.stage3d = RSU5(512, 64, 128)
        self.stage2d = RSU6(256, 32, 64)
        self.stage1d = RSU7(128, 16, 64)

        # Multi-scale side outputs
        self.side1 = nn.Conv2d(64, out_ch, 3, padding=1)
        self.side2 = nn.Conv2d(64, out_ch, 3, padding=1)
        self.side3 = nn.Conv2d(128, out_ch, 3, padding=1)
        self.side4 = nn.Conv2d(256, out_ch, 3, padding=1)
        self.side5 = nn.Conv2d(512, out_ch, 3, padding=1)
        self.side6 = nn.Conv2d(512, out_ch, 3, padding=1)

        self.outconv = nn.Conv2d(6 * out_ch, out_ch, 1)

    def forward(self, x):
        hx = x

        # Stage 1
        h1 = self.stage1(hx)
        hx = self.pool12(h1)

        # Stage 2
        h2 = self.stage2(hx)
        hx = self.pool23(h2)

        # Stage 3
        h3 = self.stage3(hx)
        hx = self.pool34(h3)

        # Stage 4
        h4 = self.stage4(hx)
        hx = self.pool45(h4)

        # Stage 5
        h5 = self.stage5(hx)
        hx = self.pool56(h5)

        # Stage 6
        h6 = self.stage6(hx)
        hx6up = _upsample_like(h6, h5)

        # Decoders
        h5d = self.stage5d(torch.cat((hx6up, h5), 1))
        hx5up = _upsample_like(h5d, h4)

        h4d = self.stage4d(torch.cat((hx5up, h4), 1))
        hx4up = _upsample_like(h4d, h3)

        h3d = self.stage3d(torch.cat((hx4up, h3), 1))
        hx3up = _upsample_like(h3d, h2)

        h2d = self.stage2d(torch.cat((hx3up, h2), 1))
        hx2up = _upsample_like(h2d, h1)

        h1d = self.stage1d(torch.cat((hx2up, h1), 1))

        # Side output saliency predictions
        d1 = self.side1(h1d)
        d2 = self.side2(h2d)
        d2 = _upsample_like(d2, d1)

        d3 = self.side3(h3d)
        d3 = _upsample_like(d3, d1)

        d4 = self.side4(h4d)
        d4 = _upsample_like(d4, d1)

        d5 = self.side5(h5d)
        d5 = _upsample_like(d5, d1)

        d6 = self.side6(h6)
        d6 = _upsample_like(d6, d1)

        # Fuse all side predictions
        d0 = self.outconv(torch.cat((d1, d2, d3, d4, d5, d6), 1))

        return F.sigmoid(d0), F.sigmoid(d1), F.sigmoid(d2), F.sigmoid(d3), F.sigmoid(d4), F.sigmoid(d5), F.sigmoid(d6)


def load_u2net_model(weights_path: Path = None, device: str = "cpu") -> U2NET:
    """
    Instantiates U2NET and loads weights.
    Downloads official pretrained weights if not found locally.
    """
    model = U2NET(in_ch=3, out_ch=1)

    target_path = Path(weights_path) if weights_path else Path.home() / ".cache" / "u2net" / "u2net.pth"
    target_path.parent.mkdir(parents=True, exist_ok=True)

    if not target_path.exists():
        logger.info(f"U2-Net weights not found at {target_path}. Attempting download...")
        download_success = False
        for url in U2NET_URLS:
            try:
                logger.info(f"Downloading U2-Net weights from {url}...")
                urllib.request.urlretrieve(url, str(target_path))
                if target_path.exists() and target_path.stat().st_size > 10_000_000:
                    logger.info("U2-Net weights downloaded successfully.")
                    download_success = True
                    break
            except Exception as e:
                logger.warning(f"Download from {url} failed: {e}")

        if not download_success:
            logger.warning("Could not download external U2-Net weights. Model initialized without pretrained weights.")
            model.to(device)
            model.eval()
            return model

    if target_path.exists():
        try:
            state_dict = torch.load(str(target_path), map_location=device, weights_only=True)
            # Remove module prefix if trained under DataParallel
            clean_state_dict = {}
            for k, v in state_dict.items():
                clean_k = k.replace("module.", "")
                clean_state_dict[clean_k] = v
            model.load_state_dict(clean_state_dict, strict=False)
            logger.info(f"Loaded U2-Net weights from {target_path}")
        except Exception as e:
            logger.error(f"Error loading U2-Net weights from {target_path}: {e}")

    model.to(device)
    model.eval()
    return model


def predict_leaf_mask(img_bgr: np.ndarray, model: U2NET, device: str = "cpu", threshold: float = 0.5) -> np.ndarray:
    """
    Runs leaf saliency segmentation on input BGR image.
    Returns: Binary uint8 mask (0 or 255) of original image dimensions.
    """
    h_orig, w_orig = img_bgr.shape[:2]

    # Preprocessing for U2-Net: 320x320 RGB normalized
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img_rgb, (320, 320), interpolation=cv2.INTER_LINEAR)

    # Standard ImageNet normalization
    img_tensor = img_resized.astype(np.float32) / 255.0
    img_tensor = (img_tensor - np.array([0.485, 0.456, 0.406])) / np.array([0.229, 0.224, 0.225])
    img_tensor = torch.from_numpy(img_tensor.transpose(2, 0, 1)).unsqueeze(0).float().to(device)

    with torch.no_grad():
        d0, *_ = model(img_tensor)

    # Extract primary saliency map d0
    pred = d0[0, 0, :, :].cpu().numpy()

    # Normalize saliency prediction to [0, 1]
    pred_min, pred_max = pred.min(), pred.max()
    if pred_max - pred_min > 1e-6:
        pred = (pred - pred_min) / (pred_max - pred_min)
    else:
        pred = np.zeros_like(pred)

    # Resize back to original image dimensions
    pred_orig = cv2.resize(pred, (w_orig, h_orig), interpolation=cv2.INTER_LINEAR)

    # Binary thresholding
    binary_mask = (pred_orig >= threshold).astype(np.uint8) * 255

    # Refine mask with morphological closing to fill interior lesion holes
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel)

    return binary_mask
