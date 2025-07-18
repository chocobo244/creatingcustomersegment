"""
Attribution API routes for B2B marketing attribution.
"""
from datetime import datetime, date
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from backend.app.core.database import get_db_session, AsyncSession
from backend.app.services.attribution_service import B2BAttributionService
from backend.app.utils.logging import LoggerMixin


router = APIRouter(prefix="/attribution", tags=["attribution"])


class AttributionRequest(BaseModel):
    """Request model for B2B attribution calculation."""
    account_ids: Optional[List[str]] = Field(None, description="List of account IDs to analyze")
    date_from: Optional[date] = Field(None, description="Start date for analysis")
    date_to: Optional[date] = Field(None, description="End date for analysis")
    attribution_weights: Optional[Dict[str, float]] = Field(
        None, 
        description="Custom weights for attribution factors (time, quality, account, stage, velocity)"
    )


class ChannelInsightsRequest(BaseModel):
    """Request model for channel performance insights."""
    account_ids: Optional[List[str]] = Field(None, description="List of account IDs to analyze")
    date_from: Optional[date] = Field(None, description="Start date for analysis")
    date_to: Optional[date] = Field(None, description="End date for analysis")


class AlignmentReportRequest(BaseModel):
    """Request model for sales-marketing alignment report."""
    account_ids: Optional[List[str]] = Field(None, description="List of account IDs to analyze")
    date_from: Optional[date] = Field(None, description="Start date for analysis")
    date_to: Optional[date] = Field(None, description="End date for analysis")


class AttributionAPI(LoggerMixin):
    """API endpoints for B2B attribution analysis."""
    
    def __init__(self):
        self.attribution_service = B2BAttributionService()


attribution_api = AttributionAPI()


