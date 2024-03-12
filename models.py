from sqlalchemy import Boolean, Column, DateTime, Integer, String

import database

from datetime import datetime, timedelta


class RefreshToken(database.Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    user_email = Column(String, index=True)
    user_name = Column(String)
    user_img = Column(String)
    is_blacklisted = Column(Boolean, default=False)
    expires_at = Column(DateTime, default=datetime.utcnow() + timedelta(days=1))


