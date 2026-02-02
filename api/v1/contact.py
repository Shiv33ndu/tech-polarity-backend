# app/api/v1/contact.py

from fastapi import APIRouter, BackgroundTasks, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from schemas.contact import ContactCreate, ContactResponse
from db.mongo import database
from services.mail_service import send_contact_email

router = APIRouter(prefix="/contact", tags=["Contact"])

limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("5/minute")  # Anti-spam
async def submit_contact_form(
    request: Request,
    payload: ContactCreate,
    background_tasks: BackgroundTasks,
):
    # Store message
    await database.contacts.insert_one(
        {
            "name": payload.name,
            "email": payload.email,
            "message": payload.message,
            "ip_address": get_remote_address(request),
        }
    )

    # Send email asynchronously
    background_tasks.add_task(
        send_contact_email,
        payload.name,
        payload.email,
        payload.message,
    )

    return {"message": "Your message has been sent successfully"}
