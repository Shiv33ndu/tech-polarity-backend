# app/services/mail_service.py

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import settings
import httpx


class MailService:

    @staticmethod
    async def send_contact_email(
        name: str,
        email: str,
        message: str,
    ):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": "Tech Polarity <onboarding@resend.dev>",
                    "to": [settings.CONTACT_TO_EMAIL],
                    "subject": "New Contact Message",
                    "html": f"""
                        <p><strong>Name:</strong> {name}</p>
                        <p><strong>Email:</strong> {email}</p>
                        <p>{message}</p>
                    """,
                },
                timeout=10,
            )

            response.raise_for_status()
