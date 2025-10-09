"""
Campaign model referenced by touchpoints.
"""
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from .base import Base


class Campaign(Base):
    __tablename__ = "campaign"

    name = Column(String(255), nullable=False, index=True)

    touchpoints = relationship("Touchpoint", back_populates="campaign")
