from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from database import Base

class EventDB(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    camera_source = Column(String, index=True)
    detected_object = Column(String)
    threat_level = Column(String)  # e.g., 'low', 'medium', 'high', 'critical'
    confidence = Column(Float)
    location_x = Column(Integer, nullable=True) # Center x
    location_y = Column(Integer, nullable=True) # Center y
    image_path = Column(String, nullable=True) # Optional path to saved frame crop
