"""
Deep Learning-based Cartoon Style Generator
Uses a trained neural network model for photo-to-cartoon conversion
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import numpy as np
import os
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class ResidualBlock(nn.Module):
    """Residual block with instance normalization"""
    def __init__(self, channels: int):
        super().__init__()
        self.conv1 = nn.Conv2d(channels, channels, 3, padding=1)
        self.conv2 = nn.Conv2d(channels, channels, 3, padding=1)
        self.in1 = nn.InstanceNorm2d(channels)
        self.in2 = nn.InstanceNorm2d(channels)
        
    def forward(self, x):
        residual = x
        out = F.relu(self.in1(self.conv1(x)))
        out = self.in2(self.conv2(out))
        return out + residual


class CartoonGenerator(nn.Module):
    """
    Generator network for photo-to-cartoon conversion.
    Architecture based on encoder-decoder with residual blocks.
    """
    def __init__(self, num_residual_blocks: int = 8):
        super().__init__()
        
        # Initial convolution
        self.initial = nn.Sequential(
            nn.Conv2d(3, 64, 7, padding=3),
            nn.InstanceNorm2d(64),
            nn.ReLU(inplace=True)
        )
        
        # Downsampling
        self.down1 = nn.Sequential(
            nn.Conv2d(64, 128, 3, stride=2, padding=1),
            nn.InstanceNorm2d(128),
            nn.ReLU(inplace=True)
        )
        self.down2 = nn.Sequential(
            nn.Conv2d(128, 256, 3, stride=2, padding=1),
            nn.InstanceNorm2d(256),
            nn.ReLU(inplace=True)
        )
        
        # Residual blocks
        self.residual_blocks = nn.Sequential(
            *[ResidualBlock(256) for _ in range(num_residual_blocks)]
        )
        
        # Upsampling
        self.up1 = nn.Sequential(
            nn.ConvTranspose2d(256, 128, 3, stride=2, padding=1, output_padding=1),
            nn.InstanceNorm2d(128),
            nn.ReLU(inplace=True)
        )
        self.up2 = nn.Sequential(
            nn.ConvTranspose2d(128, 64, 3, stride=2, padding=1, output_padding=1),
            nn.InstanceNorm2d(64),
            nn.ReLU(inplace=True)
        )
        
        # Output convolution
        self.output = nn.Sequential(
            nn.Conv2d(64, 3, 7, padding=3),
            nn.Tanh()
        )
    
    def forward(self, x):
        x = self.initial(x)
        x = self.down1(x)
        x = self.down2(x)
        x = self.residual_blocks(x)
        x = self.up1(x)
        x = self.up2(x)
        x = self.output(x)
        return x


class CartoonStyleTransfer:
    """
    Cartoon style transfer using trained deep learning model.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the cartoon style transfer.
        
        Args:
            model_path: Path to trained model weights
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"CartoonStyleTransfer using device: {self.device}")
        
        # Default model path
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.model_path = model_path or os.path.join(base_dir, "ml_weights", "cartoon_generator.pt")
        
        # Initialize model - LIGHTWEIGHT version matching trained model
        self.model = CartoonGenerator(num_residual_blocks=4)
        self.model = self.model.to(self.device)
        
        # Load weights if available
        self._load_model()
        
        # Set to evaluation mode
        self.model.eval()
        
        # Define transforms
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
        ])
        
        self.inverse_transform = transforms.Compose([
            transforms.Normalize(mean=[-1, -1, -1], std=[2, 2, 2]),
        ])
    
    def _load_model(self):
        """Load model weights if available."""
        if os.path.exists(self.model_path):
            try:
                state_dict = torch.load(self.model_path, map_location=self.device)
                self.model.load_state_dict(state_dict)
                logger.info(f"Loaded cartoon generator model from: {self.model_path}")
                self._model_loaded = True
            except Exception as e:
                logger.warning(f"Could not load model weights: {e}")
                self._model_loaded = False
        else:
            logger.warning(f"Model file not found: {self.model_path}")
            self._model_loaded = False
    
    def is_model_loaded(self) -> bool:
        """Check if model weights are loaded."""
        return getattr(self, '_model_loaded', False)
    
    def preprocess(self, image: Image.Image, max_size: int = 1024) -> torch.Tensor:
        """
        Preprocess image for model input.
        
        Args:
            image: PIL Image
            max_size: Maximum dimension size
            
        Returns:
            Preprocessed tensor
        """
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize if too large while maintaining aspect ratio
        w, h = image.size
        if max(w, h) > max_size:
            scale = max_size / max(w, h)
            new_w = int(w * scale)
            new_h = int(h * scale)
            # Ensure dimensions are divisible by 4 for the network
            new_w = (new_w // 4) * 4
            new_h = (new_h // 4) * 4
            image = image.resize((new_w, new_h), Image.LANCZOS)
        else:
            # Ensure dimensions are divisible by 4
            new_w = (w // 4) * 4
            new_h = (h // 4) * 4
            if (new_w, new_h) != (w, h):
                image = image.resize((new_w, new_h), Image.LANCZOS)
        
        # Apply transforms
        tensor = self.transform(image)
        tensor = tensor.unsqueeze(0)  # Add batch dimension
        
        return tensor.to(self.device), image.size
    
    def postprocess(self, tensor: torch.Tensor, original_size: Tuple[int, int]) -> Image.Image:
        """
        Postprocess model output to PIL Image.
        
        Args:
            tensor: Model output tensor
            original_size: Original image size (w, h)
            
        Returns:
            PIL Image
        """
        # Remove batch dimension
        tensor = tensor.squeeze(0)
        
        # Inverse normalize
        tensor = self.inverse_transform(tensor)
        
        # Clamp values to [0, 1]
        tensor = torch.clamp(tensor, 0, 1)
        
        # Convert to numpy
        image_np = tensor.cpu().numpy().transpose(1, 2, 0)
        image_np = (image_np * 255).astype(np.uint8)
        
        # Convert to PIL Image
        image = Image.fromarray(image_np)
        
        # Resize back to original size if needed
        if image.size != original_size:
            image = image.resize(original_size, Image.LANCZOS)
        
        return image
    
    def generate(self, image: Image.Image) -> Image.Image:
        """
        Generate cartoon style image from input photo.
        
        Args:
            image: Input PIL Image
            
        Returns:
            Cartoonified PIL Image
        """
        original_size = image.size
        
        # Preprocess
        input_tensor, proc_size = self.preprocess(image)
        
        # Generate
        with torch.no_grad():
            output_tensor = self.model(input_tensor)
        
        # Postprocess
        result = self.postprocess(output_tensor, original_size)
        
        return result
    
    def generate_from_path(self, image_path: str) -> Image.Image:
        """
        Generate cartoon from image file path.
        
        Args:
            image_path: Path to input image
            
        Returns:
            Cartoonified PIL Image
        """
        image = Image.open(image_path)
        return self.generate(image)
    
    def generate_from_numpy(self, image_np: np.ndarray) -> np.ndarray:
        """
        Generate cartoon from numpy array (BGR format from OpenCV).
        
        Args:
            image_np: Input image as numpy array (BGR)
            
        Returns:
            Cartoonified image as numpy array (BGR)
        """
        # Convert BGR to RGB
        image_rgb = image_np[:, :, ::-1]
        
        # Convert to PIL
        image_pil = Image.fromarray(image_rgb)
        
        # Generate
        result_pil = self.generate(image_pil)
        
        # Convert back to numpy BGR
        result_np = np.array(result_pil)[:, :, ::-1]
        
        return result_np


# Singleton instance
_cartoon_transfer_instance: Optional[CartoonStyleTransfer] = None


def get_cartoon_transfer() -> CartoonStyleTransfer:
    """Get or create singleton CartoonStyleTransfer instance."""
    global _cartoon_transfer_instance
    
    if _cartoon_transfer_instance is None:
        _cartoon_transfer_instance = CartoonStyleTransfer()
    
    return _cartoon_transfer_instance
