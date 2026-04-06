"""
Cartoon Face Classification Service
Uses trained ResNet18 model to classify cartoon faces into celebrity identities
"""
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import json
import os
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class CartoonClassifier:
    """
    Cartoon face classifier using pretrained ResNet18 model.
    Classifies cartoon images into 100 celebrity identities.
    """
    
    # ImageNet normalization values
    IMAGENET_MEAN = [0.485, 0.456, 0.406]
    IMAGENET_STD = [0.229, 0.224, 0.225]
    IMAGE_SIZE = 224
    
    def __init__(self, model_path: str = None, labels_path: str = None):
        """
        Initialize the classifier.
        
        Args:
            model_path: Path to trained model weights (.pt file)
            labels_path: Path to label mappings JSON file
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        # Default paths
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        models_dir = os.path.join(base_dir, "ml_weights")
        
        self.model_path = model_path or os.path.join(models_dir, "cartoon_resnet18.pt")
        self.labels_path = labels_path or os.path.join(models_dir, "cartoon_labels.json")
        
        # Load label mappings
        self.label_mappings = self._load_labels()
        self.num_classes = len(self.label_mappings.get("idx_to_identity", {}))
        
        # Load model
        self.model = self._load_model()
        
        # Define transforms
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(self.IMAGE_SIZE),
            transforms.ToTensor(),
            transforms.Normalize(mean=self.IMAGENET_MEAN, std=self.IMAGENET_STD)
        ])
        
        logger.info(f"CartoonClassifier initialized with {self.num_classes} classes")
    
    def _load_labels(self) -> Dict:
        """Load label mappings from JSON file."""
        if not os.path.exists(self.labels_path):
            logger.warning(f"Labels file not found: {self.labels_path}")
            return {"idx_to_identity": {}, "identity_to_idx": {}}
        
        try:
            with open(self.labels_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading labels: {e}")
            return {"idx_to_identity": {}, "identity_to_idx": {}}
    
    def _load_model(self) -> nn.Module:
        """Load the trained ResNet18 model."""
        # Create model architecture
        model = models.resnet18(weights=None)
        
        # Modify final layer for our number of classes
        if self.num_classes > 0:
            in_features = model.fc.in_features
            model.fc = nn.Linear(in_features, self.num_classes)
        
        # Load trained weights if available
        if os.path.exists(self.model_path):
            try:
                state_dict = torch.load(self.model_path, map_location=self.device)
                model.load_state_dict(state_dict)
                logger.info(f"Loaded model weights from: {self.model_path}")
            except Exception as e:
                logger.error(f"Error loading model weights: {e}")
        else:
            logger.warning(f"Model weights not found: {self.model_path}")
        
        model = model.to(self.device)
        model.eval()
        
        return model
    
    def preprocess_image(self, image: Image.Image) -> torch.Tensor:
        """
        Preprocess an image for model input.
        
        Args:
            image: PIL Image object
            
        Returns:
            Preprocessed tensor ready for model inference
        """
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Apply transforms
        tensor = self.transform(image)
        
        # Add batch dimension
        tensor = tensor.unsqueeze(0)
        
        return tensor.to(self.device)
    
    def predict(
        self, 
        image: Image.Image, 
        top_k: int = 5
    ) -> List[Dict]:
        """
        Predict the identity of a cartoon face.
        
        Args:
            image: PIL Image object
            top_k: Number of top predictions to return
            
        Returns:
            List of predictions with identity names and confidence scores
        """
        # Preprocess image
        input_tensor = self.preprocess_image(image)
        
        # Run inference
        with torch.no_grad():
            outputs = self.model(input_tensor)
            probabilities = torch.softmax(outputs, dim=1)
        
        # Get top-k predictions
        top_probs, top_indices = torch.topk(probabilities, min(top_k, self.num_classes))
        
        predictions = []
        idx_to_identity = self.label_mappings.get("idx_to_identity", {})
        
        for prob, idx in zip(top_probs[0], top_indices[0]):
            idx_str = str(idx.item())
            identity = idx_to_identity.get(idx_str, f"Unknown_{idx.item()}")
            
            # Format identity name (add spaces before capitals)
            formatted_name = self._format_identity_name(identity)
            
            predictions.append({
                "identity": identity,
                "display_name": formatted_name,
                "confidence": round(prob.item() * 100, 2),
                "class_index": idx.item()
            })
        
        return predictions
    
    def predict_from_path(
        self, 
        image_path: str, 
        top_k: int = 5
    ) -> List[Dict]:
        """
        Predict identity from an image file path.
        
        Args:
            image_path: Path to image file
            top_k: Number of top predictions to return
            
        Returns:
            List of predictions
        """
        image = Image.open(image_path)
        return self.predict(image, top_k)
    
    def predict_from_bytes(
        self, 
        image_bytes: bytes, 
        top_k: int = 5
    ) -> List[Dict]:
        """
        Predict identity from image bytes.
        
        Args:
            image_bytes: Image data as bytes
            top_k: Number of top predictions to return
            
        Returns:
            List of predictions
        """
        import io
        image = Image.open(io.BytesIO(image_bytes))
        return self.predict(image, top_k)
    
    def _format_identity_name(self, name: str) -> str:
        """
        Format identity name by adding spaces before capital letters.
        e.g., 'BarackObama' -> 'Barack Obama'
        """
        import re
        # Add space before each capital letter (except the first one)
        formatted = re.sub(r'(?<!^)(?=[A-Z])', ' ', name)
        return formatted
    
    def get_all_identities(self) -> List[str]:
        """Get list of all available identity names."""
        idx_to_identity = self.label_mappings.get("idx_to_identity", {})
        identities = list(idx_to_identity.values())
        return sorted([self._format_identity_name(i) for i in identities])
    
    def is_model_loaded(self) -> bool:
        """Check if model weights are loaded successfully."""
        return os.path.exists(self.model_path) and self.num_classes > 0


# Singleton instance for reuse across requests
_classifier_instance: Optional[CartoonClassifier] = None


def get_classifier() -> CartoonClassifier:
    """
    Get or create the singleton CartoonClassifier instance.
    This ensures the model is loaded only once and reused.
    """
    global _classifier_instance
    
    if _classifier_instance is None:
        _classifier_instance = CartoonClassifier()
    
    return _classifier_instance
