from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime

from app.core.database import Base


class TrendReport(Base):
    __tablename__ = "trend_reports"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String, index=True)
    mode = Column(String, default="on_demand")
    report = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
