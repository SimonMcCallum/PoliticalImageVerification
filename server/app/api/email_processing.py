"""Email processing endpoints for verifying and tracking email-submitted jobs."""

import hashlib
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.email_job import EmailProcessingJob, EmailJobStatus
from app.models.party import PartyUser
from app.schemas.email_processing import EmailJobResponse

router = APIRouter(prefix="/email", tags=["email"])


@router.post("/verify/{job_id}")
async def verify_email_job(
    job_id: uuid.UUID,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Confirm an email processing job using the one-time verification token.

    This endpoint is called when the user clicks the verification link
    sent to their registered email address.
    """
    result = await db.execute(
        select(EmailProcessingJob).where(EmailProcessingJob.id == job_id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != EmailJobStatus.PENDING_VERIFICATION:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job has already been verified or processed",
        )

    # Check expiry
    if job.verification_expires and job.verification_expires < datetime.now(timezone.utc):
        job.status = EmailJobStatus.FAILED
        job.error_message = "Verification link expired"
        job.completed_at = datetime.now(timezone.utc)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification link has expired",
        )

    # Verify token
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    if token_hash != job.verification_token_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token",
        )

    # Mark as verified and trigger processing
    job.status = EmailJobStatus.VERIFIED
    job.verification_token_hash = None  # Invalidate the token
    await db.commit()

    # Process the job asynchronously
    import asyncio
    from app.services.email_processor import process_verified_job
    asyncio.create_task(process_verified_job(job_id, db))

    return {"detail": "Email submission verified. Your image is being processed."}


@router.get("/jobs", response_model=list[EmailJobResponse])
async def list_email_jobs(
    user: PartyUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List email processing jobs for the current user."""
    result = await db.execute(
        select(EmailProcessingJob)
        .where(EmailProcessingJob.party_user_id == user.id)
        .order_by(EmailProcessingJob.created_at.desc())
        .limit(20)
    )
    jobs = result.scalars().all()
    return jobs


@router.get("/jobs/{job_id}", response_model=EmailJobResponse)
async def get_email_job(
    job_id: uuid.UUID,
    user: PartyUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get status of a specific email processing job."""
    result = await db.execute(
        select(EmailProcessingJob).where(
            EmailProcessingJob.id == job_id,
            EmailProcessingJob.party_user_id == user.id,
        )
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
