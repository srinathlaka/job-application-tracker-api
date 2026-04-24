from sqlalchemy import Column, Integer, String, Boolean

from app.database import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    company = Column(String, nullable=False)
    position = Column(String, nullable=False)
    status = Column(String, nullable=False)
    german_required = Column(Boolean, nullable=False)
    location = Column(String, nullable=True)
    notes = Column(String, nullable=True)