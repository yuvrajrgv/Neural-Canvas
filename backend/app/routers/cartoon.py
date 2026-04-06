"""
Cartoon Classification and Generation Routes
API endpoints for classifying cartoon faces and generating cartoons from photos
"""
from fastapi import APIRouter, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse, Response
from typing import Optional
import logging
import io
from PIL import Image

from app.schemas.image import (
    CartoonClassifyResponse,
    CartoonClassifyError,
    CartoonModelInfo,
    CartoonPrediction,
)
from app.ml.cartoon_classifier import get_classifier
from app.ml.cartoon_generator import get_cartoon_transfer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cartoon", tags=["Cartoon Classification"])


@router.get("/info", response_model=CartoonModelInfo)
async def get_model_info():
    """
    Get information about the cartoon classification model.
    
    Returns model status, number of classes, and list of recognizable identities.
    """
    try:
        classifier = get_classifier()
        
        return CartoonModelInfo(
            model_loaded=classifier.is_model_loaded(),
            num_classes=classifier.num_classes,
            identities=classifier.get_all_identities(),
            device=str(classifier.device)
        )
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/classify", response_model=CartoonClassifyResponse)
async def classify_cartoon(
    file: UploadFile = File(..., description="Cartoon image to classify"),
    top_k: Optional[int] = 5
):
    """
    Classify a cartoon face image.
    
    Upload a cartoon face image and get predictions for which celebrity
    the cartoon represents.
    
    - **file**: Cartoon face image (jpg, jpeg, png, webp)
    - **top_k**: Number of top predictions to return (default: 5)
    
    Returns top-k predictions with confidence scores.
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image (jpg, jpeg, png, webp)"
        )
    
    # Validate top_k
    if top_k is not None and (top_k < 1 or top_k > 100):
        top_k = 5
    
    try:
        classifier = get_classifier()
        
        # Check if model is loaded
        if not classifier.is_model_loaded():
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "success": False,
                    "error": "Model not loaded",
                    "message": "The classification model is not available. Please ensure the model file exists."
                }
            )
        
        # Read image bytes
        image_bytes = await file.read()
        
        # Get predictions
        predictions = classifier.predict_from_bytes(image_bytes, top_k=top_k)
        
        # Convert to response format
        prediction_models = [
            CartoonPrediction(**pred) for pred in predictions
        ]
        
        return CartoonClassifyResponse(
            success=True,
            predictions=prediction_models,
            message=f"Successfully classified cartoon. Top prediction: {predictions[0]['display_name']} ({predictions[0]['confidence']:.1f}%)"
        )
        
    except Exception as e:
        logger.error(f"Classification error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Classification failed: {str(e)}"
        )


@router.get("/identities")
async def get_identities():
    """
    Get list of all recognizable celebrity identities.
    
    Returns a list of all 100 celebrity names that the model can recognize.
    """
    try:
        classifier = get_classifier()
        identities = classifier.get_all_identities()
        
        return {
            "count": len(identities),
            "identities": identities
        }
    except Exception as e:
        logger.error(f"Error getting identities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/health")
async def classifier_health():
    """
    Health check for the cartoon classification service.
    """
    try:
        classifier = get_classifier()
        model_loaded = classifier.is_model_loaded()
        
        return {
            "status": "healthy" if model_loaded else "degraded",
            "model_loaded": model_loaded,
            "device": str(classifier.device),
            "num_classes": classifier.num_classes
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router.post("/generate")
async def generate_cartoon(
    file: UploadFile = File(..., description="Photo to convert to cartoon")
):
    """
    Generate a cartoon image from a photo using the trained DL model.
    
    Upload a photo and receive a cartoonified version generated by our
    GAN-based deep learning model trained on cartoon-face pairs.
    
    - **file**: Photo to cartoonify (jpg, jpeg, png, webp)
    
    Returns the cartoonified image as PNG.
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image (jpg, jpeg, png, webp)"
        )
    
    try:
        cartoon_transfer = get_cartoon_transfer()
        
        # Check if model is loaded
        if not cartoon_transfer.is_model_loaded():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Cartoon generator model not loaded. Please ensure the model file exists at backend/ml_weights/cartoon_generator.pt"
            )
        
        # Read image
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # Generate cartoon
        logger.info(f"Generating cartoon for image: {file.filename}")
        cartoon_image = cartoon_transfer.generate(image)
        
        # Convert to bytes
        output_buffer = io.BytesIO()
        cartoon_image.save(output_buffer, format="PNG", quality=95)
        output_buffer.seek(0)
        
        logger.info(f"Successfully generated cartoon for: {file.filename}")
        
        return Response(
            content=output_buffer.getvalue(),
            media_type="image/png",
            headers={
                "Content-Disposition": f"inline; filename=cartoon_{file.filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cartoon generation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cartoon generation failed: {str(e)}"
        )


@router.get("/generator/info")
async def get_generator_info():
    """
    Get information about the cartoon generator model.
    """
    try:
        cartoon_transfer = get_cartoon_transfer()
        
        return {
            "model_loaded": cartoon_transfer.is_model_loaded(),
            "model_path": cartoon_transfer.model_path,
            "device": str(cartoon_transfer.device),
            "architecture": "GAN-based Generator with 4 residual blocks"
        }
    except Exception as e:
        logger.error(f"Error getting generator info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
