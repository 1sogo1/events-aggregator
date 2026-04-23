from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class Event(Base):
    __tablename__ = "events"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    event_time = Column(DateTime, nullable=False)
    registration_deadline = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)  # будет хранить значение из EventStatus
    number_of_visitors = Column(Integer, default=0)
    place_id = Column(String, nullable=False)
    place_name = Column(String)
    place_city = Column(String)
    place_address = Column(String)
    seats_pattern = Column(String)
    changed_at = Column(DateTime)
    created_at = Column(DateTime)
    status_changed_at = Column(DateTime)


class SyncMetadata(Base):
    __tablename__ = "sync_metadata"
    
    id = Column(String, primary_key=True, default="singleton")
    last_sync_at = Column(DateTime, nullable=True)
    last_changed_at = Column(DateTime, nullable=True)
    sync_status = Column(String, default="pending")
    error_message = Column(String, nullable=True)

class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_id = Column(String, nullable=False)
    event_id = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    seat = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)