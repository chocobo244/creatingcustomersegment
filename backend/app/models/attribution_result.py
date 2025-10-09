"""
AttributionResult model to store computed attribution payloads.
"""
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from .base import Base


class AttributionResult(Base):
    __tablename__ = "attribution_result"

    model_name = Column(String(100), nullable=False, index=True)
    results = Column(JSONB, nullable=False)
    extra_metadata = Column(JSONB, nullable=True)

    # Optional linkage to a customer/account
    customer_id = Column(ForeignKey("customer.id"), nullable=True, index=True)
    customer = relationship("Customer", back_populates="attribution_results")
