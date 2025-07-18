"""
Touchpoint model representing customer interactions with marketing channels.
"""
from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import Column, String, DateTime, Numeric, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base import Base


class Touchpoint(Base):
    """Model representing a customer touchpoint/interaction."""
    
    __tablename__ = "touchpoints"
    
    # Customer information
    customer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("customer.id"),
        nullable=False,
        index=True
    )
    
    # Campaign and channel information
    campaign_id = Column(
        UUID(as_uuid=True),
        ForeignKey("campaign.id"),
        nullable=True,
        index=True
    )
    
    channel_id = Column(
        UUID(as_uuid=True),
        ForeignKey("channel.id"),
        nullable=False,
        index=True
    )
    
    # Touchpoint details
    touchpoint_timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    
    touchpoint_type = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Type of touchpoint: impression, click, visit, etc."
    )
    
    # Attribution data
    position_in_journey = Column(
        String(20),
        nullable=True,
        index=True,
        comment="Position: first, middle, last, only"
    )
    
    time_to_conversion = Column(
        Numeric(10, 2),
        nullable=True,
        comment="Hours between this touchpoint and conversion"
    )
    
    # Cost and value data
    cost = Column(
        Numeric(10, 4),
        nullable=True,
        default=0.0,
        comment="Cost of this touchpoint"
    )
    
    # Metadata and additional attributes
    referrer_url = Column(Text, nullable=True)
    landing_page_url = Column(Text, nullable=True)
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    
    # Device and context information
    device_type = Column(
        String(20),
        nullable=True,
        comment="desktop, mobile, tablet"
    )
    
    browser = Column(String(50), nullable=True)
    operating_system = Column(String(50), nullable=True)
    
    # Geographic information
    country = Column(String(2), nullable=True)
    region = Column(String(50), nullable=True)
    city = Column(String(100), nullable=True)
    
    # Custom attributes stored as JSON
    custom_attributes = Column(
        JSONB,
        nullable=True,
        comment="Additional custom attributes as JSON"
    )
    
    # External system references
    external_id = Column(
        String(100),
        nullable=True,
        index=True,
        comment="ID from external system"
    )
    
    source_system = Column(
        String(50),
        nullable=True,
        comment="Source system that provided this data"
    )
    
    # Relationships
    customer = relationship("Customer", back_populates="touchpoints")
    campaign = relationship("Campaign", back_populates="touchpoints")
    channel = relationship("Channel", back_populates="touchpoints")
    
    # Indexes for common query patterns
    __table_args__ = (
        Index(
            "ix_touchpoints_customer_timestamp",
            "customer_id",
            "touchpoint_timestamp"
        ),
        Index(
            "ix_touchpoints_channel_timestamp",
            "channel_id", 
            "touchpoint_timestamp"
        ),
        Index(
            "ix_touchpoints_campaign_timestamp",
            "campaign_id",
            "touchpoint_timestamp"
        ),
        Index(
            "ix_touchpoints_type_timestamp",
            "touchpoint_type",
            "touchpoint_timestamp"
        ),
    )
    
    def __repr__(self) -> str:
        return (
            f"<Touchpoint("
            f"customer_id={self.customer_id}, "
            f"channel_id={self.channel_id}, "
            f"type={self.touchpoint_type}, "
            f"timestamp={self.touchpoint_timestamp}"
            f")>"
        )
    
    @property
    def is_first_touch(self) -> bool:
        """Check if this is a first touch touchpoint."""
        return self.position_in_journey == "first"
    
    @property
    def is_last_touch(self) -> bool:
        """Check if this is a last touch touchpoint."""
        return self.position_in_journey == "last"
    
    @property
    def is_middle_touch(self) -> bool:
        """Check if this is a middle touch touchpoint."""
        return self.position_in_journey == "middle"
    
    @property
    def is_only_touch(self) -> bool:
        """Check if this is the only touchpoint in the journey."""
        return self.position_in_journey == "only"