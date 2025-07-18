"""
Unit tests for B2B Marketing Attribution Engine.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, Mock

from backend.app.services.b2b_attribution_engine import (
    B2BMarketingAttributionEngine,
    B2BAttributionAnalyzer,
    B2BStageType,
    TouchpointType,
    LeadData,
    OpportunityData,
    TouchpointData
)


class TestB2BMarketingAttributionEngine:
    """Test the main B2B attribution engine."""
    
    @pytest.fixture
    def engine(self):
        """Create a B2B attribution engine instance."""
        return B2BMarketingAttributionEngine()
    
    @pytest.fixture
    def sample_lead_data(self):
        """Create sample lead data for testing."""
        return [
            LeadData(
                lead_id="lead_1",
                account_id="account_1",
                lead_score=85,
                demographic_score=75,
                behavioral_score=90,
                firmographic_score=80,
                created_date=datetime(2024, 1, 1),
                stage=B2BStageType.INTEREST,
                source="organic_search",
                lead_quality_tier="A"
            ),
            LeadData(
                lead_id="lead_2",
                account_id="account_1",
                lead_score=65,
                demographic_score=60,
                behavioral_score=70,
                firmographic_score=55,
                created_date=datetime(2024, 1, 15),
                stage=B2BStageType.CONSIDERATION,
                source="paid_search",
                lead_quality_tier="B"
            ),
            LeadData(
                lead_id="lead_3",
                account_id="account_2",
                lead_score=45,
                demographic_score=40,
                behavioral_score=50,
                firmographic_score=35,
                created_date=datetime(2024, 2, 1),
                stage=B2BStageType.AWARENESS,
                source="social",
                lead_quality_tier="C"
            )
        ]
    
    @pytest.fixture
    def sample_opportunity_data(self):
        """Create sample opportunity data for testing."""
        return [
            OpportunityData(
                opportunity_id="opp_1",
                account_id="account_1",
                lead_ids=["lead_1", "lead_2"],
                stage="Closed Won",
                probability=1.0,
                amount=100000.0,
                created_date=datetime(2024, 1, 1),
                close_date=datetime(2024, 6, 1),
                sales_cycle_days=150,
                deal_size_tier="enterprise",
                decision_makers_count=3,
                influencers_count=2
            ),
            OpportunityData(
                opportunity_id="opp_2",
                account_id="account_2",
                lead_ids=["lead_3"],
                stage="Closed Won",
                probability=1.0,
                amount=25000.0,
                created_date=datetime(2024, 2, 1),
                close_date=datetime(2024, 4, 1),
                sales_cycle_days=60,
                deal_size_tier="smb",
                decision_makers_count=1,
                influencers_count=1
            )
        ]
    
    @pytest.fixture
    def sample_touchpoint_data(self):
        """Create sample touchpoint data for testing."""
        return [
            TouchpointData(
                touchpoint_id="tp_1",
                lead_id="lead_1",
                account_id="account_1",
                timestamp=datetime(2024, 1, 5),
                touchpoint_type=TouchpointType.CONTENT_DOWNLOAD,
                channel="organic_search",
                campaign_id="campaign_1",
                content_id="whitepaper_1",
                engagement_score=75.0,
                stage_influence=B2BStageType.AWARENESS,
                cost=0.0,
                is_sales_touch=False,
                is_marketing_touch=True,
                sales_rep_id=None
            ),
            TouchpointData(
                touchpoint_id="tp_2",
                lead_id="lead_1",
                account_id="account_1",
                timestamp=datetime(2024, 2, 1),
                touchpoint_type=TouchpointType.WEBINAR_ATTENDANCE,
                channel="email",
                campaign_id="campaign_2",
                content_id="webinar_1",
                engagement_score=85.0,
                stage_influence=B2BStageType.INTEREST,
                cost=500.0,
                is_sales_touch=False,
                is_marketing_touch=True,
                sales_rep_id=None
            ),
            TouchpointData(
                touchpoint_id="tp_3",
                lead_id="lead_1",
                account_id="account_1",
                timestamp=datetime(2024, 3, 1),
                touchpoint_type=TouchpointType.DEMO_REQUEST,
                channel="website",
                campaign_id=None,
                content_id=None,
                engagement_score=95.0,
                stage_influence=B2BStageType.INTENT,
                cost=0.0,
                is_sales_touch=True,
                is_marketing_touch=True,
                sales_rep_id="rep_1"
            ),
            TouchpointData(
                touchpoint_id="tp_4",
                lead_id="lead_1",
                account_id="account_1",
                timestamp=datetime(2024, 4, 1),
                touchpoint_type=TouchpointType.SALES_CALL,
                channel="phone",
                campaign_id=None,
                content_id=None,
                engagement_score=90.0,
                stage_influence=B2BStageType.EVALUATION,
                cost=0.0,
                is_sales_touch=True,
                is_marketing_touch=False,
                sales_rep_id="rep_1"
            ),
            TouchpointData(
                touchpoint_id="tp_5",
                lead_id="lead_3",
                account_id="account_2",
                timestamp=datetime(2024, 2, 15),
                touchpoint_type=TouchpointType.EMAIL_ENGAGEMENT,
                channel="email",
                campaign_id="campaign_3",
                content_id="newsletter_1",
                engagement_score=60.0,
                stage_influence=B2BStageType.AWARENESS,
                cost=50.0,
                is_sales_touch=False,
                is_marketing_touch=True,
                sales_rep_id=None
            )
        ]

    def test_b2b_specific_attribution_comprehensive(self, engine, sample_lead_data, sample_opportunity_data, sample_touchpoint_data):
        """Test the comprehensive B2B attribution calculation."""
        result = engine.b2b_specific_attribution(
            lead_data=sample_lead_data,
            opportunity_data=sample_opportunity_data,
            touchpoint_data=sample_touchpoint_data
        )
        
        # Check that all attribution methods are present
        assert 'time_weighted_attribution' in result
        assert 'quality_weighted_attribution' in result
        assert 'account_based_attribution' in result
        assert 'stage_progression_attribution' in result
        assert 'pipeline_velocity_attribution' in result
        assert 'combined_b2b_attribution' in result
        assert 'attribution_summary' in result
        
        # Check that attribution results are not empty
        assert len(result['combined_b2b_attribution']) > 0
        
        # Check that attribution summary has expected structure
        summary = result['attribution_summary']
        assert 'total_attribution_value' in summary
        assert 'touchpoint_count' in summary
        assert 'top_contributing_touchpoints' in summary

    def test_calculate_b2b_time_decay(self, engine, sample_opportunity_data, sample_touchpoint_data):
        """Test B2B-specific time decay attribution."""
        result = engine.calculate_b2b_time_decay(
            touchpoint_data=sample_touchpoint_data,
            opportunity_data=sample_opportunity_data
        )
        
        # Should have attribution for touchpoints
        assert len(result) > 0
        
        # Check that more recent touchpoints have higher weights for same opportunity
        account_1_touchpoints = [(tp.touchpoint_id, tp.timestamp) for tp in sample_touchpoint_data if tp.account_id == "account_1"]
        if len(account_1_touchpoints) >= 2:
            # Sort by timestamp and check weights
            sorted_tps = sorted(account_1_touchpoints, key=lambda x: x[1])
            # More recent touchpoints should generally have higher weights
            assert result.get(sorted_tps[-1][0], 0) >= result.get(sorted_tps[0][0], 0)

    def test_calculate_lead_quality_impact(self, engine, sample_lead_data, sample_touchpoint_data):
        """Test lead quality impact calculation."""
        result = engine.calculate_lead_quality_impact(
            lead_data=sample_lead_data,
            touchpoint_data=sample_touchpoint_data
        )
        
        # Should have weights for touchpoints with leads
        assert len(result) > 0
        
        # Find touchpoints for leads with different quality tiers
        lead_lookup = {lead.lead_id: lead for lead in sample_lead_data}
        
        # Check that higher quality leads get higher weights for similar touchpoints
        for tp_id, weight in result.items():
            touchpoint = next(tp for tp in sample_touchpoint_data if tp.touchpoint_id == tp_id)
            lead = lead_lookup.get(touchpoint.lead_id)
            if lead:
                assert weight > 0
                # A-tier leads should generally get higher weights than C-tier
                if lead.lead_quality_tier == 'A':
                    assert weight >= 0.5  # Reasonable minimum for A-tier leads

    def test_calculate_account_level_attribution(self, engine, sample_opportunity_data, sample_touchpoint_data):
        """Test account-based attribution calculation."""
        result = engine.calculate_account_level_attribution(
            opportunity_data=sample_opportunity_data,
            touchpoint_data=sample_touchpoint_data
        )
        
        # Should have attribution for touchpoints
        assert len(result) > 0
        
        # Check that enterprise deals get different treatment than SMB
        account_1_total = sum(weight for tp_id, weight in result.items() 
                             if any(tp.touchpoint_id == tp_id and tp.account_id == "account_1" 
                                   for tp in sample_touchpoint_data))
        account_2_total = sum(weight for tp_id, weight in result.items() 
                             if any(tp.touchpoint_id == tp_id and tp.account_id == "account_2" 
                                   for tp in sample_touchpoint_data))
        
        # Enterprise deal (account_1) should have higher total attribution
        assert account_1_total > account_2_total

    def test_calculate_stage_progression_attribution(self, engine, sample_touchpoint_data):
        """Test stage progression attribution."""
        result = engine.calculate_stage_progression_attribution(
            touchpoint_data=sample_touchpoint_data
        )
        
        # Should have weights for all touchpoints
        assert len(result) == len(sample_touchpoint_data)
        
        # Check that touchpoints with higher stage influence get higher weights
        evaluation_stage_touchpoints = [tp for tp in sample_touchpoint_data 
                                       if tp.stage_influence == B2BStageType.EVALUATION]
        awareness_stage_touchpoints = [tp for tp in sample_touchpoint_data 
                                      if tp.stage_influence == B2BStageType.AWARENESS]
        
        if evaluation_stage_touchpoints and awareness_stage_touchpoints:
            eval_weight = result[evaluation_stage_touchpoints[0].touchpoint_id]
            awareness_weight = result[awareness_stage_touchpoints[0].touchpoint_id]
            # Evaluation stage should have higher weight than awareness
            # (accounting for engagement score differences)
            assert eval_weight >= awareness_weight * 0.8  # Allow some tolerance

    def test_calculate_pipeline_velocity_impact(self, engine, sample_opportunity_data, sample_touchpoint_data):
        """Test pipeline velocity impact calculation."""
        result = engine.calculate_pipeline_velocity_impact(
            opportunity_data=sample_opportunity_data,
            touchpoint_data=sample_touchpoint_data
        )
        
        # Should have weights for touchpoints
        assert len(result) > 0
        
        # Check that demo and sales call touchpoints get velocity bonuses
        demo_touchpoints = [tp for tp in sample_touchpoint_data 
                           if tp.touchpoint_type == TouchpointType.DEMO_REQUEST]
        if demo_touchpoints:
            demo_weight = result.get(demo_touchpoints[0].touchpoint_id, 0)
            assert demo_weight > 0

    def test_combine_b2b_attribution_factors(self, engine):
        """Test combining attribution factors."""
        # Create sample attribution data
        time_weighted = {"tp_1": 100.0, "tp_2": 50.0}
        quality_weighted = {"tp_1": 80.0, "tp_2": 60.0}
        account_based = {"tp_1": 90.0, "tp_2": 40.0}
        stage_weighted = {"tp_1": 70.0, "tp_2": 30.0}
        velocity_impact = {"tp_1": 60.0, "tp_2": 20.0}
        
        result = engine.combine_b2b_attribution_factors(
            time_weighted=time_weighted,
            quality_weighted=quality_weighted,
            account_based=account_based,
            stage_weighted=stage_weighted,
            velocity_impact=velocity_impact
        )
        
        # Should have combined weights for all touchpoints
        assert "tp_1" in result
        assert "tp_2" in result
        
        # tp_1 should have higher combined weight than tp_2
        assert result["tp_1"] > result["tp_2"]

    def test_combine_b2b_attribution_factors_custom_weights(self, engine):
        """Test combining attribution factors with custom weights."""
        time_weighted = {"tp_1": 100.0}
        quality_weighted = {"tp_1": 80.0}
        account_based = {"tp_1": 90.0}
        stage_weighted = {"tp_1": 70.0}
        velocity_impact = {"tp_1": 60.0}
        
        custom_weights = {
            'time': 0.5,      # Higher weight on time
            'quality': 0.2,
            'account': 0.2,
            'stage': 0.05,
            'velocity': 0.05
        }
        
        result = engine.combine_b2b_attribution_factors(
            time_weighted=time_weighted,
            quality_weighted=quality_weighted,
            account_based=account_based,
            stage_weighted=stage_weighted,
            velocity_impact=velocity_impact,
            weights=custom_weights
        )
        
        # Should weight time factor more heavily
        expected = (100.0 * 0.5) + (80.0 * 0.2) + (90.0 * 0.2) + (70.0 * 0.05) + (60.0 * 0.05)
        assert abs(result["tp_1"] - expected) < 0.01

    def test_generate_attribution_summary(self, engine):
        """Test attribution summary generation."""
        attribution_results = {
            "tp_1": 1000.0,
            "tp_2": 500.0,
            "tp_3": 300.0,
            "tp_4": 200.0,
            "tp_5": 100.0
        }
        
        summary = engine.generate_attribution_summary(attribution_results)
        
        # Check summary structure
        assert 'total_attribution_value' in summary
        assert 'touchpoint_count' in summary
        assert 'average_attribution_per_touchpoint' in summary
        assert 'top_contributing_touchpoints' in summary
        assert 'attribution_distribution' in summary
        
        # Check values
        assert summary['total_attribution_value'] == 2100.0
        assert summary['touchpoint_count'] == 5
        assert summary['average_attribution_per_touchpoint'] == 420.0
        
        # Check top touchpoints are sorted correctly
        top_touchpoints = summary['top_contributing_touchpoints']
        assert len(top_touchpoints) == 5
        assert top_touchpoints[0]['touchpoint_id'] == 'tp_1'
        assert top_touchpoints[0]['attribution_value'] == 1000.0

    def test_calculate_account_complexity(self, engine):
        """Test account complexity calculation."""
        # Enterprise deal with many stakeholders and long cycle
        enterprise_opp = OpportunityData(
            opportunity_id="opp_enterprise",
            account_id="account_enterprise",
            lead_ids=["lead_1"],
            stage="Closed Won",
            probability=1.0,
            amount=500000.0,
            created_date=datetime(2024, 1, 1),
            close_date=datetime(2024, 12, 1),
            sales_cycle_days=400,
            deal_size_tier="enterprise",
            decision_makers_count=5,
            influencers_count=3
        )
        
        complexity = engine._calculate_account_complexity(enterprise_opp)
        
        # Should be significantly higher than base complexity
        assert complexity > 1.5
        
        # SMB deal should have lower complexity
        smb_opp = OpportunityData(
            opportunity_id="opp_smb",
            account_id="account_smb",
            lead_ids=["lead_1"],
            stage="Closed Won",
            probability=1.0,
            amount=10000.0,
            created_date=datetime(2024, 1, 1),
            close_date=datetime(2024, 2, 1),
            sales_cycle_days=30,
            deal_size_tier="smb",
            decision_makers_count=1,
            influencers_count=0
        )
        
        smb_complexity = engine._calculate_account_complexity(smb_opp)
        assert smb_complexity < complexity

    def test_touchpoint_type_weights(self, engine):
        """Test that different touchpoint types have appropriate weights."""
        # Demo requests should have higher weight than website visits
        demo_weight = engine.touchpoint_type_weights[TouchpointType.DEMO_REQUEST]
        website_weight = engine.touchpoint_type_weights[TouchpointType.WEBSITE_VISIT]
        
        assert demo_weight > website_weight
        
        # Sales calls should have high weight
        sales_call_weight = engine.touchpoint_type_weights[TouchpointType.SALES_CALL]
        assert sales_call_weight > 1.0
        
        # Referrals should have the highest weight
        referral_weight = engine.touchpoint_type_weights[TouchpointType.REFERRAL]
        assert referral_weight >= sales_call_weight

    def test_lead_quality_multipliers(self, engine):
        """Test lead quality tier multipliers."""
        # A-tier leads should have highest multiplier
        a_tier = engine.lead_quality_multipliers['A']
        b_tier = engine.lead_quality_multipliers['B']
        c_tier = engine.lead_quality_multipliers['C']
        d_tier = engine.lead_quality_multipliers['D']
        
        assert a_tier > b_tier > c_tier > d_tier
        assert a_tier >= 1.5
        assert d_tier <= 1.0


class TestB2BAttributionAnalyzer:
    """Test the B2B attribution analyzer."""
    
    @pytest.fixture
    def engine(self):
        """Create a B2B attribution engine instance."""
        return B2BMarketingAttributionEngine()
    
    @pytest.fixture
    def analyzer(self, engine):
        """Create a B2B attribution analyzer instance."""
        return B2BAttributionAnalyzer(engine)
    
    @pytest.fixture
    def sample_attribution_results(self):
        """Sample attribution results for testing."""
        return {
            "tp_1": 5000.0,
            "tp_2": 3000.0,
            "tp_3": 2000.0,
            "tp_4": 1500.0,
            "tp_5": 500.0
        }
    
    @pytest.fixture
    def sample_touchpoint_data_for_analysis(self):
        """Sample touchpoint data for analyzer testing."""
        return [
            TouchpointData(
                touchpoint_id="tp_1",
                lead_id="lead_1",
                account_id="account_1",
                timestamp=datetime(2024, 1, 5),
                touchpoint_type=TouchpointType.CONTENT_DOWNLOAD,
                channel="organic_search",
                campaign_id="campaign_1",
                content_id="whitepaper_1",
                engagement_score=75.0,
                stage_influence=B2BStageType.AWARENESS,
                cost=100.0,
                is_sales_touch=False,
                is_marketing_touch=True,
                sales_rep_id=None
            ),
            TouchpointData(
                touchpoint_id="tp_2",
                lead_id="lead_1",
                account_id="account_1",
                timestamp=datetime(2024, 2, 1),
                touchpoint_type=TouchpointType.SALES_CALL,
                channel="phone",
                campaign_id=None,
                content_id=None,
                engagement_score=90.0,
                stage_influence=B2BStageType.EVALUATION,
                cost=0.0,
                is_sales_touch=True,
                is_marketing_touch=False,
                sales_rep_id="rep_1"
            ),
            TouchpointData(
                touchpoint_id="tp_3",
                lead_id="lead_1",
                account_id="account_1",
                timestamp=datetime(2024, 3, 1),
                touchpoint_type=TouchpointType.DEMO_REQUEST,
                channel="website",
                campaign_id=None,
                content_id=None,
                engagement_score=95.0,
                stage_influence=B2BStageType.INTENT,
                cost=0.0,
                is_sales_touch=True,
                is_marketing_touch=True,
                sales_rep_id="rep_1"
            ),
            TouchpointData(
                touchpoint_id="tp_4",
                lead_id="lead_2",
                account_id="account_2",
                timestamp=datetime(2024, 2, 15),
                touchpoint_type=TouchpointType.EMAIL_ENGAGEMENT,
                channel="email",
                campaign_id="campaign_2",
                content_id="newsletter_1",
                engagement_score=60.0,
                stage_influence=B2BStageType.AWARENESS,
                cost=50.0,
                is_sales_touch=False,
                is_marketing_touch=True,
                sales_rep_id=None
            ),
            TouchpointData(
                touchpoint_id="tp_5",
                lead_id="lead_2",
                account_id="account_2",
                timestamp=datetime(2024, 3, 1),
                touchpoint_type=TouchpointType.WEBINAR_ATTENDANCE,
                channel="social",
                campaign_id="campaign_3",
                content_id="webinar_1",
                engagement_score=80.0,
                stage_influence=B2BStageType.INTEREST,
                cost=200.0,
                is_sales_touch=False,
                is_marketing_touch=True,
                sales_rep_id=None
            )
        ]

    def test_analyze_channel_performance(self, analyzer, sample_attribution_results, sample_touchpoint_data_for_analysis):
        """Test channel performance analysis."""
        result = analyzer.analyze_channel_performance(
            attribution_results=sample_attribution_results,
            touchpoint_data=sample_touchpoint_data_for_analysis
        )
        
        # Should have performance data for each channel
        assert len(result) > 0
        
        # Check structure of channel performance data
        for channel, metrics in result.items():
            assert 'total_attribution' in metrics
            assert 'touchpoint_count' in metrics
            assert 'total_cost' in metrics
            assert 'roi' in metrics
            assert 'cost_per_attribution' in metrics
            assert 'touchpoint_types' in metrics
            
            # Check that calculations are reasonable
            assert metrics['total_attribution'] > 0
            assert metrics['touchpoint_count'] > 0
            assert isinstance(metrics['touchpoint_types'], list)

    def test_analyze_sales_marketing_alignment(self, analyzer, sample_attribution_results, sample_touchpoint_data_for_analysis):
        """Test sales-marketing alignment analysis."""
        result = analyzer.analyze_sales_marketing_alignment(
            attribution_results=sample_attribution_results,
            touchpoint_data=sample_touchpoint_data_for_analysis
        )
        
        # Check structure
        assert 'sales_attribution' in result
        assert 'marketing_attribution' in result
        assert 'joint_attribution' in result
        assert 'sales_percentage' in result
        assert 'marketing_percentage' in result
        assert 'joint_percentage' in result
        assert 'alignment_score' in result
        
        # Check that percentages add up to approximately 100
        total_percentage = (
            result['sales_percentage'] + 
            result['marketing_percentage'] + 
            result['joint_percentage']
        )
        assert abs(total_percentage - 100.0) < 0.01
        
        # Alignment score should be between 0 and 100
        assert 0 <= result['alignment_score'] <= 100

    def test_calculate_alignment_score(self, analyzer):
        """Test alignment score calculation."""
        # Perfect alignment (40% marketing, 40% sales, 20% joint)
        perfect_score = analyzer._calculate_alignment_score(4000, 4000, 2000)
        assert perfect_score == 100.0
        
        # Poor alignment (100% sales, 0% marketing, 0% joint)
        poor_score = analyzer._calculate_alignment_score(10000, 0, 0)
        assert poor_score < perfect_score
        
        # No attribution
        zero_score = analyzer._calculate_alignment_score(0, 0, 0)
        assert zero_score == 0

    def test_channel_roi_calculation(self, analyzer):
        """Test ROI calculation in channel performance analysis."""
        attribution_results = {"tp_1": 1000.0, "tp_2": 500.0}
        touchpoint_data = [
            TouchpointData(
                touchpoint_id="tp_1",
                lead_id="lead_1",
                account_id="account_1",
                timestamp=datetime(2024, 1, 5),
                touchpoint_type=TouchpointType.CONTENT_DOWNLOAD,
                channel="paid_search",
                campaign_id="campaign_1",
                content_id="whitepaper_1",
                engagement_score=75.0,
                stage_influence=B2BStageType.AWARENESS,
                cost=200.0,  # Cost $200, attribution $1000 -> ROI = 4.0
                is_sales_touch=False,
                is_marketing_touch=True,
                sales_rep_id=None
            ),
            TouchpointData(
                touchpoint_id="tp_2",
                lead_id="lead_2",
                account_id="account_2",
                timestamp=datetime(2024, 1, 10),
                touchpoint_type=TouchpointType.EMAIL_ENGAGEMENT,
                channel="email",
                campaign_id="campaign_2",
                content_id="newsletter_1",
                engagement_score=60.0,
                stage_influence=B2BStageType.AWARENESS,
                cost=100.0,  # Cost $100, attribution $500 -> ROI = 4.0
                is_sales_touch=False,
                is_marketing_touch=True,
                sales_rep_id=None
            )
        ]
        
        result = analyzer.analyze_channel_performance(
            attribution_results=attribution_results,
            touchpoint_data=touchpoint_data
        )
        
        # Both channels should have ROI of 4.0
        paid_search_roi = result['paid_search']['roi']
        email_roi = result['email']['roi']
        
        assert abs(paid_search_roi - 4.0) < 0.01
        assert abs(email_roi - 4.0) < 0.01


class TestB2BDataClasses:
    """Test the B2B data classes and enums."""
    
    def test_lead_data_creation(self):
        """Test LeadData creation and attributes."""
        lead = LeadData(
            lead_id="test_lead",
            account_id="test_account",
            lead_score=85,
            demographic_score=75,
            behavioral_score=90,
            firmographic_score=80,
            created_date=datetime(2024, 1, 1),
            stage=B2BStageType.INTEREST,
            source="organic_search",
            lead_quality_tier="A"
        )
        
        assert lead.lead_id == "test_lead"
        assert lead.lead_score == 85
        assert lead.stage == B2BStageType.INTEREST
        assert lead.lead_quality_tier == "A"

    def test_opportunity_data_creation(self):
        """Test OpportunityData creation and attributes."""
        opportunity = OpportunityData(
            opportunity_id="test_opp",
            account_id="test_account",
            lead_ids=["lead_1", "lead_2"],
            stage="Closed Won",
            probability=1.0,
            amount=100000.0,
            created_date=datetime(2024, 1, 1),
            close_date=datetime(2024, 6, 1),
            sales_cycle_days=150,
            deal_size_tier="enterprise",
            decision_makers_count=3,
            influencers_count=2
        )
        
        assert opportunity.opportunity_id == "test_opp"
        assert opportunity.amount == 100000.0
        assert opportunity.deal_size_tier == "enterprise"
        assert len(opportunity.lead_ids) == 2

    def test_touchpoint_data_creation(self):
        """Test TouchpointData creation and attributes."""
        touchpoint = TouchpointData(
            touchpoint_id="test_tp",
            lead_id="test_lead",
            account_id="test_account",
            timestamp=datetime(2024, 1, 5),
            touchpoint_type=TouchpointType.DEMO_REQUEST,
            channel="website",
            campaign_id="campaign_1",
            content_id="demo_form",
            engagement_score=95.0,
            stage_influence=B2BStageType.INTENT,
            cost=0.0,
            is_sales_touch=True,
            is_marketing_touch=True,
            sales_rep_id="rep_1"
        )
        
        assert touchpoint.touchpoint_id == "test_tp"
        assert touchpoint.touchpoint_type == TouchpointType.DEMO_REQUEST
        assert touchpoint.stage_influence == B2BStageType.INTENT
        assert touchpoint.is_sales_touch is True
        assert touchpoint.is_marketing_touch is True

    def test_enum_values(self):
        """Test enum values are correct."""
        # Test B2BStageType values
        assert B2BStageType.AWARENESS.value == "awareness"
        assert B2BStageType.PURCHASE.value == "purchase"
        
        # Test TouchpointType values
        assert TouchpointType.DEMO_REQUEST.value == "demo_request"
        assert TouchpointType.SALES_CALL.value == "sales_call"
        assert TouchpointType.WEBINAR_ATTENDANCE.value == "webinar_attendance"


class TestB2BEdgeCases:
    """Test edge cases and error handling for B2B attribution."""
    
    @pytest.fixture
    def engine(self):
        """Create a B2B attribution engine instance."""
        return B2BMarketingAttributionEngine()

    def test_empty_data_handling(self, engine):
        """Test handling of empty data sets."""
        result = engine.b2b_specific_attribution(
            lead_data=[],
            opportunity_data=[],
            touchpoint_data=[]
        )
        
        # Should handle empty data gracefully
        assert isinstance(result, dict)
        # Most attribution methods should return empty results
        for key, value in result.items():
            if key != 'attribution_summary':
                assert isinstance(value, dict)

    def test_missing_lead_data(self, engine):
        """Test handling when touchpoints have no corresponding lead data."""
        touchpoint_data = [
            TouchpointData(
                touchpoint_id="tp_orphan",
                lead_id="nonexistent_lead",
                account_id="account_1",
                timestamp=datetime(2024, 1, 5),
                touchpoint_type=TouchpointType.WEBSITE_VISIT,
                channel="organic_search",
                campaign_id=None,
                content_id=None,
                engagement_score=50.0,
                stage_influence=B2BStageType.AWARENESS,
                cost=0.0,
                is_sales_touch=False,
                is_marketing_touch=True,
                sales_rep_id=None
            )
        ]
        
        quality_weighted = engine.calculate_lead_quality_impact(
            lead_data=[],  # No leads
            touchpoint_data=touchpoint_data
        )
        
        # Should handle missing leads gracefully
        assert isinstance(quality_weighted, dict)
        # Orphaned touchpoint should not get quality attribution
        assert "tp_orphan" not in quality_weighted

    def test_zero_engagement_score(self, engine):
        """Test handling of touchpoints with zero engagement score."""
        touchpoint_data = [
            TouchpointData(
                touchpoint_id="tp_zero",
                lead_id="lead_1",
                account_id="account_1",
                timestamp=datetime(2024, 1, 5),
                touchpoint_type=TouchpointType.WEBSITE_VISIT,
                channel="organic_search",
                campaign_id=None,
                content_id=None,
                engagement_score=0.0,  # Zero engagement
                stage_influence=B2BStageType.AWARENESS,
                cost=0.0,
                is_sales_touch=False,
                is_marketing_touch=True,
                sales_rep_id=None
            )
        ]
        
        lead_data = [
            LeadData(
                lead_id="lead_1",
                account_id="account_1",
                lead_score=50,
                demographic_score=50,
                behavioral_score=50,
                firmographic_score=50,
                created_date=datetime(2024, 1, 1),
                stage=B2BStageType.AWARENESS,
                source="organic_search",
                lead_quality_tier="B"
            )
        ]
        
        quality_weighted = engine.calculate_lead_quality_impact(
            lead_data=lead_data,
            touchpoint_data=touchpoint_data
        )
        
        # Should handle zero engagement gracefully
        assert "tp_zero" in quality_weighted
        # Zero engagement should result in very low attribution
        assert quality_weighted["tp_zero"] >= 0