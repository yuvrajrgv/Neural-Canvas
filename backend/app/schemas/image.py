"""
Pydantic schemas for Image processing
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ImageStyleEnum(str, Enum):
    CARTOON = "cartoon"
    PENCIL_SKETCH = "pencil_sketch"
    COLOR_PENCIL = "color_pencil"
    EDGE_PRESERVE = "edge_preserve"
    WATERCOLOR = "watercolor"


class JobStatusEnum(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ImageProcessRequest(BaseModel):
    style: ImageStyleEnum = ImageStyleEnum.CARTOON


class ImageJobResponse(BaseModel):
    id: int
    original_filename: str
    style: str
    status: str
    created_at: datetime
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class ImageJobDetailResponse(ImageJobResponse):
    original_url: str
    processed_url: Optional[str] = None
    comparison_url: Optional[str] = None
    download_count: int = 0


class ImageUploadResponse(BaseModel):
    job_id: int
    message: str
    original_url: str


class ImageListResponse(BaseModel):
    jobs: List[ImageJobResponse]
    total: int
    page: int
    per_page: int


class StyleInfo(BaseModel):
    name: str
    value: str
    description: str


class StylesListResponse(BaseModel):
    styles: List[StyleInfo]


# Cartoon Classification Schemas
class CartoonPrediction(BaseModel):
    """Single prediction result for cartoon classification"""
    identity: str = Field(..., description="Raw identity name")
    display_name: str = Field(..., description="Formatted display name")
    confidence: float = Field(..., description="Confidence percentage (0-100)")
    class_index: int = Field(..., description="Class index in the model")


class CartoonClassifyResponse(BaseModel):
    """Response for cartoon classification endpoint"""
    success: bool = Field(default=True)
    predictions: List[CartoonPrediction]
    message: str = Field(default="Classification successful")


class CartoonClassifyError(BaseModel):
    """Error response for cartoon classification"""
    success: bool = Field(default=False)
    error: str
    message: str


class CartoonModelInfo(BaseModel):
    """Information about the cartoon classification model"""
    model_loaded: bool
    num_classes: int
    identities: List[str]
    device: str
