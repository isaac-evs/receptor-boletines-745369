from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
import os
import logging

from app.services.database_service import get_newsletter_by_id_and_email, get_s3_presigned_url
from app.exceptions import NewsletterNotFoundException, UnauthorizedAccessException, S3AccessException

router = APIRouter()

templates_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=templates_path)

logger = logging.getLogger(__name__)

@router.get("/newsletters/{newsletter_id}", response_class=HTMLResponse)
async def view_newsletter(
    request: Request,
    newsletter_id: str,
    email: str = Query(None, description="Email associated with the newsletter")
):
    try:
        if not email:
            logger.warning(f"Attempted to access newsletter {newsletter_id} without providing an email")
            raise HTTPException(status_code=400, detail="Email parameter is required")

        newsletter = get_newsletter_by_id_and_email(newsletter_id, email)

        if not newsletter:
            logger.warning(f"Newsletter not found: ID={newsletter_id}, email={email}")
            raise HTTPException(status_code=404, detail="Newsletter not found")

        image_url = newsletter.image_url

        if image_url.startswith("s3://"):
            parts = image_url.replace("s3://", "").split("/", 1)
            if len(parts) > 1:
                object_key = parts[1]
                presigned_url = get_s3_presigned_url(object_key)
                if presigned_url:
                    image_url = presigned_url
                else:
                    logger.error(f"Failed to generate presigned URL for {image_url}")
                    raise HTTPException(status_code=500, detail="Failed to access image resource")

        return templates.TemplateResponse(
            "newsletter.html",
            {
                "request": request,
                "newsletter_id": newsletter_id,
                "content": newsletter.content,
                "image_url": image_url,
                "email": email,
                "created_at": newsletter.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error displaying newsletter: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
