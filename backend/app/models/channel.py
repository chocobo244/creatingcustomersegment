"""
Channel model referenced by touchpoints.
"""
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from .base import Base


class Channel(Base):
    __tablename__ = "channel"

    name = Column(String(100), nullable=False, unique=True, index=True)

    touchpoints = relationship("Touchpoint", back_populates="channel")