@router.post("/b2b/calculate", response_model=Dict)
async def calculate_b2b_attribution(
    request: AttributionRequest,
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Calculate comprehensive B2B marketing attribution.
    
    This endpoint provides sophisticated B2B attribution analysis including:
    - Time-decay attribution accounting for long B2B sales cycles
    - Lead quality impact analysis
    - Account-based attribution for enterprise deals
    - Stage progression analysis
    - Pipeline velocity tracking
    - Combined B2B attribution model
    
    Returns detailed attribution results with insights and recommendations.
    """
    try:
        attribution_api.logger.info(
            "B2B attribution calculation requested",
            account_ids=request.account_ids,
            date_range=f"{request.date_from} to {request.date_to}"
        )
        
        # Convert dates to datetime if provided
        date_from = datetime.combine(request.date_from, datetime.min.time()) if request.date_from else None
        date_to = datetime.combine(request.date_to, datetime.max.time()) if request.date_to else None
        
        results = await attribution_api.attribution_service.calculate_b2b_attribution(
            db_session=db_session,
            account_ids=request.account_ids,
            date_from=date_from,
            date_to=date_to,
            attribution_weights=request.attribution_weights
        )
        
        return {
            "status": "success",
            "data": results,
            "message": "B2B attribution calculated successfully"
        }
        
    except Exception as e:
        attribution_api.logger.error(f"Error calculating B2B attribution: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate B2B attribution: {str(e)}"
        )


@router.post("/b2b/channel-insights", response_model=Dict)
async def get_channel_performance_insights(
    request: ChannelInsightsRequest,
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Get detailed channel performance insights for B2B marketing.
    
    Analyzes channel performance including:
    - ROI by channel
    - Cost efficiency metrics
    - Touchpoint volume analysis
    - Actionable optimization recommendations
    
    Returns channel-specific insights and recommendations for optimization.
    """
    try:
        attribution_api.logger.info(
            "Channel insights requested",
            account_ids=request.account_ids,
            date_range=f"{request.date_from} to {request.date_to}"
        )
        
        # Convert dates to datetime if provided
        date_from = datetime.combine(request.date_from, datetime.min.time()) if request.date_from else None
        date_to = datetime.combine(request.date_to, datetime.max.time()) if request.date_to else None
        
        insights = await attribution_api.attribution_service.get_channel_performance_insights(
            db_session=db_session,
            account_ids=request.account_ids,
            date_from=date_from,
            date_to=date_to
        )
        
        return {
            "status": "success",
            "data": insights,
            "message": "Channel performance insights generated successfully"
        }
        
    except Exception as e:
        attribution_api.logger.error(f"Error generating channel insights: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate channel insights: {str(e)}"
        )


@router.post("/b2b/alignment-report", response_model=Dict)
async def get_sales_marketing_alignment_report(
    request: AlignmentReportRequest,
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Generate sales-marketing alignment report.
    
    Analyzes the collaboration and alignment between sales and marketing teams:
    - Attribution split between sales and marketing touchpoints
    - Joint touchpoint analysis
    - Alignment score calculation
    - Specific recommendations for improvement
    - Letter grade assessment
    
    Returns comprehensive alignment analysis with actionable recommendations.
    """
    try:
        attribution_api.logger.info(
            "Sales-marketing alignment report requested",
            account_ids=request.account_ids,
            date_range=f"{request.date_from} to {request.date_to}"
        )
        
        # Convert dates to datetime if provided
        date_from = datetime.combine(request.date_from, datetime.min.time()) if request.date_from else None
        date_to = datetime.combine(request.date_to, datetime.max.time()) if request.date_to else None
        
        report = await attribution_api.attribution_service.get_sales_marketing_alignment_report(
            db_session=db_session,
            account_ids=request.account_ids,
            date_from=date_from,
            date_to=date_to
        )
        
        return {
            "status": "success",
            "data": report,
            "message": "Sales-marketing alignment report generated successfully"
        }
        
    except Exception as e:
        attribution_api.logger.error(f"Error generating alignment report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate alignment report: {str(e)}"
        )


@router.get("/b2b/touchpoint-types", response_model=Dict)
async def get_b2b_touchpoint_types():
    """
    Get available B2B touchpoint types and their attribution weights.
    
    Returns:
    - List of available touchpoint types
    - Base attribution weights for each type
    - Descriptions of touchpoint categories
    """
    try:
        from backend.app.services.b2b_attribution_engine import TouchpointType
        
        engine = B2BAttributionService().engine
        
        touchpoint_info = {}
        for touchpoint_type in TouchpointType:
            weight = engine.touchpoint_type_weights.get(touchpoint_type, 1.0)
            touchpoint_info[touchpoint_type.value] = {
                "weight": weight,
                "category": _get_touchpoint_category(touchpoint_type),
                "description": _get_touchpoint_description(touchpoint_type)
            }
        
        return {
            "status": "success",
            "data": {
                "touchpoint_types": touchpoint_info,
                "lead_quality_multipliers": engine.lead_quality_multipliers,
                "stage_progression_weights": {
                    stage.value: weight 
                    for stage, weight in engine.stage_progression_weights.items()
                }
            },
            "message": "B2B touchpoint types retrieved successfully"
        }
        
    except Exception as e:
        attribution_api.logger.error(f"Error retrieving touchpoint types: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve touchpoint types: {str(e)}"
        )


@router.get("/b2b/model-info", response_model=Dict)
async def get_b2b_model_info():
    """
    Get information about the B2B attribution model.
    
    Returns:
    - Model description and methodology
    - Attribution factors and their default weights
    - B2B-specific features
    - Expected data requirements
    """
    try:
        model_info = {
            "model_name": "B2B Marketing Attribution Engine",
            "version": "1.0.0",
            "description": "Comprehensive B2B attribution model designed for complex sales cycles and account-based marketing",
            "attribution_factors": {
                "time_weighted": {
                    "weight": 0.25,
                    "description": "Time decay attribution accounting for long B2B sales cycles (3-18 months)"
                },
                "quality_weighted": {
                    "weight": 0.25,
                    "description": "Lead quality impact based on scoring and demographic fit"
                },
                "account_based": {
                    "weight": 0.25,
                    "description": "Account-level attribution considering buying committee and deal complexity"
                },
                "stage_progression": {
                    "weight": 0.15,
                    "description": "Attribution based on touchpoint influence on funnel progression"
                },
                "pipeline_velocity": {
                    "weight": 0.10,
                    "description": "Impact on sales cycle acceleration and deal velocity"
                }
            },
            "b2b_features": [
                "Long sales cycle optimization (3-18 months)",
                "Lead quality scoring integration",
                "Account-based marketing support",
                "Buying committee analysis",
                "Sales-marketing alignment tracking",
                "Pipeline velocity optimization",
                "Enterprise deal complexity handling"
            ],
            "data_requirements": {
                "leads": ["lead_score", "demographic_score", "behavioral_score", "firmographic_score", "quality_tier"],
                "opportunities": ["deal_size", "sales_cycle_days", "decision_makers_count", "close_date"],
                "touchpoints": ["engagement_score", "touchpoint_type", "channel", "sales_rep_id", "cost"]
            },
            "supported_deal_tiers": ["enterprise", "mid-market", "smb"],
            "supported_sales_cycles": {
                "enterprise": "270 days (9 months)",
                "mid-market": "150 days (5 months)", 
                "smb": "60 days (2 months)"
            }
        }
        
        return {
            "status": "success",
            "data": model_info,
            "message": "B2B model information retrieved successfully"
        }
        
    except Exception as e:
        attribution_api.logger.error(f"Error retrieving model info: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve model info: {str(e)}"
        )


def _get_touchpoint_category(touchpoint_type) -> str:
    """Get category for touchpoint type."""
    from backend.app.services.b2b_attribution_engine import TouchpointType
    
    high_intent = [TouchpointType.DEMO_REQUEST, TouchpointType.SALES_CALL]
    engagement = [TouchpointType.WEBINAR_ATTENDANCE, TouchpointType.CONTENT_DOWNLOAD, TouchpointType.TRADE_SHOW]
    nurturing = [TouchpointType.EMAIL_ENGAGEMENT, TouchpointType.DIRECT_MAIL]
    awareness = [TouchpointType.WEBSITE_VISIT, TouchpointType.SOCIAL_ENGAGEMENT]
    referral = [TouchpointType.REFERRAL]
    
    if touchpoint_type in high_intent:
        return "High Intent"
    elif touchpoint_type in engagement:
        return "Engagement"
    elif touchpoint_type in nurturing:
        return "Nurturing"
    elif touchpoint_type in awareness:
        return "Awareness"
    elif touchpoint_type in referral:
        return "Referral"
    else:
        return "Other"


def _get_touchpoint_description(touchpoint_type) -> str:
    """Get description for touchpoint type."""
    from backend.app.services.b2b_attribution_engine import TouchpointType
    
    descriptions = {
        TouchpointType.DEMO_REQUEST: "High-intent touchpoint indicating strong purchase consideration",
        TouchpointType.SALES_CALL: "Direct sales interaction with high conversion potential",
        TouchpointType.WEBINAR_ATTENDANCE: "Educational content engagement showing interest",
        TouchpointType.CONTENT_DOWNLOAD: "Content consumption indicating research behavior",
        TouchpointType.TRADE_SHOW: "In-person event interaction with high engagement value",
        TouchpointType.EMAIL_ENGAGEMENT: "Email marketing interaction for nurturing",
        TouchpointType.WEBSITE_VISIT: "General website interaction for awareness building",
        TouchpointType.SOCIAL_ENGAGEMENT: "Social media interaction and engagement",
        TouchpointType.DIRECT_MAIL: "Physical marketing material interaction",
        TouchpointType.REFERRAL: "Word-of-mouth or partner referral with highest trust value"
    }
    
    return descriptions.get(touchpoint_type, "Generic touchpoint interaction")


# Legacy endpoint for backward compatibility
@router.post("/calculate", response_model=Dict)
async def calculate_attribution_legacy(
    model_name: str = Query(..., description="Attribution model name (use 'b2b' for B2B model)"),
    account_ids: Optional[List[str]] = Query(None, description="Account IDs to analyze"),
    date_from: Optional[date] = Query(None, description="Start date"),
    date_to: Optional[date] = Query(None, description="End date"),
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Legacy attribution calculation endpoint.
    
    This endpoint maintains backward compatibility while redirecting to the new B2B engine.
    For new implementations, use the /b2b/calculate endpoint instead.
    """
    attribution_api.logger.warning(
        "Legacy attribution endpoint used - consider migrating to /b2b/calculate",
        model_name=model_name
    )
    
    # Redirect to B2B model regardless of requested model
    request = AttributionRequest(
        account_ids=account_ids,
        date_from=date_from,
        date_to=date_to
    )
    
    return await calculate_b2b_attribution(request, db_session)