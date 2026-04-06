"""
Image job management service
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
from typing import Optional, List
import os
import uuid
from datetime import datetime

from app.models.image_job import ImageJob, JobStatus
from app.models.user import User
from app.schemas.image import ImageStyleEnum
from app.core.config import settings


class ImageService:
    
    @staticmethod
    def save_uploaded_file(file: UploadFile, user_id: int) -> tuple[str, str]:
        """
        Save uploaded file to storage
        Returns (filename, file_path)
        """
        # Generate unique filename
        ext = file.filename.split('.')[-1].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}"
            )
        
        unique_filename = f"{user_id}_{uuid.uuid4().hex}.{ext}"
        file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = file.file.read()
            if len(content) > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE // (1024*1024)}MB"
                )
            buffer.write(content)
        
        return unique_filename, file_path
    
    @staticmethod
    def create_image_job(
        db: Session,
        user_id: int,
        original_filename: str,
        original_path: str,
        style: ImageStyleEnum
    ) -> ImageJob:
        """Create a new image processing job"""
        job = ImageJob(
            user_id=user_id,
            original_filename=original_filename,
            original_path=original_path,
            style=style.value,
            status=JobStatus.PENDING.value,
        )
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        return job
    
    @staticmethod
    def get_job_by_id(db: Session, job_id: int, user_id: int = None) -> Optional[ImageJob]:
        """Get image job by ID, optionally filtered by user"""
        query = db.query(ImageJob).filter(ImageJob.id == job_id)
        if user_id:
            query = query.filter(ImageJob.user_id == user_id)
        return query.first()
    
    @staticmethod
    def get_user_jobs(
        db: Session,
        user_id: int,
        page: int = 1,
        per_page: int = 10,
        status_filter: str = None
    ) -> tuple[List[ImageJob], int]:
        """Get paginated list of user's image jobs"""
        query = db.query(ImageJob).filter(ImageJob.user_id == user_id)
        
        if status_filter:
            query = query.filter(ImageJob.status == status_filter)
        
        total = query.count()
        jobs = query.order_by(ImageJob.created_at.desc())\
                   .offset((page - 1) * per_page)\
                   .limit(per_page)\
                   .all()
        
        return jobs, total
    
    @staticmethod
    def update_job_status(
        db: Session,
        job: ImageJob,
        status: JobStatus,
        processed_path: str = None,
        comparison_path: str = None,
        error_message: str = None
    ) -> ImageJob:
        """Update job status and paths"""
        job.status = status.value
        
        if processed_path:
            job.processed_path = processed_path
        if comparison_path:
            job.comparison_path = comparison_path
        if error_message:
            job.error_message = error_message
        if status == JobStatus.COMPLETED:
            job.processed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(job)
        
        return job
    
    @staticmethod
    def increment_download_count(db: Session, job: ImageJob) -> ImageJob:
        """Increment download count"""
        job.download_count += 1
        db.commit()
        db.refresh(job)
        return job
    
    @staticmethod
    def delete_job(db: Session, job: ImageJob) -> bool:
        """Delete job and associated files"""
        # Delete files
        if job.original_path and os.path.exists(job.original_path):
            os.remove(job.original_path)
        if job.processed_path and os.path.exists(job.processed_path):
            os.remove(job.processed_path)
        if job.comparison_path and os.path.exists(job.comparison_path):
            os.remove(job.comparison_path)
        
        db.delete(job)
        db.commit()
        
        return True
    
    @staticmethod
    def get_file_url(file_path: str, base_url: str = "/files") -> str:
        """Generate URL for file access"""
        if not file_path:
            return None
        filename = os.path.basename(file_path)
        return f"{base_url}/{filename}"


image_service = ImageService()
