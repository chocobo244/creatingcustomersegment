"""
Attribution service for B2B marketing attribution analysis.
"""
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import asdict

from backend.app.services.b2b_attribution_engine import (
    B2BMarketingAttributionEngine,
    B2BAttributionAnalyzer,
    B2BStageType,
    TouchpointType,
    LeadData,
    OpportunityData,
    TouchpointData
)
from backend.app.models.touchpoint import Touchpoint
from backend.app.models.customer import Customer
from backend.app.models.conversion import Conversion
from backend.app.models.attribution_result import AttributionResult
from backend.app.utils.logging import LoggerMixin
from backend.app.core.database import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select


class B2BAttributionService(LoggerMixin):
    """
    Service for managing B2B marketing attribution analysis.
    Provides high-level interface for the B2B Attribution Engine.
    """
    
    def __init__(self):
        self.engine = B2BMarketingAttributionEngine()
        self.analyzer = B2BAttributionAnalyzer(self.engine)
    
    async def calculate_b2b_attribution(
        self,
        db_session: AsyncSession,
        account_ids: Optional[List[str]] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        attribution_weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, any]:
        """
        Calculate comprehensive B2B attribution for specified accounts and date range.
        
        Args:
            db_session: Database session
            account_ids: List of account IDs to analyze (None = all accounts)
            date_from: Start date for analysis
            date_to: End date for analysis
            attribution_weights: Custom weights for attribution factors
            
        Returns:
            Comprehensive B2B attribution results
        """
        self.logger.info(
            "Starting B2B attribution calculation",
            account_ids=account_ids,
            date_from=date_from,
            date_to=date_to
        )
        
        try:
            # Load data from database
            lead_data, opportunity_data, touchpoint_data = await self._load_b2b_data(
                db_session=db_session,
                account_ids=account_ids,
                date_from=date_from,
                date_to=date_to
            )
            
            # Calculate attribution using B2B engine
            attribution_results = self.engine.b2b_specific_attribution(
                lead_data=lead_data,
                opportunity_data=opportunity_data,
                touchpoint_data=touchpoint_data
            )
            
            # Add analysis insights
            channel_analysis = self.analyzer.analyze_channel_performance(
                attribution_results=attribution_results['combined_b2b_attribution'],
                touchpoint_data=touchpoint_data
            )
            
            alignment_analysis = self.analyzer.analyze_sales_marketing_alignment(
                attribution_results=attribution_results['combined_b2b_attribution'],
                touchpoint_data=touchpoint_data
            )
            
            # Combine all results
            comprehensive_results = {
                **attribution_results,
                'channel_performance': channel_analysis,
                'sales_marketing_alignment': alignment_analysis,
                'metadata': {
                    'leads_analyzed': len(lead_data),
                    'opportunities_analyzed': len(opportunity_data),
                    'touchpoints_analyzed': len(touchpoint_data),
                    'analysis_date': datetime.utcnow().isoformat(),
                    'attribution_weights': attribution_weights
                }
            }
            
            # Store results in database
            await self._store_attribution_results(
                db_session=db_session,
                results=comprehensive_results,
                account_ids=account_ids
            )
            
            self.logger.info("B2B attribution calculation completed successfully")
            return comprehensive_results
            
        except Exception as e:
            self.logger.error(f"Error in B2B attribution calculation: {str(e)}")
            raise
    
    async def _load_b2b_data(
        self,
        db_session: AsyncSession,
        account_ids: Optional[List[str]] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> tuple[List[LeadData], List[OpportunityData], List[TouchpointData]]:
        """Load B2B data from database and convert to engine format."""
        
        # Build query conditions
        conditions = []
        if account_ids:
            conditions.append(Customer.id.in_(account_ids))
        if date_from:
            conditions.append(Touchpoint.timestamp >= date_from)
        if date_to:
            conditions.append(Touchpoint.timestamp <= date_to)
        
        # Load touchpoints with related data
        touchpoint_query = (
            select(Touchpoint)
            .options(selectinload(Touchpoint.customer))
            .options(selectinload(Touchpoint.conversion))
        )
        
        if conditions:
            touchpoint_query = touchpoint_query.where(*conditions)
        
        result = await db_session.execute(touchpoint_query)
        touchpoints = result.scalars().all()
        
        # Load customers (accounts)
        customer_query = select(Customer).options(selectinload(Customer.touchpoints))
        if account_ids:
            customer_query = customer_query.where(Customer.id.in_(account_ids))
        
        result = await db_session.execute(customer_query)
        customers = result.scalars().all()
        
        # Load conversions (opportunities)
        conversion_query = (
            select(Conversion)
            .options(selectinload(Conversion.customer))
            .options(selectinload(Conversion.touchpoints))
        )
        if account_ids:
            conversion_query = conversion_query.where(Conversion.customer_id.in_(account_ids))
        
        result = await db_session.execute(conversion_query)
        conversions = result.scalars().all()
        
        # Convert to B2B engine format
        lead_data = self._convert_customers_to_leads(customers)
        opportunity_data = self._convert_conversions_to_opportunities(conversions)
        touchpoint_data = self._convert_touchpoints_to_b2b_format(touchpoints)
        
        return lead_data, opportunity_data, touchpoint_data
    
    def _convert_customers_to_leads(self, customers: List[Customer]) -> List[LeadData]:
        """Convert Customer models to LeadData for B2B engine."""
        lead_data = []
        
        for customer in customers:
            # Extract lead scoring from customer data
            lead_score = getattr(customer, 'lead_score', 50)  # Default if not available
            demographic_score = getattr(customer, 'demographic_score', 50)
            behavioral_score = getattr(customer, 'behavioral_score', 50)
            firmographic_score = getattr(customer, 'firmographic_score', 50)
            
            # Determine lead quality tier based on lead score
            if lead_score >= 80:
                quality_tier = "A"
            elif lead_score >= 60:
                quality_tier = "B"
            elif lead_score >= 40:
                quality_tier = "C"
            else:
                quality_tier = "D"
            
            # Map customer stage to B2B stage
            stage_mapping = {
                'awareness': B2BStageType.AWARENESS,
                'interest': B2BStageType.INTEREST,
                'consideration': B2BStageType.CONSIDERATION,
                'intent': B2BStageType.INTENT,
                'evaluation': B2BStageType.EVALUATION,
                'purchase': B2BStageType.PURCHASE
            }
            stage = stage_mapping.get(getattr(customer, 'stage', 'awareness'), B2BStageType.AWARENESS)
            
            lead = LeadData(
                lead_id=customer.id,
                account_id=customer.id,  # In this context, customer == account
                lead_score=lead_score,
                demographic_score=demographic_score,
                behavioral_score=behavioral_score,
                firmographic_score=firmographic_score,
                created_date=customer.created_at,
                stage=stage,
                source=getattr(customer, 'source', 'unknown'),
                lead_quality_tier=quality_tier
            )
            lead_data.append(lead)
        
        return lead_data
    
    def _convert_conversions_to_opportunities(self, conversions: List[Conversion]) -> List[OpportunityData]:
        """Convert Conversion models to OpportunityData for B2B engine."""
        opportunity_data = []
        
        for conversion in conversions:
            # Calculate sales cycle
            if hasattr(conversion, 'close_date') and conversion.close_date:
                cycle_days = (conversion.close_date - conversion.created_at).days
            else:
                cycle_days = 90  # Default cycle
            
            # Determine deal size tier based on value
            if conversion.value >= 100000:
                deal_tier = "enterprise"
            elif conversion.value >= 25000:
                deal_tier = "mid-market"
            else:
                deal_tier = "smb"
            
            opportunity = OpportunityData(
                opportunity_id=conversion.id,
                account_id=conversion.customer_id,
                lead_ids=[conversion.customer_id],  # Single lead per conversion in this model
                stage="Closed Won",  # Conversions are closed deals
                probability=1.0,
                amount=conversion.value,
                created_date=conversion.created_at,
                close_date=getattr(conversion, 'close_date', conversion.created_at),
                sales_cycle_days=cycle_days,
                deal_size_tier=deal_tier,
                decision_makers_count=getattr(conversion, 'decision_makers_count', 1),
                influencers_count=getattr(conversion, 'influencers_count', 0)
            )
            opportunity_data.append(opportunity)
        
        return opportunity_data
    
    def _convert_touchpoints_to_b2b_format(self, touchpoints: List[Touchpoint]) -> List[TouchpointData]:
        """Convert Touchpoint models to TouchpointData for B2B engine."""
        touchpoint_data = []
        
        for touchpoint in touchpoints:
            # Map generic touchpoint types to B2B types
            type_mapping = {
                'email': TouchpointType.EMAIL_ENGAGEMENT,
                'website': TouchpointType.WEBSITE_VISIT,
                'social': TouchpointType.SOCIAL_ENGAGEMENT,
                'search': TouchpointType.WEBSITE_VISIT,
                'content': TouchpointType.CONTENT_DOWNLOAD,
                'webinar': TouchpointType.WEBINAR_ATTENDANCE,
                'demo': TouchpointType.DEMO_REQUEST,
                'call': TouchpointType.SALES_CALL,
                'trade_show': TouchpointType.TRADE_SHOW,
                'referral': TouchpointType.REFERRAL,
                'direct_mail': TouchpointType.DIRECT_MAIL
            }
            
            touchpoint_type = type_mapping.get(
                touchpoint.channel.lower(), 
                TouchpointType.WEBSITE_VISIT
            )
            
            # Determine stage influence based on touchpoint type and channel
            if touchpoint_type in [TouchpointType.DEMO_REQUEST, TouchpointType.SALES_CALL]:
                stage_influence = B2BStageType.EVALUATION
            elif touchpoint_type in [TouchpointType.WEBINAR_ATTENDANCE, TouchpointType.CONTENT_DOWNLOAD]:
                stage_influence = B2BStageType.CONSIDERATION
            elif touchpoint_type == TouchpointType.EMAIL_ENGAGEMENT:
                stage_influence = B2BStageType.INTEREST
            else:
                stage_influence = B2BStageType.AWARENESS
            
            # Determine if it's a sales or marketing touch
            sales_channels = ['call', 'sales_call', 'demo', 'phone']
            marketing_channels = ['email', 'social', 'content', 'webinar', 'website', 'search']
            
            is_sales_touch = touchpoint.channel.lower() in sales_channels
            is_marketing_touch = touchpoint.channel.lower() in marketing_channels
            
            # If it's a demo request, it's both sales and marketing
            if touchpoint_type == TouchpointType.DEMO_REQUEST:
                is_sales_touch = True
                is_marketing_touch = True
            
            b2b_touchpoint = TouchpointData(
                touchpoint_id=touchpoint.id,
                lead_id=touchpoint.customer_id,
                account_id=touchpoint.customer_id,
                timestamp=touchpoint.timestamp,
                touchpoint_type=touchpoint_type,
                channel=touchpoint.channel,
                campaign_id=getattr(touchpoint, 'campaign_id', None),
                content_id=getattr(touchpoint, 'content_id', None),
                engagement_score=getattr(touchpoint, 'engagement_score', 50.0),
                stage_influence=stage_influence,
                cost=getattr(touchpoint, 'cost', 0.0),
                is_sales_touch=is_sales_touch,
                is_marketing_touch=is_marketing_touch,
                sales_rep_id=getattr(touchpoint, 'sales_rep_id', None)
            )
            touchpoint_data.append(b2b_touchpoint)
        
        return touchpoint_data
    
    async def _store_attribution_results(
        self,
        db_session: AsyncSession,
        results: Dict[str, any],
        account_ids: Optional[List[str]]
    ) -> None:
        """Store attribution results in database."""
        try:
            # Store overall attribution results
            attribution_result = AttributionResult(
                model_name="B2B_Marketing_Attribution",
                results=results,
                created_at=datetime.utcnow(),
                metadata={
                    'account_ids': account_ids,
                    'model_type': 'b2b_comprehensive'
                }
            )
            
            db_session.add(attribution_result)
            await db_session.commit()
            
            self.logger.info("Attribution results stored successfully")
            
        except Exception as e:
            self.logger.error(f"Error storing attribution results: {str(e)}")
            await db_session.rollback()
            raise
    
    async def get_channel_performance_insights(
        self,
        db_session: AsyncSession,
        account_ids: Optional[List[str]] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, any]:
        """Get detailed channel performance insights for B2B marketing."""
        
        # Load data and calculate attribution
        lead_data, opportunity_data, touchpoint_data = await self._load_b2b_data(
            db_session=db_session,
            account_ids=account_ids,
            date_from=date_from,
            date_to=date_to
        )
        
        if not touchpoint_data:
            return {'channels': {}, 'insights': 'No touchpoint data available for analysis'}
        
        # Calculate attribution
        attribution_results = self.engine.b2b_specific_attribution(
            lead_data=lead_data,
            opportunity_data=opportunity_data,
            touchpoint_data=touchpoint_data
        )
        
        # Analyze channel performance
        channel_analysis = self.analyzer.analyze_channel_performance(
            attribution_results=attribution_results['combined_b2b_attribution'],
            touchpoint_data=touchpoint_data
        )
        
        # Generate insights
        insights = self._generate_channel_insights(channel_analysis)
        
        return {
            'channels': channel_analysis,
            'insights': insights,
            'summary': {
                'total_channels': len(channel_analysis),
                'best_performing_channel': max(channel_analysis.keys(), 
                                             key=lambda k: channel_analysis[k]['roi']) if channel_analysis else None,
                'analysis_period': f"{date_from} to {date_to}" if date_from and date_to else "All time"
            }
        }
    
    def _generate_channel_insights(self, channel_analysis: Dict[str, any]) -> List[str]:
        """Generate actionable insights from channel analysis."""
        insights = []
        
        if not channel_analysis:
            return ["No channel data available for analysis"]
        
        # Find best and worst performing channels
        channels_by_roi = sorted(
            channel_analysis.items(), 
            key=lambda x: x[1]['roi'], 
            reverse=True
        )
        
        if channels_by_roi:
            best_channel = channels_by_roi[0]
            insights.append(
                f"Best performing channel: {best_channel[0]} with ROI of {best_channel[1]['roi']:.2f}"
            )
            
            worst_channel = channels_by_roi[-1]
            if worst_channel[1]['roi'] < 0:
                insights.append(
                    f"Consider optimizing {worst_channel[0]} channel - currently showing negative ROI of {worst_channel[1]['roi']:.2f}"
                )
        
        # Find channels with high volume but low efficiency
        for channel, metrics in channel_analysis.items():
            if metrics['touchpoint_count'] > 10 and metrics['roi'] < 1.0:
                insights.append(
                    f"{channel} has high touchpoint volume ({metrics['touchpoint_count']}) but low ROI ({metrics['roi']:.2f}) - opportunity for optimization"
                )
        
        # Find high-cost channels
        high_cost_threshold = 1000
        for channel, metrics in channel_analysis.items():
            if metrics['total_cost'] > high_cost_threshold and metrics['roi'] < 2.0:
                insights.append(
                    f"{channel} is a high-cost channel (${metrics['total_cost']:.0f}) with moderate ROI ({metrics['roi']:.2f}) - consider cost optimization"
                )
        
        return insights
    
    async def get_sales_marketing_alignment_report(
        self,
        db_session: AsyncSession,
        account_ids: Optional[List[str]] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, any]:
        """Generate sales-marketing alignment report."""
        
        # Load data and calculate attribution
        lead_data, opportunity_data, touchpoint_data = await self._load_b2b_data(
            db_session=db_session,
            account_ids=account_ids,
            date_from=date_from,
            date_to=date_to
        )
        
        if not touchpoint_data:
            return {
                'alignment_score': 0,
                'recommendations': ['No touchpoint data available for analysis']
            }
        
        # Calculate attribution
        attribution_results = self.engine.b2b_specific_attribution(
            lead_data=lead_data,
            opportunity_data=opportunity_data,
            touchpoint_data=touchpoint_data
        )
        
        # Analyze alignment
        alignment_analysis = self.analyzer.analyze_sales_marketing_alignment(
            attribution_results=attribution_results['combined_b2b_attribution'],
            touchpoint_data=touchpoint_data
        )
        
        # Generate recommendations
        recommendations = self._generate_alignment_recommendations(alignment_analysis)
        
        return {
            **alignment_analysis,
            'recommendations': recommendations,
            'grade': self._get_alignment_grade(alignment_analysis['alignment_score'])
        }
    
    def _generate_alignment_recommendations(self, alignment_data: Dict[str, any]) -> List[str]:
        """Generate recommendations for improving sales-marketing alignment."""
        recommendations = []
        
        score = alignment_data['alignment_score']
        sales_pct = alignment_data['sales_percentage']
        marketing_pct = alignment_data['marketing_percentage']
        joint_pct = alignment_data['joint_percentage']
        
        if score < 50:
            recommendations.append("Poor sales-marketing alignment detected. Consider implementing joint planning sessions.")
        
        if sales_pct > 60:
            recommendations.append("Sales is dominating attribution. Increase marketing's role in lead nurturing and qualification.")
        elif sales_pct < 20:
            recommendations.append("Sales involvement is low. Consider more sales-marketing collaboration on qualified leads.")
        
        if marketing_pct > 60:
            recommendations.append("Marketing is dominating attribution. Ensure sales is properly engaged in the process.")
        elif marketing_pct < 20:
            recommendations.append("Marketing involvement is low. Increase marketing touchpoints throughout the sales cycle.")
        
        if joint_pct < 10:
            recommendations.append("Very few joint sales-marketing touchpoints. Consider collaborative campaigns and activities.")
        elif joint_pct > 40:
            recommendations.append("High joint touchpoint percentage. Ensure clear ownership and accountability.")
        
        if score >= 80:
            recommendations.append("Excellent alignment! Continue current collaboration practices and consider sharing best practices.")
        
        return recommendations
    
    def _get_alignment_grade(self, score: float) -> str:
        """Convert alignment score to letter grade."""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "F"