"""
Image Job model for tracking image processing tasks
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base


class ImageStyle(str, enum.Enum):
    CARTOON = "cartoon"
    PENCIL_SKETCH = "pencil_sketch"
    COLOR_PENCIL = "color_pencil"
    EDGE_PRESERVE = "edge_preserve"
    WATERCOLOR = "watercolor"


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ImageJob(Base):
    __tablename__ = "image_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # File information
    original_filename = Column(String(255), nullable=False)
    original_path = Column(String(500), nullable=False)
    processed_path = Column(String(500), nullable=True)
    comparison_path = Column(String(500), nullable=True)
    
    # Processing details
    style = Column(String(50), default=ImageStyle.CARTOON.value)
    status = Column(String(50), default=JobStatus.PENDING.value)
    error_message = Column(Text, nullable=True)
    
    # Download tracking
    download_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="image_jobs")
    
    def __repr__(self):
        return f"<ImageJob(id={self.id}, user_id={self.user_id}, status={self.status})>"
