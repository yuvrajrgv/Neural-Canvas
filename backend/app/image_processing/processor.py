"""
Image Processing Engine
Combines OpenCV and Deep Learning for artistic transformations
"""
import cv2
import numpy as np
import os
from typing import Tuple
import uuid
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Try to import the DL-based cartoon generator
try:
    from app.ml.cartoon_generator import get_cartoon_transfer
    DL_CARTOON_AVAILABLE = True
    logger.info("Deep learning cartoon generator available")
except ImportError as e:
    DL_CARTOON_AVAILABLE = False
    logger.warning(f"Deep learning cartoon generator not available: {e}")


class ImageProcessor:
    """
    Image transformation processor with multiple artistic styles.
    Uses deep learning model for cartoon style when available.
    """
    
    def __init__(self, use_dl_model: bool = True):
        """
        Initialize the processor.
        
        Args:
            use_dl_model: Whether to use deep learning model for cartoon style
        """
        self.output_dir = settings.PROCESSED_DIR
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.use_dl_model = use_dl_model and DL_CARTOON_AVAILABLE
        self._cartoon_transfer = None
        
        if self.use_dl_model:
            try:
                self._cartoon_transfer = get_cartoon_transfer()
                if self._cartoon_transfer.is_model_loaded():
                    logger.info("Using deep learning model for cartoon generation")
                else:
                    logger.info("DL model not loaded, falling back to OpenCV")
                    self.use_dl_model = False
            except Exception as e:
                logger.warning(f"Failed to initialize DL cartoon model: {e}")
                self.use_dl_model = False
    
    def process_image(self, input_path: str, style: str) -> Tuple[str, str]:
        """
        Process image with specified style
        
        Args:
            input_path: Path to input image
            style: Style to apply (cartoon, pencil_sketch, color_pencil, edge_preserve, watercolor)
            
        Returns:
            Tuple of (processed_image_path, comparison_image_path)
        """
        # Read image
        img = cv2.imread(input_path)
        if img is None:
            raise ValueError(f"Could not read image: {input_path}")
        
        # Resize if too large (max 2000px on longest side)
        img = self._resize_if_needed(img, max_size=2000)
        
        # Apply style
        style_methods = {
            "cartoon": self._apply_cartoon_effect,
            "pencil_sketch": self._apply_pencil_sketch,
            "color_pencil": self._apply_color_pencil,
            "edge_preserve": self._apply_edge_preserve,
            "watercolor": self._apply_watercolor,
        }
        
        process_func = style_methods.get(style, self._apply_cartoon_effect)
        processed = process_func(img)
        
        # Generate output paths
        unique_id = uuid.uuid4().hex
        ext = ".png"
        processed_filename = f"processed_{unique_id}{ext}"
        comparison_filename = f"comparison_{unique_id}{ext}"
        
        processed_path = os.path.join(self.output_dir, processed_filename)
        comparison_path = os.path.join(self.output_dir, comparison_filename)
        
        # Save processed image
        cv2.imwrite(processed_path, processed)
        
        # Create and save comparison image
        comparison = self._create_comparison(img, processed)
        cv2.imwrite(comparison_path, comparison)
        
        return processed_path, comparison_path
    
    def _resize_if_needed(self, img: np.ndarray, max_size: int = 2000) -> np.ndarray:
        """Resize image if larger than max_size while maintaining aspect ratio"""
        h, w = img.shape[:2]
        if max(h, w) > max_size:
            scale = max_size / max(h, w)
            new_w = int(w * scale)
            new_h = int(h * scale)
            img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        return img
    
    def _apply_cartoon_effect(self, img: np.ndarray) -> np.ndarray:
        """
        Classic cartoon effect:
        1. Apply bilateral filter for smoothing while preserving edges
        2. Convert to grayscale and apply median blur
        3. Detect edges using adaptive thresholding
        4. Combine edges with color-quantized image
        """
        # Downscale for faster processing, then upscale
        h, w = img.shape[:2]
        
        # Step 1: Apply bilateral filter multiple times for smoothing
        color = img.copy()
        for _ in range(3):
            color = cv2.bilateralFilter(color, d=9, sigmaColor=75, sigmaSpace=75)
        
        # Step 2: Color quantization using K-means
        color = self._color_quantization(color, k=8)
        
        # Step 3: Convert to grayscale and detect edges
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 7)
        
        # Adaptive thresholding for edges
        edges = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            blockSize=9,
            C=2
        )
        
        # Step 4: Combine edges with color
        edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        cartoon = cv2.bitwise_and(color, edges_colored)
        
        return cartoon
    
    def _apply_pencil_sketch(self, img: np.ndarray) -> np.ndarray:
        """
        Pencil sketch effect:
        1. Convert to grayscale
        2. Invert the grayscale image
        3. Apply Gaussian blur to inverted image
        4. Blend using color dodge
        """
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Invert grayscale image
        inverted = 255 - gray
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(inverted, (21, 21), sigmaX=0, sigmaY=0)
        
        # Blend using color dodge
        sketch = self._dodge_blend(gray, blurred)
        
        # Convert back to BGR for consistency
        sketch_bgr = cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
        
        return sketch_bgr
    
    def _apply_color_pencil(self, img: np.ndarray) -> np.ndarray:
        """
        Color pencil effect:
        1. Apply stylization filter
        2. Enhance edges
        3. Blend with original colors
        """
        # Apply stylization
        stylized = cv2.stylization(img, sigma_s=60, sigma_r=0.07)
        
        # Create edge layer
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edges = cv2.dilate(edges, None)
        edges_inv = 255 - edges
        edges_colored = cv2.cvtColor(edges_inv, cv2.COLOR_GRAY2BGR)
        
        # Blend stylized with edges
        result = cv2.multiply(stylized, edges_colored, scale=1/255)
        
        # Enhance saturation
        hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = hsv[:, :, 1] * 1.3  # Increase saturation
        hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
        result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        return result
    
    def _apply_edge_preserve(self, img: np.ndarray) -> np.ndarray:
        """
        Edge-preserving smooth effect:
        1. Apply edge-preserving filter
        2. Enhance details
        3. Apply subtle sharpening
        """
        # Edge-preserving filter
        filtered = cv2.edgePreservingFilter(img, flags=1, sigma_s=60, sigma_r=0.4)
        
        # Detail enhancement
        enhanced = cv2.detailEnhance(filtered, sigma_s=10, sigma_r=0.15)
        
        # Subtle sharpening
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]]) / 9
        sharpened = cv2.filter2D(enhanced, -1, kernel)
        
        # Blend sharpened with enhanced
        result = cv2.addWeighted(enhanced, 0.7, sharpened, 0.3, 0)
        
        return result
    
    def _apply_watercolor(self, img: np.ndarray) -> np.ndarray:
        """
        Watercolor painting effect:
        1. Apply bilateral filter for smoothing
        2. Apply median filter for color blending
        3. Reduce color palette
        4. Add subtle texture
        """
        # Multiple bilateral filter passes for smooth color regions
        result = img.copy()
        for _ in range(5):
            result = cv2.bilateralFilter(result, d=9, sigmaColor=100, sigmaSpace=100)
        
        # Median filter for additional smoothing
        result = cv2.medianBlur(result, 7)
        
        # Color quantization
        result = self._color_quantization(result, k=12)
        
        # Add subtle edge darkening for watercolor look
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 30, 100)
        edges = cv2.dilate(edges, None)
        edges = cv2.GaussianBlur(edges, (5, 5), 0)
        edges_inv = 255 - edges
        edges_colored = cv2.cvtColor(edges_inv, cv2.COLOR_GRAY2BGR)
        
        # Blend
        result = cv2.multiply(result, edges_colored, scale=1/255)
        
        # Brighten slightly
        result = cv2.convertScaleAbs(result, alpha=1.1, beta=10)
        
        return result
    
    def _color_quantization(self, img: np.ndarray, k: int = 8) -> np.ndarray:
        """
        Reduce number of colors using K-means clustering
        """
        # Reshape image to be a list of pixels
        data = img.reshape((-1, 3)).astype(np.float32)
        
        # Define criteria and apply K-means
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        _, labels, centers = cv2.kmeans(
            data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS
        )
        
        # Convert back to uint8 and reshape
        centers = np.uint8(centers)
        quantized = centers[labels.flatten()]
        quantized = quantized.reshape(img.shape)
        
        return quantized
    
    def _dodge_blend(self, base: np.ndarray, blend: np.ndarray) -> np.ndarray:
        """
        Color dodge blend mode for pencil sketch effect
        """
        # Avoid division by zero
        blend_inv = 255 - blend
        blend_inv[blend_inv == 0] = 1
        
        result = base.astype(np.float32) * 255 / blend_inv.astype(np.float32)
        result = np.clip(result, 0, 255).astype(np.uint8)
        
        return result
    
    def _create_comparison(self, original: np.ndarray, processed: np.ndarray) -> np.ndarray:
        """
        Create side-by-side comparison image
        """
        # Ensure same dimensions
        h1, w1 = original.shape[:2]
        h2, w2 = processed.shape[:2]
        
        # Resize processed to match original if needed
        if (h1, w1) != (h2, w2):
            processed = cv2.resize(processed, (w1, h1))
        
        # Add labels
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = max(0.5, min(h1, w1) / 1000)
        thickness = max(1, int(font_scale * 2))
        
        # Create copies with labels
        original_labeled = original.copy()
        processed_labeled = processed.copy()
        
        # Add white background for text
        cv2.rectangle(original_labeled, (10, 10), (150, 50), (255, 255, 255), -1)
        cv2.rectangle(processed_labeled, (10, 10), (150, 50), (255, 255, 255), -1)
        
        cv2.putText(original_labeled, "Original", (15, 40), font, font_scale, (0, 0, 0), thickness)
        cv2.putText(processed_labeled, "Toonified", (15, 40), font, font_scale, (0, 0, 0), thickness)
        
        # Create separator line
        separator = np.ones((h1, 5, 3), dtype=np.uint8) * 255
        
        # Concatenate horizontally
        comparison = np.hstack([original_labeled, separator, processed_labeled])
        
        return comparison


# Singleton instance
image_processor = ImageProcessor()
