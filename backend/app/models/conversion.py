"""
Conversion model representing closed deals/opportunities.
"""
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.orm import relationship

from .base import Base


class Conversion(Base):
    __tablename__ = "conversion"

    customer_id = Column(ForeignKey("customer.id"), nullable=False, index=True)
    value = Column(Numeric(15, 2), nullable=False, default=0.0)
    close_date = Column(DateTime(timezone=True), nullable=True, index=True)

    decision_makers_count = Column(Integer, nullable=False, default=1)
    influencers_count = Column(Integer, nullable=False, default=0)

    # Relationships
    customer = relationship("Customer", back_populates="conversions")
    touchpoints = relationship("Touchpoint", back_populates="conversion")
