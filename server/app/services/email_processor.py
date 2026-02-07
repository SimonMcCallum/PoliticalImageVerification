"""
Email processing service for image submissions.

Handles incoming email with image attachments, verifies sender identity
against registered party user accounts, and processes images with promoter
statement overlays. Designed to prevent spoofed submissions via a
verification-email-to-registered-address flow.
"""

import asyncio
import email
import hashlib
import logging
import secrets
from datetime import datetime, timezone, timedelta
from email.message import EmailMessage
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.services.encryption import decrypt_string, encrypt_data, generate_dek, encrypt_dek
from app.services.promoter_overlay import overlay_promoter_statement
from app.services.storage import store_blob, retrieve_blob

logger = logging.getLogger(__name__)

# Image MIME types we accept from email attachments
ACCEPTED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


def _hash_email(email_addr: str) -> str:
    """SHA-256 hash of an email address for audit logging."""
    return hashlib.sha256(email_addr.lower().strip().encode()).hexdigest()


def _generate_verification_token() -> tuple[str, str]:
    """Generate a verification token and its hash.

    Returns:
        (plain_token, token_hash) - send the plain token to the user,
        store the hash in the database.
    """
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    return token, token_hash


async def find_user_by_email(sender_email: str, db: AsyncSession):
    """Look up a PartyUser by matching their decrypted email.

    This is necessarily O(n) since emails are encrypted at rest.
    For production scale, consider a hash index column.
    """
    from app.models.party import PartyUser

    result = await db.execute(
        select(PartyUser).where(PartyUser.is_active == True)  # noqa: E712
    )
    users = result.scalars().all()

    sender_lower = sender_email.lower().strip()
    for user in users:
        try:
            decrypted_email = decrypt_string(user.email_encrypted)
            if decrypted_email.lower().strip() == sender_lower:
                return user
        except Exception:
            continue
    return None


async def send_verification_email(
    recipient_email: str,
    job_id: UUID,
    token: str,
) -> None:
    """Send a verification email to the registered address to confirm
    the sender actually submitted the image (anti-spoofing).
    """
    try:
        import aiosmtplib

        verification_url = (
            f"{settings.VERIFICATION_BASE_URL.rstrip('/')}"
            f"/../api/v1/email/verify/{job_id}?token={token}"
        )

        msg = EmailMessage()
        msg["From"] = settings.EMAIL_PROCESSING_ADDRESS
        msg["To"] = recipient_email
        msg["Subject"] = f"[{settings.PROJECT_NAME}] Confirm your image submission"
        msg.set_content(
            f"You (or someone using your email) submitted an image for processing.\n\n"
            f"If you sent this image, please confirm by visiting:\n"
            f"{verification_url}\n\n"
            f"This link expires in {settings.EMAIL_VERIFICATION_EXPIRE_MINUTES} minutes.\n\n"
            f"If you did not submit an image, please ignore this email.\n"
        )

        await aiosmtplib.send(
            msg,
            hostname=settings.EMAIL_SMTP_HOST,
            port=settings.EMAIL_SMTP_PORT,
            username=settings.EMAIL_SMTP_USER,
            password=settings.EMAIL_SMTP_PASSWORD,
            use_tls=True,
        )
        logger.info("Verification email sent for job %s", job_id)
    except Exception:
        logger.exception("Failed to send verification email for job %s", job_id)
        raise


async def process_verified_job(job_id: UUID, db: AsyncSession) -> None:
    """Process a job that has been verified: retrieve image, add promoter
    statement, store result, and email the result back.
    """
    from app.models.email_job import EmailProcessingJob, EmailJobStatus
    from app.models.party import Party, PartyUser

    result = await db.execute(
        select(EmailProcessingJob).where(EmailProcessingJob.id == job_id)
    )
    job = result.scalar_one_or_none()
    if not job or job.status != EmailJobStatus.VERIFIED:
        return

    job.status = EmailJobStatus.PROCESSING
    await db.commit()

    try:
        # Get user and party
        user_result = await db.execute(
            select(PartyUser).where(PartyUser.id == job.party_user_id)
        )
        user = user_result.scalar_one()

        party_result = await db.execute(
            select(Party).where(Party.id == user.party_id)
        )
        party = party_result.scalar_one()

        if not party.promoter_statement:
            job.status = EmailJobStatus.FAILED
            job.error_message = "No promoter statement set for party"
            job.completed_at = datetime.now(timezone.utc)
            await db.commit()
            return

        # Retrieve the stored image
        image_bytes = await retrieve_blob(job.image_storage_key)

        # Apply promoter statement
        if job.add_promoter:
            processed_bytes = overlay_promoter_statement(
                image_bytes,
                party.promoter_statement,
                position=job.position,
            )
        else:
            processed_bytes = image_bytes

        # Store result
        result_key = await store_blob(processed_bytes, prefix="email_results")
        job.result_storage_key = result_key
        job.status = EmailJobStatus.COMPLETED
        job.completed_at = datetime.now(timezone.utc)
        await db.commit()

        # Email result back to user
        try:
            import aiosmtplib
            from email.message import EmailMessage

            recipient = decrypt_string(user.email_encrypted)
            msg = EmailMessage()
            msg["From"] = settings.EMAIL_PROCESSING_ADDRESS
            msg["To"] = recipient
            msg["Subject"] = f"[{settings.PROJECT_NAME}] Your processed image"
            msg.set_content(
                "Your image has been processed with the promoter statement.\n"
                "The processed image is attached.\n"
            )
            msg.add_attachment(
                processed_bytes,
                maintype="image",
                subtype="png",
                filename="promoter_stamped.png",
            )
            await aiosmtplib.send(
                msg,
                hostname=settings.EMAIL_SMTP_HOST,
                port=settings.EMAIL_SMTP_PORT,
                username=settings.EMAIL_SMTP_USER,
                password=settings.EMAIL_SMTP_PASSWORD,
                use_tls=True,
            )
            logger.info("Result emailed back for job %s", job_id)
        except Exception:
            logger.exception("Failed to email result for job %s", job_id)

    except Exception as e:
        job.status = EmailJobStatus.FAILED
        job.error_message = str(e)[:500]
        job.completed_at = datetime.now(timezone.utc)
        await db.commit()
        logger.exception("Failed to process email job %s", job_id)


