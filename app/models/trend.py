from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.core.database import Base

class Trend(Base):
    __tablename__ = "trends"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, index=True)
    keyword = Column(String, index=True)
    content = Column(Text)
    sentiment = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
