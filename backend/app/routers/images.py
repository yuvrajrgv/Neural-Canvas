"""
Image processing routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas.image import (
    ImageStyleEnum,
    ImageProcessRequest,
    ImageJobResponse,
    ImageJobDetailResponse,
    ImageUploadResponse,
    ImageListResponse,
    StyleInfo,
    StylesListResponse,
)
from app.services.image_service import image_service
from app.image_processing.processor import ImageProcessor
from app.core.security import get_current_user
from app.models.user import User
from app.models.image_job import JobStatus
import os

router = APIRouter(prefix="/images", tags=["Images"])

# Style descriptions
STYLE_DESCRIPTIONS = {
    ImageStyleEnum.CARTOON: "Classic cartoon effect with bold edges and flat colors",
    ImageStyleEnum.PENCIL_SKETCH: "Grayscale pencil sketch drawing effect",
    ImageStyleEnum.COLOR_PENCIL: "Colored pencil artistic stylization",
    ImageStyleEnum.EDGE_PRESERVE: "Edge-preserving smooth effect with enhanced details",
    ImageStyleEnum.WATERCOLOR: "Soft watercolor painting effect",
}


@router.get("/styles", response_model=StylesListResponse)
async def get_available_styles():
    """
    Get list of available image transformation styles
    """
    styles = [
        StyleInfo(
            name=style.value.replace("_", " ").title(),
            value=style.value,
            description=STYLE_DESCRIPTIONS.get(style, "")
        )
        for style in ImageStyleEnum
    ]
    return StylesListResponse(styles=styles)


@router.post("/upload", response_model=ImageUploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    style: ImageStyleEnum = ImageStyleEnum.CARTOON,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload an image for processing
    
    - **file**: Image file (jpg, jpeg, png, webp)
    - **style**: Transformation style to apply
    """
    # Validate file
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Save file
    filename, file_path = image_service.save_uploaded_file(file, current_user.id)
    
    # Create job
    job = image_service.create_image_job(
        db=db,
        user_id=current_user.id,
        original_filename=file.filename,
        original_path=file_path,
        style=style
    )
    
    return ImageUploadResponse(
        job_id=job.id,
        message="Image uploaded successfully",
        original_url=f"/images/file/{job.id}/original"
    )


@router.post("/{job_id}/process", response_model=ImageJobResponse)
async def process_image(
    job_id: int,
    background_tasks: BackgroundTasks,
    style: Optional[ImageStyleEnum] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start processing an uploaded image
    
    - **job_id**: ID of the upload job
    - **style**: Optional new style (overrides upload style)
    """
    job = image_service.get_job_by_id(db, job_id, current_user.id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image job not found"
        )
    
    if job.status == JobStatus.PROCESSING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image is already being processed"
        )
    
    # Update style if provided
    if style:
        job.style = style.value
        db.commit()
    
    # Process in background using the DATABASE_URL from settings
    from app.core.config import settings
    background_tasks.add_task(
        process_image_task,
        db_url=settings.DATABASE_URL,
        job_id=job.id
    )
    
    # Update status to processing
    image_service.update_job_status(db, job, JobStatus.PROCESSING)
    
    return ImageJobResponse.model_validate(job)


def process_image_task(db_url: str, job_id: int):
    """Background task for image processing"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.models.image_job import ImageJob
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Create new engine and session for background task
        engine = create_engine(db_url, pool_pre_ping=True)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        job = db.query(ImageJob).filter(ImageJob.id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found")
            db.close()
            return
        
        logger.info(f"Starting processing for job {job_id} with style {job.style}")
        
        processor = ImageProcessor()
        
        # Process image
        processed_path, comparison_path = processor.process_image(
            input_path=job.original_path,
            style=job.style
        )
        
        logger.info(f"Processing completed for job {job_id}")
        
        # Update job with results
        job.processed_path = processed_path
        job.comparison_path = comparison_path
        job.status = JobStatus.COMPLETED.value
        from datetime import datetime
        job.processed_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Job {job_id} marked as completed")
        
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {str(e)}", exc_info=True)
        try:
            if job:
                job.status = JobStatus.FAILED.value
                job.error_message = str(e)
                db.commit()
        except:
            pass
    finally:
        try:
            db.close()
        except:
            pass


@router.get("/{job_id}", response_model=ImageJobDetailResponse)
async def get_image_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get details of an image processing job
    """
    job = image_service.get_job_by_id(db, job_id, current_user.id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image job not found"
        )
    
    return ImageJobDetailResponse(
        id=job.id,
        original_filename=job.original_filename,
        style=job.style,
        status=job.status,
        created_at=job.created_at,
        processed_at=job.processed_at,
        error_message=job.error_message,
        original_url=f"/images/file/{job.id}/original",
        processed_url=f"/images/file/{job.id}/processed" if job.processed_path else None,
        comparison_url=f"/images/file/{job.id}/comparison" if job.comparison_path else None,
        download_count=job.download_count
    )


@router.get("/", response_model=ImageListResponse)
async def list_image_jobs(
    page: int = 1,
    per_page: int = 10,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all image jobs for current user
    
    - **page**: Page number (default 1)
    - **per_page**: Items per page (default 10)
    - **status**: Filter by status (pending, processing, completed, failed)
    """
    jobs, total = image_service.get_user_jobs(
        db=db,
        user_id=current_user.id,
        page=page,
        per_page=per_page,
        status_filter=status
    )
    
    return ImageListResponse(
        jobs=[ImageJobResponse.model_validate(job) for job in jobs],
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/file/{job_id}/{file_type}")
async def get_image_file(
    job_id: int,
    file_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get image file (original, processed, or comparison)
    
    - **file_type**: original, processed, or comparison
    """
    job = image_service.get_job_by_id(db, job_id, current_user.id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image job not found"
        )
    
    if file_type == "original":
        file_path = job.original_path
    elif file_type == "processed":
        file_path = job.processed_path
    elif file_type == "comparison":
        file_path = job.comparison_path
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type"
        )
    
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return FileResponse(file_path)


@router.get("/download/{job_id}")
async def download_processed_image(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Download processed image
    """
    job = image_service.get_job_by_id(db, job_id, current_user.id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image job not found"
        )
    
    if job.status != JobStatus.COMPLETED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image processing not completed"
        )
    
    if not job.processed_path or not os.path.exists(job.processed_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Processed image not found"
        )
    
    # Increment download count
    image_service.increment_download_count(db, job)
    
    # Generate download filename
    original_name = os.path.splitext(job.original_filename)[0]
    ext = os.path.splitext(job.processed_path)[1]
    download_filename = f"{original_name}_toonified{ext}"
    
    return FileResponse(
        job.processed_path,
        filename=download_filename,
        media_type="image/png"
    )


@router.delete("/{job_id}", response_model=dict)
async def delete_image_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an image job and associated files
    """
    job = image_service.get_job_by_id(db, job_id, current_user.id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image job not found"
        )
    
    image_service.delete_job(db, job)
    
    return {"message": "Image job deleted successfully"}
