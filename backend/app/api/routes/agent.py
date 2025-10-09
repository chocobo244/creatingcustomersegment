"""
Agent endpoints for segmentation, insights, and basic support/sales handling.
"""
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.app.core.database import get_db_session, AsyncSession
from backend.app.services.agent_service import (
    CustomerSegmentationService,
    SupportSalesAgentService,
)

router = APIRouter(prefix="/agent", tags=["agent"])


class SegmentationRequest(BaseModel):
    k: int = Field(4, ge=2, le=20, description="Number of clusters")
    features: Optional[List[str]] = Field(
        None,
        description="Customer feature names to use; defaults to sensible numeric fields",
    )


@router.post("/segmentation/run", response_model=Dict)
async def run_segmentation(
    request: SegmentationRequest,
    db_session: AsyncSession = Depends(get_db_session),
):
    try:
        service = CustomerSegmentationService()
        result = await service.segment_customers(
            db_session=db_session,
            num_clusters=request.k,
            feature_names=request.features,
        )
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Segmentation failed: {e}")


@router.get("/insights", response_model=Dict)
async def get_insights(
    k: int = 4,
    db_session: AsyncSession = Depends(get_db_session),
):
    try:
        service = CustomerSegmentationService()
        result = await service.generate_segment_insights(db_session=db_session, num_clusters=k)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insights generation failed: {e}")


class SupportRequest(BaseModel):
    message: str
    customer_id: Optional[str] = None


@router.post("/support/ask", response_model=Dict)
async def support_ask(
    request: SupportRequest,
):
    agent = SupportSalesAgentService()
    reply = agent.handle_support_inquiry(message=request.message, customer_id=request.customer_id)
    return {"status": "success", "data": reply}


class SalesRequest(BaseModel):
    message: Optional[str] = None
    customer_id: Optional[str] = None


@router.post("/sales/assist", response_model=Dict)
async def sales_assist(
    request: SalesRequest,
    db_session: AsyncSession = Depends(get_db_session),
):
    agent = SupportSalesAgentService()
    reply = agent.handle_sales_inquiry(message=request.message or "", customer_id=request.customer_id)
    return {"status": "success", "data": reply}
