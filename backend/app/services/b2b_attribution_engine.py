"""
B2B Marketing Attribution Engine

Specifically designed for B2B marketing workflows with complex sales cycles,
lead scoring, account-based marketing, and pipeline velocity tracking.
"""
import math
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

from backend.app.utils.logging import LoggerMixin, log_attribution_calculation
from config.settings import get_attribution_settings


class B2BStageType(Enum):
    """B2B sales funnel stages"""
    AWARENESS = "awareness"
    INTEREST = "interest"
    CONSIDERATION = "consideration"
    INTENT = "intent"
    EVALUATION = "evaluation"
    PURCHASE = "purchase"


class TouchpointType(Enum):
    """B2B touchpoint types with different attribution weights"""
    CONTENT_DOWNLOAD = "content_download"
    WEBINAR_ATTENDANCE = "webinar_attendance"
    DEMO_REQUEST = "demo_request"
    TRADE_SHOW = "trade_show"
    SALES_CALL = "sales_call"
    EMAIL_ENGAGEMENT = "email_engagement"
    WEBSITE_VISIT = "website_visit"
    SOCIAL_ENGAGEMENT = "social_engagement"
    DIRECT_MAIL = "direct_mail"
    REFERRAL = "referral"


@dataclass
class LeadData:
    """Lead information for attribution"""
    lead_id: str
    account_id: str
    lead_score: int
    demographic_score: int
    behavioral_score: int
    firmographic_score: int
    created_date: datetime
    stage: B2BStageType
    source: str
    lead_quality_tier: str  # A, B, C, D


@dataclass
class OpportunityData:
    """Opportunity/deal information"""
    opportunity_id: str
    account_id: str
    lead_ids: List[str]
    stage: str
    probability: float
    amount: float
    created_date: datetime
    close_date: Optional[datetime]
    sales_cycle_days: int
    deal_size_tier: str  # enterprise, mid-market, smb
    decision_makers_count: int
    influencers_count: int


@dataclass
class TouchpointData:
    """Enhanced touchpoint data for B2B attribution"""
    touchpoint_id: str
    lead_id: str
    account_id: str
    timestamp: datetime
    touchpoint_type: TouchpointType
    channel: str
    campaign_id: Optional[str]
    content_id: Optional[str]
    engagement_score: float  # 0-100
    stage_influence: B2BStageType
    cost: float
    is_sales_touch: bool
    is_marketing_touch: bool
    sales_rep_id: Optional[str]


