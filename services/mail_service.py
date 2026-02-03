# app/services/mail_service.py

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from core.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)


async def send_contact_email(
    name: str,
    email: str,
    message: str,
):
    msg = MessageSchema(
        subject="New Contact Message - Tech Polarity",
        recipients=[settings.MAIL_FROM],
        body=f"""
        Name: {name}
        Email: {email}

        Message:
        {message}
        """,
        subtype="plain",
    )

    fm = FastMail(conf)
    await fm.send_message(msg)