async def handle_incoming_email(raw_email: bytes, db: AsyncSession) -> None:
    """Process a single incoming email message.

    1. Parse the email and extract sender + image attachment
    2. Look up sender in registered party users
    3. Create a pending job
    4. Send verification email to the registered address
    """
    from app.models.email_job import EmailProcessingJob, EmailJobStatus

    msg = email.message_from_bytes(raw_email, policy=email.policy.default)
    sender = msg.get("From", "")

    # Extract email address from "Name <email>" format
    if "<" in sender and ">" in sender:
        sender_email = sender.split("<")[1].split(">")[0]
    else:
        sender_email = sender.strip()

    if not sender_email:
        logger.warning("Incoming email with no sender address, skipping")
        return

    # Find matching party user
    user = await find_user_by_email(sender_email, db)
    if not user:
        logger.warning("No registered user found for sender %s", _hash_email(sender_email))
        return

    if not user.email_verified_for_processing:
        logger.warning("User %s has not enabled email processing", user.id)
        return

    # Extract image attachment
    image_bytes = None
    image_type = None
    for part in msg.walk():
        content_type = part.get_content_type()
        if content_type in ACCEPTED_IMAGE_TYPES:
            image_bytes = part.get_payload(decode=True)
            image_type = content_type
            break

    if not image_bytes:
        logger.warning("No image attachment found in email from %s", _hash_email(sender_email))
        return

    # Store the incoming image
    storage_key = await store_blob(image_bytes, prefix="email_incoming")

    # Generate verification token
    token, token_hash = _generate_verification_token()

    # Create job
    job = EmailProcessingJob(
        party_user_id=user.id,
        sender_email_hash=_hash_email(sender_email),
        image_storage_key=storage_key,
        add_promoter=True,
        position=user.default_statement_position,
        verification_token_hash=token_hash,
        verification_expires=datetime.now(timezone.utc)
        + timedelta(minutes=settings.EMAIL_VERIFICATION_EXPIRE_MINUTES),
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Send verification email to the registered address (not the apparent sender)
    registered_email = decrypt_string(user.email_encrypted)
    await send_verification_email(registered_email, job.id, token)

    logger.info("Email job %s created, verification email sent", job.id)


async def email_polling_loop() -> None:
    """Background task that polls the IMAP inbox for new messages."""
    logger.info("Email polling loop started")

    while True:
        try:
            import aioimaplib

            imap = aioimaplib.IMAP4_SSL(
                host=settings.EMAIL_IMAP_HOST,
                port=settings.EMAIL_IMAP_PORT,
            )
            await imap.wait_hello_from_server()
            await imap.login(settings.EMAIL_IMAP_USER, settings.EMAIL_IMAP_PASSWORD)
            await imap.select("INBOX")

            # Search for unseen messages
            _, data = await imap.search("UNSEEN")
            if data and data[0]:
                message_ids = data[0].split()
                for msg_id in message_ids:
                    _, msg_data = await imap.fetch(msg_id, "(RFC822)")
                    if msg_data and len(msg_data) > 1:
                        raw_email = msg_data[1]
                        if isinstance(raw_email, tuple) and len(raw_email) > 1:
                            # Process with a fresh DB session
                            from app.core.database import async_session_factory
                            async with async_session_factory() as db:
                                await handle_incoming_email(raw_email[1], db)

                        # Mark as seen
                        await imap.store(msg_id, "+FLAGS", "\\Seen")

            await imap.logout()
        except asyncio.CancelledError:
            logger.info("Email polling loop cancelled")
            break
        except Exception:
            logger.exception("Error in email polling loop")

        await asyncio.sleep(settings.EMAIL_POLL_INTERVAL_SECONDS)
