from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional


class ContactMessage:
    def __init__(
        self,
        name: str,
        email: str,
        message: str,
        ip_address: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ):
        self.name = name
        self.email = email
        self.message = message
        self.ip_address = ip_address
        self.created_at = created_at or datetime.now(ZoneInfo("Asia/Kolkata"))
