"""
Customer model representing customers in the attribution system.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, DateTime, Numeric, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base import Base


class Customer(Base):
    """Model representing a customer in the attribution system."""
    
    __tablename__ = "customer"
    
    # Basic customer information
    external_customer_id = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        comment="Customer ID from external system (CRM, etc.)"
    )
    
    email = Column(
        String(255),
        nullable=True,
        unique=True,
        index=True
    )
    
    # Customer demographics
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    
    # Customer journey timestamps
    first_touchpoint_at = Column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Timestamp of first touchpoint"
    )
    
    last_touchpoint_at = Column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Timestamp of last touchpoint"
    )
    
    first_conversion_at = Column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Timestamp of first conversion"
    )
    
    last_conversion_at = Column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Timestamp of last conversion"
    )
    
    # Customer value metrics
    total_conversions = Column(
        Numeric(10, 0),
        nullable=False,
        default=0,
        comment="Total number of conversions"
    )
    
    total_conversion_value = Column(
        Numeric(15, 2),
        nullable=False,
        default=0.0,
        comment="Total value of all conversions"
    )
    
    total_touchpoints = Column(
        Numeric(10, 0),
        nullable=False,
        default=0,
        comment="Total number of touchpoints"
    )
    
    # Customer lifecycle metrics
    customer_lifetime_days = Column(
        Numeric(10, 2),
        nullable=True,
        comment="Days between first touchpoint and last activity"
    )
    
    average_time_to_conversion = Column(
        Numeric(10, 2),
        nullable=True,
        comment="Average hours between first touchpoint and conversion"
    )
    
    # Customer segmentation
    customer_segment = Column(
        String(50),
        nullable=True,
        index=True,
        comment="Customer segment for analysis"
    )
    
    customer_tier = Column(
        String(20),
        nullable=True,
        index=True,
        comment="Customer tier: bronze, silver, gold, platinum"
    )
    
    # Status flags
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Whether customer is currently active"
    )
    
    is_converted = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
        comment="Whether customer has converted at least once"
    )
    
    # Geographic information
    country = Column(String(2), nullable=True, index=True)
    region = Column(String(50), nullable=True)
    city = Column(String(100), nullable=True)
    timezone = Column(String(50), nullable=True)
    
    # Acquisition information
    acquisition_channel = Column(
        String(50),
        nullable=True,
        index=True,
        comment="Channel that acquired this customer"
    )
    
    acquisition_campaign = Column(
        String(100),
        nullable=True,
        comment="Campaign that acquired this customer"
    )
    
    acquisition_source = Column(
        String(100),
        nullable=True,
        comment="Traffic source that acquired this customer"
    )
    
    # Custom attributes
    custom_attributes = Column(
        JSONB,
        nullable=True,
        comment="Additional custom customer attributes as JSON"
    )
    
    # Data quality and enrichment
    data_quality_score = Column(
        Numeric(3, 2),
        nullable=True,
        comment="Data quality score from 0.0 to 1.0"
    )
    
    last_enriched_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last time customer data was enriched"
    )
    
    # External system references
    source_system = Column(
        String(50),
        nullable=True,
        comment="Source system that provided this customer"
    )
    
    external_sync_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last time data was synced from external system"
    )
    
    # Relationships
    touchpoints = relationship(
        "Touchpoint",
        back_populates="customer",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    conversions = relationship(
        "Conversion",
        back_populates="customer",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    attribution_results = relationship(
        "AttributionResult",
        back_populates="customer",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    def __repr__(self) -> str:
        return (
            f"<Customer("
            f"id={self.id}, "
            f"external_id={self.external_customer_id}, "
            f"email={self.email}, "
            f"conversions={self.total_conversions}"
            f")>"
        )
    
    @property
    def full_name(self) -> Optional[str]:
        """Get customer's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return None
    
    @property
    def journey_length_days(self) -> Optional[float]:
        """Calculate customer journey length in days."""
        if self.first_touchpoint_at and self.last_touchpoint_at:
            delta = self.last_touchpoint_at - self.first_touchpoint_at
            return delta.total_seconds() / (24 * 3600)
        return None
    
    @property
    def conversion_rate(self) -> float:
        """Calculate customer conversion rate."""
        if self.total_touchpoints > 0:
            return float(self.total_conversions) / float(self.total_touchpoints)
        return 0.0
    
    @property
    def average_conversion_value(self) -> float:
        """Calculate average conversion value."""
        if self.total_conversions > 0:
            return float(self.total_conversion_value) / float(self.total_conversions)
        return 0.0