class B2BMarketingAttributionEngine(LoggerMixin):
    """
    Specifically designed for B2B marketing workflows with complex attribution models
    that account for long sales cycles, lead quality, and account-based marketing.
    """
    
    def __init__(self):
        self.settings = get_attribution_settings()
        
        # B2B-specific model weights
        self.touchpoint_type_weights = {
            TouchpointType.DEMO_REQUEST: 1.5,
            TouchpointType.SALES_CALL: 1.4,
            TouchpointType.WEBINAR_ATTENDANCE: 1.2,
            TouchpointType.CONTENT_DOWNLOAD: 1.1,
            TouchpointType.TRADE_SHOW: 1.3,
            TouchpointType.EMAIL_ENGAGEMENT: 0.8,
            TouchpointType.WEBSITE_VISIT: 0.6,
            TouchpointType.SOCIAL_ENGAGEMENT: 0.7,
            TouchpointType.DIRECT_MAIL: 0.9,
            TouchpointType.REFERRAL: 1.6,
        }
        
        self.stage_progression_weights = {
            B2BStageType.AWARENESS: 0.8,
            B2BStageType.INTEREST: 1.0,
            B2BStageType.CONSIDERATION: 1.2,
            B2BStageType.INTENT: 1.4,
            B2BStageType.EVALUATION: 1.5,
            B2BStageType.PURCHASE: 1.3,
        }
        
        self.lead_quality_multipliers = {
            'A': 1.5,  # High-quality leads
            'B': 1.2,  # Medium-quality leads
            'C': 1.0,  # Low-quality leads
            'D': 0.7,  # Very low-quality leads
        }

    def b2b_specific_attribution(
        self,
        lead_data: List[LeadData],
        opportunity_data: List[OpportunityData],
        touchpoint_data: List[TouchpointData]
    ) -> Dict[str, any]:
        """
        Master attribution model specifically for B2B sales cycles.
        
        Args:
            lead_data: List of lead information
            opportunity_data: List of opportunity/deal information  
            touchpoint_data: List of touchpoint interactions
            
        Returns:
            Comprehensive B2B attribution results
        """
        self.logger.info(
            "Starting B2B attribution calculation",
            leads_count=len(lead_data),
            opportunities_count=len(opportunity_data),
            touchpoints_count=len(touchpoint_data)
        )
        
        # Calculate different attribution perspectives
        time_weighted = self.calculate_b2b_time_decay(touchpoint_data, opportunity_data)
        quality_weighted = self.calculate_lead_quality_impact(lead_data, touchpoint_data)
        account_based = self.calculate_account_level_attribution(opportunity_data, touchpoint_data)
        stage_weighted = self.calculate_stage_progression_attribution(touchpoint_data)
        velocity_impact = self.calculate_pipeline_velocity_impact(opportunity_data, touchpoint_data)
        
        # Combine all factors for comprehensive B2B attribution
        combined_attribution = self.combine_b2b_attribution_factors(
            time_weighted=time_weighted,
            quality_weighted=quality_weighted,
            account_based=account_based,
            stage_weighted=stage_weighted,
            velocity_impact=velocity_impact
        )
        
        return {
            'time_weighted_attribution': time_weighted,
            'quality_weighted_attribution': quality_weighted,
            'account_based_attribution': account_based,
            'stage_progression_attribution': stage_weighted,
            'pipeline_velocity_attribution': velocity_impact,
            'combined_b2b_attribution': combined_attribution,
            'attribution_summary': self.generate_attribution_summary(combined_attribution)
        }

    def calculate_b2b_time_decay(
        self,
        touchpoint_data: List[TouchpointData],
        opportunity_data: List[OpportunityData],
        avg_sales_cycle_days: int = 180
    ) -> Dict[str, float]:
        """
        Calculate time decay attribution accounting for long B2B sales cycles.
        
        B2B sales cycles are typically 3-18 months, requiring different decay rates
        than B2C attribution models.
        """
        attribution_weights = {}
        
        for opportunity in opportunity_data:
            opp_touchpoints = [
                tp for tp in touchpoint_data 
                if tp.account_id == opportunity.account_id
            ]
            
            if not opp_touchpoints:
                continue
                
            # Use actual sales cycle or average
            cycle_days = opportunity.sales_cycle_days or avg_sales_cycle_days
            
            # B2B-specific decay: slower decay for longer cycles
            half_life_days = max(cycle_days * 0.3, 14)  # Minimum 2 weeks
            
            conversion_date = opportunity.close_date or opportunity.created_date
            
            total_weight = 0
            touchpoint_weights = {}
            
            for touchpoint in opp_touchpoints:
                days_to_conversion = (conversion_date - touchpoint.timestamp).days
                days_to_conversion = max(0, days_to_conversion)
                
                # B2B time decay formula - gentler decay for long cycles
                weight = math.exp(-days_to_conversion / half_life_days)
                
                # Apply touchpoint type weight
                weight *= self.touchpoint_type_weights.get(touchpoint.touchpoint_type, 1.0)
                
                touchpoint_weights[touchpoint.touchpoint_id] = weight
                total_weight += weight
            
            # Normalize weights for this opportunity
            if total_weight > 0:
                for tp_id, weight in touchpoint_weights.items():
                    attribution_weights[tp_id] = (weight / total_weight) * opportunity.amount
        
        return attribution_weights

    def calculate_lead_quality_impact(
        self,
        lead_data: List[LeadData],
        touchpoint_data: List[TouchpointData]
    ) -> Dict[str, float]:
        """
        Weight touchpoints by lead quality score and demographic fit.
        
        High-quality leads should receive higher attribution weights.
        """
        lead_lookup = {lead.lead_id: lead for lead in lead_data}
        attribution_weights = {}
        
        for touchpoint in touchpoint_data:
            lead = lead_lookup.get(touchpoint.lead_id)
            if not lead:
                continue
            
            # Base weight from engagement score
            base_weight = touchpoint.engagement_score / 100.0
            
            # Apply lead quality multiplier
            quality_multiplier = self.lead_quality_multipliers.get(lead.lead_quality_tier, 1.0)
            
            # Apply lead score influence (normalized)
            score_multiplier = min(lead.lead_score / 100.0, 2.0)  # Cap at 2x
            
            # Demographic and firmographic bonus
            demo_bonus = 1 + (lead.demographic_score / 1000.0)  # Small bonus
            firmo_bonus = 1 + (lead.firmographic_score / 1000.0)  # Small bonus
            
            final_weight = (
                base_weight * 
                quality_multiplier * 
                score_multiplier * 
                demo_bonus * 
                firmo_bonus
            )
            
            attribution_weights[touchpoint.touchpoint_id] = final_weight
        
        return attribution_weights

    def calculate_account_level_attribution(
        self,
        opportunity_data: List[OpportunityData],
        touchpoint_data: List[TouchpointData]
    ) -> Dict[str, float]:
        """
        Account-based attribution for enterprise deals with multiple stakeholders.
        
        Considers buying committee size, deal size, and account complexity.
        """
        attribution_weights = {}
        
        # Group touchpoints by account
        account_touchpoints = {}
        for touchpoint in touchpoint_data:
            if touchpoint.account_id not in account_touchpoints:
                account_touchpoints[touchpoint.account_id] = []
            account_touchpoints[touchpoint.account_id].append(touchpoint)
        
        for opportunity in opportunity_data:
            account_id = opportunity.account_id
            touchpoints = account_touchpoints.get(account_id, [])
            
            if not touchpoints:
                continue
            
            # Account complexity factors
            complexity_multiplier = self._calculate_account_complexity(opportunity)
            
            # Buying committee influence
            committee_size = opportunity.decision_makers_count + opportunity.influencers_count
            committee_factor = 1 + (committee_size * 0.1)  # Larger committees = more complex attribution
            
            # Deal size influence
            deal_size_multiplier = self._get_deal_size_multiplier(opportunity.deal_size_tier)
            
            # Distribute attribution across touchpoints
            total_account_weight = 0
            touchpoint_weights = {}
            
            for touchpoint in touchpoints:
                # Base weight from touchpoint type and engagement
                base_weight = (
                    self.touchpoint_type_weights.get(touchpoint.touchpoint_type, 1.0) *
                    (touchpoint.engagement_score / 100.0)
                )
                
                # Sales vs marketing touch weighting
                if touchpoint.is_sales_touch:
                    base_weight *= 1.3  # Sales touches weighted higher in B2B
                elif touchpoint.is_marketing_touch:
                    base_weight *= 1.0
                
                # Apply account-level factors
                final_weight = (
                    base_weight * 
                    complexity_multiplier * 
                    committee_factor * 
                    deal_size_multiplier
                )
                
                touchpoint_weights[touchpoint.touchpoint_id] = final_weight
                total_account_weight += final_weight
            
            # Normalize and assign final attribution
            if total_account_weight > 0:
                for tp_id, weight in touchpoint_weights.items():
                    attribution_weights[tp_id] = (weight / total_account_weight) * opportunity.amount
        
        return attribution_weights

    def calculate_stage_progression_attribution(
        self,
        touchpoint_data: List[TouchpointData]
    ) -> Dict[str, float]:
        """
        Weight touchpoints based on their influence on stage progression.
        
        Touchpoints that move prospects through the funnel get higher weights.
        """
        attribution_weights = {}
        
        for touchpoint in touchpoint_data:
            # Base weight from engagement
            base_weight = touchpoint.engagement_score / 100.0
            
            # Apply stage influence weight
            stage_weight = self.stage_progression_weights.get(
                touchpoint.stage_influence, 
                1.0
            )
            
            # Touchpoint type influence on stage progression
            type_weight = self.touchpoint_type_weights.get(touchpoint.touchpoint_type, 1.0)
            
            # Calculate final attribution weight
            final_weight = base_weight * stage_weight * type_weight
            
            attribution_weights[touchpoint.touchpoint_id] = final_weight
        
        return attribution_weights

    def calculate_pipeline_velocity_impact(
        self,
        opportunity_data: List[OpportunityData],
        touchpoint_data: List[TouchpointData]
    ) -> Dict[str, float]:
        """
        Calculate how touchpoints impact pipeline velocity and deal acceleration.
        
        Touchpoints that accelerate deals through the pipeline get higher attribution.
        """
        attribution_weights = {}
        
        for opportunity in opportunity_data:
            opp_touchpoints = [
                tp for tp in touchpoint_data 
                if tp.account_id == opportunity.account_id
            ]
            
            if not opp_touchpoints:
                continue
            
            # Calculate velocity metrics
            actual_cycle = opportunity.sales_cycle_days
            expected_cycle = self._get_expected_cycle_days(opportunity.deal_size_tier)
            
            # Velocity multiplier - faster deals get bonus
            if actual_cycle < expected_cycle:
                velocity_bonus = 1 + ((expected_cycle - actual_cycle) / expected_cycle) * 0.5
            else:
                velocity_bonus = max(0.5, 1 - ((actual_cycle - expected_cycle) / expected_cycle) * 0.3)
            
            # Assign weights based on touchpoint timing and velocity impact
            for touchpoint in opp_touchpoints:
                base_weight = touchpoint.engagement_score / 100.0
                
                # High-impact touchpoints (demos, sales calls) get velocity bonus
                if touchpoint.touchpoint_type in [TouchpointType.DEMO_REQUEST, TouchpointType.SALES_CALL]:
                    velocity_impact = velocity_bonus * 1.2
                else:
                    velocity_impact = velocity_bonus
                
                attribution_weights[touchpoint.touchpoint_id] = base_weight * velocity_impact
        
        return attribution_weights

    def combine_b2b_attribution_factors(
        self,
        time_weighted: Dict[str, float],
        quality_weighted: Dict[str, float],
        account_based: Dict[str, float],
        stage_weighted: Dict[str, float],
        velocity_impact: Dict[str, float],
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, float]:
        """
        Combine all B2B attribution factors into a unified model.
        
        Args:
            weights: Custom weights for each factor (defaults to balanced approach)
        """
        if weights is None:
            weights = {
                'time': 0.25,
                'quality': 0.25,
                'account': 0.25,
                'stage': 0.15,
                'velocity': 0.10
            }
        
        # Get all touchpoint IDs
        all_touchpoint_ids = set()
        for attribution_dict in [time_weighted, quality_weighted, account_based, stage_weighted, velocity_impact]:
            all_touchpoint_ids.update(attribution_dict.keys())
        
        combined_attribution = {}
        
        for tp_id in all_touchpoint_ids:
            combined_score = (
                time_weighted.get(tp_id, 0) * weights['time'] +
                quality_weighted.get(tp_id, 0) * weights['quality'] +
                account_based.get(tp_id, 0) * weights['account'] +
                stage_weighted.get(tp_id, 0) * weights['stage'] +
                velocity_impact.get(tp_id, 0) * weights['velocity']
            )
            
            combined_attribution[tp_id] = combined_score
        
        return combined_attribution

    def generate_attribution_summary(
        self,
        attribution_results: Dict[str, float]
    ) -> Dict[str, any]:
        """Generate a summary of attribution results with insights."""
        if not attribution_results:
            return {}
        
        total_attribution = sum(attribution_results.values())
        touchpoint_count = len(attribution_results)
        
        # Top contributing touchpoints
        sorted_touchpoints = sorted(
            attribution_results.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        top_touchpoints = sorted_touchpoints[:5]
        
        return {
            'total_attribution_value': total_attribution,
            'touchpoint_count': touchpoint_count,
            'average_attribution_per_touchpoint': total_attribution / touchpoint_count if touchpoint_count > 0 else 0,
            'top_contributing_touchpoints': [
                {'touchpoint_id': tp_id, 'attribution_value': value, 'percentage': (value/total_attribution)*100}
                for tp_id, value in top_touchpoints
            ],
            'attribution_distribution': {
                'top_20_percent': sum(dict(sorted_touchpoints[:max(1, touchpoint_count//5)]).values()),
                'bottom_20_percent': sum(dict(sorted_touchpoints[-max(1, touchpoint_count//5):]).values())
            }
        }

    def _calculate_account_complexity(self, opportunity: OpportunityData) -> float:
        """Calculate account complexity multiplier based on deal characteristics."""
        complexity = 1.0
        
        # Deal size influence
        if opportunity.deal_size_tier == 'enterprise':
            complexity += 0.3
        elif opportunity.deal_size_tier == 'mid-market':
            complexity += 0.15
        
        # Committee size influence
        total_stakeholders = opportunity.decision_makers_count + opportunity.influencers_count
        if total_stakeholders > 5:
            complexity += 0.2
        elif total_stakeholders > 3:
            complexity += 0.1
        
        # Sales cycle length influence
        if opportunity.sales_cycle_days > 365:
            complexity += 0.25
        elif opportunity.sales_cycle_days > 180:
            complexity += 0.15
        
        return complexity

    def _get_deal_size_multiplier(self, deal_size_tier: str) -> float:
        """Get attribution multiplier based on deal size."""
        multipliers = {
            'enterprise': 1.4,
            'mid-market': 1.2,
            'smb': 1.0
        }
        return multipliers.get(deal_size_tier, 1.0)

    def _get_expected_cycle_days(self, deal_size_tier: str) -> int:
        """Get expected sales cycle days by deal size."""
        expected_cycles = {
            'enterprise': 270,  # 9 months
            'mid-market': 150,  # 5 months
            'smb': 60          # 2 months
        }
        return expected_cycles.get(deal_size_tier, 180)


class B2BAttributionAnalyzer:
    """Advanced B2B attribution analysis and reporting."""
    
    def __init__(self, attribution_engine: B2BMarketingAttributionEngine):
        self.engine = attribution_engine
    
    def analyze_channel_performance(
        self,
        attribution_results: Dict[str, float],
        touchpoint_data: List[TouchpointData]
    ) -> Dict[str, any]:
        """Analyze performance by marketing channel for B2B context."""
        channel_performance = {}
        touchpoint_lookup = {tp.touchpoint_id: tp for tp in touchpoint_data}
        
        for tp_id, attribution_value in attribution_results.items():
            touchpoint = touchpoint_lookup.get(tp_id)
            if not touchpoint:
                continue
            
            channel = touchpoint.channel
            if channel not in channel_performance:
                channel_performance[channel] = {
                    'total_attribution': 0,
                    'touchpoint_count': 0,
                    'total_cost': 0,
                    'touchpoint_types': set()
                }
            
            channel_performance[channel]['total_attribution'] += attribution_value
            channel_performance[channel]['touchpoint_count'] += 1
            channel_performance[channel]['total_cost'] += touchpoint.cost
            channel_performance[channel]['touchpoint_types'].add(touchpoint.touchpoint_type.value)
        
        # Calculate ROI and efficiency metrics
        for channel, metrics in channel_performance.items():
            if metrics['total_cost'] > 0:
                metrics['roi'] = (metrics['total_attribution'] - metrics['total_cost']) / metrics['total_cost']
                metrics['cost_per_attribution'] = metrics['total_cost'] / metrics['total_attribution']
            else:
                metrics['roi'] = float('inf') if metrics['total_attribution'] > 0 else 0
                metrics['cost_per_attribution'] = 0
            
            metrics['touchpoint_types'] = list(metrics['touchpoint_types'])
        
        return channel_performance
    
    def analyze_sales_marketing_alignment(
        self,
        attribution_results: Dict[str, float],
        touchpoint_data: List[TouchpointData]
    ) -> Dict[str, any]:
        """Analyze the contribution split between sales and marketing touchpoints."""
        sales_attribution = 0
        marketing_attribution = 0
        joint_attribution = 0
        
        touchpoint_lookup = {tp.touchpoint_id: tp for tp in touchpoint_data}
        
        for tp_id, attribution_value in attribution_results.items():
            touchpoint = touchpoint_lookup.get(tp_id)
            if not touchpoint:
                continue
            
            if touchpoint.is_sales_touch and touchpoint.is_marketing_touch:
                joint_attribution += attribution_value
            elif touchpoint.is_sales_touch:
                sales_attribution += attribution_value
            elif touchpoint.is_marketing_touch:
                marketing_attribution += attribution_value
        
        total_attribution = sales_attribution + marketing_attribution + joint_attribution
        
        return {
            'sales_attribution': sales_attribution,
            'marketing_attribution': marketing_attribution,
            'joint_attribution': joint_attribution,
            'sales_percentage': (sales_attribution / total_attribution * 100) if total_attribution > 0 else 0,
            'marketing_percentage': (marketing_attribution / total_attribution * 100) if total_attribution > 0 else 0,
            'joint_percentage': (joint_attribution / total_attribution * 100) if total_attribution > 0 else 0,
            'alignment_score': self._calculate_alignment_score(sales_attribution, marketing_attribution, joint_attribution)
        }
    
    def _calculate_alignment_score(self, sales_attr: float, marketing_attr: float, joint_attr: float) -> float:
        """Calculate a sales-marketing alignment score (0-100)."""
        total_attr = sales_attr + marketing_attr + joint_attr
        if total_attr == 0:
            return 0
        
        # Ideal balance is around 40% marketing, 40% sales, 20% joint
        marketing_pct = (marketing_attr / total_attr) * 100
        sales_pct = (sales_attr / total_attr) * 100
        joint_pct = (joint_attr / total_attr) * 100
        
        # Calculate deviation from ideal
        marketing_deviation = abs(marketing_pct - 40)
        sales_deviation = abs(sales_pct - 40)
        joint_deviation = abs(joint_pct - 20)
        
        total_deviation = marketing_deviation + sales_deviation + joint_deviation
        alignment_score = max(0, 100 - total_deviation)
        
        return alignment_score