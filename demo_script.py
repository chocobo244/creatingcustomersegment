#!/usr/bin/env python3
"""
B2B Marketing Attribution Platform - Comprehensive Demo Script

This demo showcases the complete B2B attribution capabilities including:
- B2B-specific attribution models
- Sales-marketing alignment analysis
- Channel performance optimization
- Pipeline velocity tracking
- Integration with existing marketing analytics
"""

import asyncio
import json
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import asdict

# Import our B2B attribution components
from backend.app.services.b2b_attribution_engine import (
    B2BMarketingAttributionEngine,
    B2BAttributionAnalyzer,
    B2BStageType,
    TouchpointType,
    LeadData,
    OpportunityData,
    TouchpointData
)
from backend.app.services.attribution_service import B2BAttributionService


class B2BMarketingAttributionDemo:
    """
    Comprehensive demo showcasing B2B marketing attribution capabilities
    with realistic enterprise scenarios and integration examples.
    """
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.attribution_engine = B2BMarketingAttributionEngine()
        self.analyzer = B2BAttributionAnalyzer(self.attribution_engine)
        self.demo_data = self._generate_realistic_b2b_data()
        
    def run_complete_demo(self):
        """Run the complete B2B attribution demo with all features."""
        print("🎯 B2B Marketing Attribution Platform - Enterprise Demo")
        print("=" * 80)
        print("\nDesigned for complex B2B sales cycles, account-based marketing,")
        print("and sophisticated attribution across buying committees.\n")
        
        # Demo sections
        sections = [
            ("1️⃣", "B2B Attribution Engine Overview", self.demo_attribution_models),
            ("2️⃣", "Enterprise Account Analysis", self.demo_enterprise_scenarios),
            ("3️⃣", "Sales-Marketing Alignment", self.demo_sales_marketing_alignment),
            ("4️⃣", "Channel Performance Optimization", self.demo_channel_performance),
            ("5️⃣", "Pipeline Velocity Analysis", self.demo_pipeline_velocity),
            ("6️⃣", "Integration with Existing Systems", self.demo_system_integration),
            ("7️⃣", "ROI Impact & Business Value", self.demo_roi_impact)
        ]
        
        results = {}
        
        for emoji, title, demo_func in sections:
            print(f"\n{emoji} {title}")
            print("-" * 60)
            
            try:
                section_results = demo_func()
                results[title.lower().replace(" ", "_")] = section_results
                print(f"✅ {title} - Complete\n")
                
            except Exception as e:
                print(f"❌ Error in {title}: {str(e)}")
                continue
        
        # Final summary
        self._print_demo_summary(results)
        return results
    
    def demo_attribution_models(self):
        """Demonstrate the B2B-specific attribution models."""
        print("🔍 B2B Attribution Models Analysis")
        print("   Sophisticated models designed for complex B2B sales cycles\n")
        
        # Use sample enterprise deal
        sample_lead = self.demo_data['leads'][0]  # Enterprise lead
        sample_opportunity = self.demo_data['opportunities'][0]  # Enterprise deal
        sample_touchpoints = [tp for tp in self.demo_data['touchpoints'] 
                            if tp.account_id == sample_opportunity.account_id]
        
        print(f"📊 Analyzing Enterprise Deal: {sample_opportunity.opportunity_id}")
        print(f"   • Deal Value: ${sample_opportunity.amount:,.2f}")
        print(f"   • Sales Cycle: {sample_opportunity.sales_cycle_days} days")
        print(f"   • Buying Committee: {sample_opportunity.decision_makers_count + sample_opportunity.influencers_count} people")
        print(f"   • Touchpoints: {len(sample_touchpoints)} interactions\n")
        
        # Calculate attribution using different models
        attribution_results = self.attribution_engine.b2b_specific_attribution(
            lead_data=[sample_lead],
            opportunity_data=[sample_opportunity],
            touchpoint_data=sample_touchpoints
        )
        
        # Display model results
        models = [
            ('time_weighted_attribution', 'Time-Weighted (B2B Cycles)', '⏰'),
            ('quality_weighted_attribution', 'Lead Quality Impact', '⭐'),
            ('account_based_attribution', 'Account-Based (Enterprise)', '🏢'),
            ('stage_progression_attribution', 'Stage Progression', '📈'),
            ('pipeline_velocity_attribution', 'Pipeline Velocity', '🚀'),
            ('combined_b2b_attribution', 'Combined B2B Model', '🎯')
        ]
        
        for model_key, model_name, emoji in models:
            model_results = attribution_results.get(model_key, {})
            total_attribution = sum(model_results.values())
            top_touchpoint_id = max(model_results.keys(), key=model_results.get) if model_results else None
            top_touchpoint_value = model_results.get(top_touchpoint_id, 0) if top_touchpoint_id else 0
            
            print(f"{emoji} {model_name}:")
            print(f"   • Total Attribution: ${total_attribution:,.2f}")
            if top_touchpoint_id:
                print(f"   • Top Touchpoint: {top_touchpoint_id} (${top_touchpoint_value:,.2f})")
            print()
        
        # Attribution summary
        summary = attribution_results.get('attribution_summary', {})
        print("📋 Attribution Summary:")
        print(f"   • Total Attribution Value: ${summary.get('total_attribution_value', 0):,.2f}")
        print(f"   • Average per Touchpoint: ${summary.get('average_attribution_per_touchpoint', 0):,.2f}")
        print(f"   • Top Contributing Touchpoints: {len(summary.get('top_contributing_touchpoints', []))}")
        
        return {
            'attribution_results': attribution_results,
            'sample_deal': asdict(sample_opportunity),
            'touchpoint_count': len(sample_touchpoints)
        }
    
    def demo_enterprise_scenarios(self):
        """Demonstrate attribution for different enterprise scenarios."""
        print("🏢 Enterprise Account Analysis")
        print("   Comparing attribution across deal sizes and complexity levels\n")
        
        scenarios = [
            ('Enterprise', 'enterprise', '🏭'),
            ('Mid-Market', 'mid-market', '🏢'),
            ('SMB', 'smb', '🏪')
        ]
        
        scenario_results = {}
        
        for scenario_name, deal_tier, emoji in scenarios:
            # Filter data for this scenario
            tier_opportunities = [opp for opp in self.demo_data['opportunities'] 
                                if opp.deal_size_tier == deal_tier]
            
            if not tier_opportunities:
                continue
                
            # Take first opportunity of this tier
            opportunity = tier_opportunities[0]
            leads = [lead for lead in self.demo_data['leads'] 
                    if lead.account_id == opportunity.account_id]
            touchpoints = [tp for tp in self.demo_data['touchpoints'] 
                         if tp.account_id == opportunity.account_id]
            
            # Calculate attribution
            attribution = self.attribution_engine.b2b_specific_attribution(
                lead_data=leads,
                opportunity_data=[opportunity],
                touchpoint_data=touchpoints
            )
            
            combined_attribution = attribution.get('combined_b2b_attribution', {})
            total_value = sum(combined_attribution.values())
            
            print(f"{emoji} {scenario_name} Deal Analysis:")
            print(f"   • Deal Size: ${opportunity.amount:,.2f}")
            print(f"   • Sales Cycle: {opportunity.sales_cycle_days} days")
            print(f"   • Committee Size: {opportunity.decision_makers_count + opportunity.influencers_count}")
            print(f"   • Total Attribution: ${total_value:,.2f}")
            print(f"   • Attribution Efficiency: {(total_value/opportunity.amount)*100:.1f}%")
            
            # Top touchpoint types
            touchpoint_types = {}
            for tp_id, value in combined_attribution.items():
                touchpoint = next((tp for tp in touchpoints if tp.touchpoint_id == tp_id), None)
                if touchpoint:
                    tp_type = touchpoint.touchpoint_type.value
                    touchpoint_types[tp_type] = touchpoint_types.get(tp_type, 0) + value
            
            if touchpoint_types:
                top_type = max(touchpoint_types.keys(), key=touchpoint_types.get)
                print(f"   • Top Touchpoint Type: {top_type.replace('_', ' ').title()}")
            print()
            
            scenario_results[scenario_name] = {
                'deal_value': opportunity.amount,
                'attribution_value': total_value,
                'efficiency': (total_value/opportunity.amount)*100,
                'cycle_days': opportunity.sales_cycle_days,
                'touchpoint_types': touchpoint_types
            }
        
        return scenario_results
    
    def demo_sales_marketing_alignment(self):
        """Demonstrate sales-marketing alignment analysis."""
        print("🤝 Sales-Marketing Alignment Analysis")
        print("   Measuring collaboration effectiveness between teams\n")
        
        # Calculate alignment for all data
        all_touchpoints = self.demo_data['touchpoints']
        all_attribution = self.attribution_engine.b2b_specific_attribution(
            lead_data=self.demo_data['leads'],
            opportunity_data=self.demo_data['opportunities'],
            touchpoint_data=all_touchpoints
        )
        
        # Analyze alignment
        alignment_analysis = self.analyzer.analyze_sales_marketing_alignment(
            attribution_results=all_attribution['combined_b2b_attribution'],
            touchpoint_data=all_touchpoints
        )
        
        print("📊 Alignment Metrics:")
        print(f"   • Alignment Score: {alignment_analysis['alignment_score']:.1f}/100")
        print(f"   • Alignment Grade: {self._get_alignment_grade(alignment_analysis['alignment_score'])}")
        print()
        
        print("📈 Attribution Distribution:")
        print(f"   • Sales Attribution: {alignment_analysis['sales_percentage']:.1f}%")
        print(f"   • Marketing Attribution: {alignment_analysis['marketing_percentage']:.1f}%")
        print(f"   • Joint Attribution: {alignment_analysis['joint_percentage']:.1f}%")
        print()
        
        print("💰 Financial Impact:")
        total_sales = alignment_analysis['sales_attribution']
        total_marketing = alignment_analysis['marketing_attribution']
        total_joint = alignment_analysis['joint_attribution']
        print(f"   • Sales-Driven Revenue: ${total_sales:,.2f}")
        print(f"   • Marketing-Driven Revenue: ${total_marketing:,.2f}")
        print(f"   • Collaborative Revenue: ${total_joint:,.2f}")
        print()
        
        # Recommendations
        recommendations = self._generate_alignment_recommendations(alignment_analysis)
        print("🎯 Alignment Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
        
        return {
            'alignment_score': alignment_analysis['alignment_score'],
            'distribution': {
                'sales': alignment_analysis['sales_percentage'],
                'marketing': alignment_analysis['marketing_percentage'],
                'joint': alignment_analysis['joint_percentage']
            },
            'recommendations': recommendations,
            'financial_impact': {
                'sales_revenue': total_sales,
                'marketing_revenue': total_marketing,
                'joint_revenue': total_joint
            }
        }
    
    def demo_channel_performance(self):
        """Demonstrate channel performance analysis and optimization."""
        print("📺 Channel Performance Optimization")
        print("   ROI analysis and optimization recommendations\n")
        
        # Calculate attribution
        attribution_results = self.attribution_engine.b2b_specific_attribution(
            lead_data=self.demo_data['leads'],
            opportunity_data=self.demo_data['opportunities'],
            touchpoint_data=self.demo_data['touchpoints']
        )
        
        # Analyze channel performance
        channel_analysis = self.analyzer.analyze_channel_performance(
            attribution_results=attribution_results['combined_b2b_attribution'],
            touchpoint_data=self.demo_data['touchpoints']
        )
        
        print("📊 Channel Performance Summary:")
        print(f"   • Total Channels Analyzed: {len(channel_analysis)}")
        
        # Sort channels by ROI
        sorted_channels = sorted(
            channel_analysis.items(),
            key=lambda x: x[1]['roi'],
            reverse=True
        )
        
        print("\n🏆 Top Performing Channels:")
        for i, (channel, metrics) in enumerate(sorted_channels[:3], 1):
            print(f"   {i}. {channel.title()}:")
            print(f"      • ROI: {metrics['roi']:.2f}x")
            print(f"      • Attribution: ${metrics['total_attribution']:,.2f}")
            print(f"      • Cost: ${metrics['total_cost']:,.2f}")
            print(f"      • Touchpoints: {metrics['touchpoint_count']}")
            if metrics['total_cost'] > 0:
                print(f"      • Cost per Attribution: ${metrics['cost_per_attribution']:.2f}")
            print()
        
        # Channel insights
        insights = self._generate_channel_insights(channel_analysis)
        print("💡 Channel Optimization Insights:")
        for i, insight in enumerate(insights, 1):
            print(f"   {i}. {insight}")
        
        # ROI improvement potential
        total_cost = sum(metrics['total_cost'] for metrics in channel_analysis.values())
        total_attribution = sum(metrics['total_attribution'] for metrics in channel_analysis.values())
        overall_roi = (total_attribution - total_cost) / total_cost if total_cost > 0 else 0
        
        print(f"\n📈 Overall Channel Performance:")
        print(f"   • Total Marketing Spend: ${total_cost:,.2f}")
        print(f"   • Total Attribution Value: ${total_attribution:,.2f}")
        print(f"   • Overall ROI: {overall_roi:.2f}x")
        
        return {
            'channel_performance': channel_analysis,
            'top_channels': sorted_channels[:3],
            'insights': insights,
            'overall_metrics': {
                'total_cost': total_cost,
                'total_attribution': total_attribution,
                'overall_roi': overall_roi
            }
        }
    
    def demo_pipeline_velocity(self):
        """Demonstrate pipeline velocity analysis."""
        print("🚀 Pipeline Velocity Analysis")
        print("   Understanding touchpoint impact on deal acceleration\n")
        
        # Analyze velocity by deal size
        velocity_analysis = {}
        
        for tier in ['enterprise', 'mid-market', 'smb']:
            tier_opportunities = [opp for opp in self.demo_data['opportunities'] 
                                if opp.deal_size_tier == tier]
            
            if not tier_opportunities:
                continue
            
            avg_cycle = np.mean([opp.sales_cycle_days for opp in tier_opportunities])
            expected_cycle = self.attribution_engine._get_expected_cycle_days(tier)
            velocity_score = ((expected_cycle - avg_cycle) / expected_cycle) * 100
            
            velocity_analysis[tier] = {
                'avg_cycle': avg_cycle,
                'expected_cycle': expected_cycle,
                'velocity_score': velocity_score,
                'deals_count': len(tier_opportunities)
            }
        
        print("⏱️ Sales Cycle Analysis:")
        for tier, metrics in velocity_analysis.items():
            status = "🚀 Accelerated" if metrics['velocity_score'] > 0 else "⚠️ Slower"
            print(f"   • {tier.title()} Deals:")
            print(f"     - Average Cycle: {metrics['avg_cycle']:.0f} days")
            print(f"     - Expected Cycle: {metrics['expected_cycle']} days")
            print(f"     - Velocity Score: {metrics['velocity_score']:+.1f}% {status}")
            print(f"     - Sample Size: {metrics['deals_count']} deals")
            print()
        
        # Analyze high-velocity touchpoints
        velocity_touchpoints = {}
        for touchpoint in self.demo_data['touchpoints']:
            if touchpoint.touchpoint_type in [TouchpointType.DEMO_REQUEST, TouchpointType.SALES_CALL]:
                tp_type = touchpoint.touchpoint_type.value
                velocity_touchpoints[tp_type] = velocity_touchpoints.get(tp_type, 0) + 1
        
        print("🎯 High-Velocity Touchpoints:")
        for tp_type, count in velocity_touchpoints.items():
            print(f"   • {tp_type.replace('_', ' ').title()}: {count} instances")
        
        # Velocity recommendations
        velocity_recommendations = [
            "Increase demo requests to accelerate enterprise deals",
            "Focus on sales calls during evaluation stage",
            "Implement automated nurturing for mid-market deals",
            "Use webinars to speed up consideration phase"
        ]
        
        print("\n📋 Velocity Optimization Recommendations:")
        for i, rec in enumerate(velocity_recommendations, 1):
            print(f"   {i}. {rec}")
        
        return {
            'velocity_analysis': velocity_analysis,
            'high_velocity_touchpoints': velocity_touchpoints,
            'recommendations': velocity_recommendations
        }
    
    def demo_system_integration(self):
        """Demonstrate integration capabilities with existing systems."""
        print("🔗 System Integration Capabilities")
        print("   Seamless integration with existing marketing tech stack\n")
        
        # Simulate integration scenarios
        integrations = {
            'CRM (Salesforce/HubSpot)': {
                'data_sync': 'Lead scoring, opportunity data, sales activities',
                'frequency': 'Real-time via webhooks',
                'attribution_trigger': 'Opportunity close',
                'status': '✅ Supported'
            },
            'Marketing Automation': {
                'data_sync': 'Email engagement, campaign data, lead nurturing',
                'frequency': 'Hourly batch sync',
                'attribution_trigger': 'Campaign completion',
                'status': '✅ Supported'
            },
            'Web Analytics': {
                'data_sync': 'Website interactions, content engagement',
                'frequency': 'Real-time streaming',
                'attribution_trigger': 'Session end',
                'status': '✅ Supported'
            },
            'Customer Segmentation': {
                'data_sync': 'Segment classifications, behavioral data',
                'frequency': 'Daily batch',
                'attribution_trigger': 'Segment update',
                'status': '🔧 Your Existing App'
            }
        }
        
        for system, details in integrations.items():
            print(f"📱 {system} Integration:")
            print(f"   • Data Sync: {details['data_sync']}")
            print(f"   • Frequency: {details['frequency']}")
            print(f"   • Attribution Trigger: {details['attribution_trigger']}")
            print(f"   • Status: {details['status']}")
            print()
        
        # API endpoints demonstration
        print("🔌 API Integration Examples:")
        api_examples = [
            {
                'endpoint': 'POST /attribution/b2b/calculate',
                'purpose': 'Calculate attribution for specific accounts',
                'response_time': '< 2s for 1000 touchpoints'
            },
            {
                'endpoint': 'POST /attribution/b2b/channel-insights',
                'purpose': 'Get channel performance recommendations',
                'response_time': '< 1s for analysis'
            },
            {
                'endpoint': 'GET /attribution/b2b/model-info',
                'purpose': 'Retrieve model configuration and weights',
                'response_time': '< 100ms'
            }
        ]
        
        for api in api_examples:
            print(f"   • {api['endpoint']}")
            print(f"     - Purpose: {api['purpose']}")
            print(f"     - Performance: {api['response_time']}")
            print()
        
        # Data flow example
        print("📊 Sample Data Flow Integration:")
        flow_steps = [
            "1. CRM sends opportunity data via webhook",
            "2. Marketing automation provides touchpoint history",
            "3. Attribution engine calculates B2B attribution",
            "4. Results sent back to CRM for sales visibility",
            "5. Marketing dashboard updated with channel insights"
        ]
        
        for step in flow_steps:
            print(f"   {step}")
        
        return {
            'supported_integrations': list(integrations.keys()),
            'api_endpoints': len(api_examples),
            'integration_details': integrations
        }
    
    def demo_roi_impact(self):
        """Demonstrate ROI impact and business value."""
        print("💰 ROI Impact & Business Value Analysis")
        print("   Quantifying the business impact of B2B attribution insights\n")
        
        # Calculate current attribution insights
        attribution_results = self.attribution_engine.b2b_specific_attribution(
            lead_data=self.demo_data['leads'],
            opportunity_data=self.demo_data['opportunities'],
            touchpoint_data=self.demo_data['touchpoints']
        )
        
        channel_analysis = self.analyzer.analyze_channel_performance(
            attribution_results=attribution_results['combined_b2b_attribution'],
            touchpoint_data=self.demo_data['touchpoints']
        )
        
        # ROI calculations
        total_deal_value = sum(opp.amount for opp in self.demo_data['opportunities'])
        total_marketing_spend = sum(tp.cost for tp in self.demo_data['touchpoints'])
        total_attribution = sum(attribution_results['combined_b2b_attribution'].values())
        
        print("📊 Current Business Metrics:")
        print(f"   • Total Deal Value: ${total_deal_value:,.2f}")
        print(f"   • Marketing Investment: ${total_marketing_spend:,.2f}")
        print(f"   • Attribution Coverage: ${total_attribution:,.2f}")
        print(f"   • Attribution Rate: {(total_attribution/total_deal_value)*100:.1f}%")
        print()
        
        # Optimization potential
        optimization_scenarios = {
            'Channel Reallocation': {
                'description': 'Optimize budget allocation based on channel ROI',
                'potential_improvement': 15,
                'timeframe': '3-6 months',
                'confidence': 'High'
            },
            'Sales-Marketing Alignment': {
                'description': 'Improve collaboration based on attribution insights',
                'potential_improvement': 12,
                'timeframe': '6-12 months',
                'confidence': 'Medium-High'
            },
            'Pipeline Velocity': {
                'description': 'Accelerate deals using high-velocity touchpoints',
                'potential_improvement': 20,
                'timeframe': '6-18 months',
                'confidence': 'Medium'
            },
            'Lead Quality Focus': {
                'description': 'Prioritize high-quality leads and touchpoints',
                'potential_improvement': 25,
                'timeframe': '12+ months',
                'confidence': 'High'
            }
        }
        
        print("🚀 Optimization Opportunities:")
        total_potential_value = 0
        
        for scenario, details in optimization_scenarios.items():
            potential_value = total_deal_value * (details['potential_improvement'] / 100)
            total_potential_value += potential_value
            
            print(f"   • {scenario}:")
            print(f"     - {details['description']}")
            print(f"     - Potential Value: ${potential_value:,.2f} ({details['potential_improvement']}% improvement)")
            print(f"     - Timeframe: {details['timeframe']}")
            print(f"     - Confidence: {details['confidence']}")
            print()
        
        # ROI Summary
        annual_roi = ((total_potential_value * 0.3) - total_marketing_spend) / total_marketing_spend * 100
        
        print("💎 Annual ROI Projection:")
        print(f"   • Conservative Value Realization: ${total_potential_value * 0.3:,.2f}")
        print(f"   • Current Marketing Investment: ${total_marketing_spend:,.2f}")
        print(f"   • Projected Annual ROI: {annual_roi:,.1f}%")
        print(f"   • Payback Period: ~6-9 months")
        
        # Implementation roadmap
        print("\n🗺️ Implementation Roadmap:")
        roadmap = [
            "Month 1-2: Deploy B2B attribution platform",
            "Month 3-4: Integrate with existing systems",
            "Month 5-6: Begin channel optimization",
            "Month 7-12: Full attribution-driven optimization",
            "Month 12+: Advanced predictive analytics"
        ]
        
        for milestone in roadmap:
            print(f"   • {milestone}")
        
        return {
            'current_metrics': {
                'deal_value': total_deal_value,
                'marketing_spend': total_marketing_spend,
                'attribution_coverage': total_attribution
            },
            'optimization_potential': total_potential_value,
            'projected_roi': annual_roi,
            'scenarios': optimization_scenarios
        }
    
    def _generate_realistic_b2b_data(self):
        """Generate realistic B2B data for demonstration."""
        np.random.seed(42)  # For reproducible demo
        
        # Generate leads
        leads = []
        lead_id = 1
        for account_type in ['enterprise', 'mid-market', 'smb']:
            for i in range(3):  # 3 accounts per type
                account_id = f"account_{account_type}_{i+1}"
                
                for j in range(2):  # 2 leads per account
                    if account_type == 'enterprise':
                        lead_score = np.random.randint(70, 95)
                        quality_tier = 'A' if lead_score >= 85 else 'B'
                    elif account_type == 'mid-market':
                        lead_score = np.random.randint(50, 80)
                        quality_tier = 'B' if lead_score >= 65 else 'C'
                    else:  # SMB
                        lead_score = np.random.randint(30, 70)
                        quality_tier = 'C' if lead_score >= 50 else 'D'
                    
                    lead = LeadData(
                        lead_id=f"lead_{lead_id}",
                        account_id=account_id,
                        lead_score=lead_score,
                        demographic_score=np.random.randint(40, 90),
                        behavioral_score=np.random.randint(45, 95),
                        firmographic_score=np.random.randint(50, 90),
                        created_date=datetime.now() - timedelta(days=np.random.randint(30, 365)),
                        stage=np.random.choice(list(B2BStageType)),
                        source=np.random.choice(['organic_search', 'paid_search', 'referral', 'content']),
                        lead_quality_tier=quality_tier
                    )
                    leads.append(lead)
                    lead_id += 1
        
        # Generate opportunities
        opportunities = []
        opp_id = 1
        account_types = ['enterprise', 'mid-market', 'smb']
        
        for account_type in account_types:
            for i in range(3):
                account_id = f"account_{account_type}_{i+1}"
                account_leads = [l.lead_id for l in leads if l.account_id == account_id]
                
                if account_type == 'enterprise':
                    amount = np.random.randint(200000, 1000000)
                    cycle_days = np.random.randint(180, 400)
                    decision_makers = np.random.randint(3, 8)
                    influencers = np.random.randint(2, 6)
                elif account_type == 'mid-market':
                    amount = np.random.randint(50000, 250000)
                    cycle_days = np.random.randint(90, 200)
                    decision_makers = np.random.randint(2, 4)
                    influencers = np.random.randint(1, 3)
                else:  # SMB
                    amount = np.random.randint(5000, 60000)
                    cycle_days = np.random.randint(30, 90)
                    decision_makers = np.random.randint(1, 2)
                    influencers = np.random.randint(0, 2)
                
                opportunity = OpportunityData(
                    opportunity_id=f"opp_{opp_id}",
                    account_id=account_id,
                    lead_ids=account_leads,
                    stage="Closed Won",
                    probability=1.0,
                    amount=float(amount),
                    created_date=datetime.now() - timedelta(days=cycle_days + 30),
                    close_date=datetime.now() - timedelta(days=30),
                    sales_cycle_days=cycle_days,
                    deal_size_tier=account_type,
                    decision_makers_count=decision_makers,
                    influencers_count=influencers
                )
                opportunities.append(opportunity)
                opp_id += 1
        
        # Generate touchpoints
        touchpoints = []
        tp_id = 1
        
        touchpoint_types = [
            (TouchpointType.CONTENT_DOWNLOAD, ['content', 'website'], False, True),
            (TouchpointType.EMAIL_ENGAGEMENT, ['email'], False, True),
            (TouchpointType.WEBINAR_ATTENDANCE, ['webinar', 'events'], False, True),
            (TouchpointType.WEBSITE_VISIT, ['website', 'organic_search'], False, True),
            (TouchpointType.DEMO_REQUEST, ['website', 'sales'], True, True),
            (TouchpointType.SALES_CALL, ['phone', 'sales'], True, False),
            (TouchpointType.TRADE_SHOW, ['events'], False, True),
            (TouchpointType.SOCIAL_ENGAGEMENT, ['social'], False, True)
        ]
        
        for opportunity in opportunities:
            account_leads = [l for l in leads if l.account_id == opportunity.account_id]
            
            # Generate 8-15 touchpoints per opportunity
            num_touchpoints = np.random.randint(8, 16)
            
            for i in range(num_touchpoints):
                lead = np.random.choice(account_leads)
                tp_type, channels, is_sales, is_marketing = np.random.choice(touchpoint_types)
                channel = np.random.choice(channels)
                
                # Generate touchpoint within sales cycle
                days_before_close = np.random.randint(5, opportunity.sales_cycle_days)
                touchpoint_date = opportunity.close_date - timedelta(days=days_before_close)
                
                # Cost varies by touchpoint type
                if tp_type == TouchpointType.TRADE_SHOW:
                    cost = np.random.uniform(200, 800)
                elif tp_type == TouchpointType.WEBINAR_ATTENDANCE:
                    cost = np.random.uniform(50, 150)
                elif tp_type == TouchpointType.EMAIL_ENGAGEMENT:
                    cost = np.random.uniform(1, 10)
                elif tp_type in [TouchpointType.SALES_CALL, TouchpointType.DEMO_REQUEST]:
                    cost = 0  # Internal cost
                else:
                    cost = np.random.uniform(5, 100)
                
                touchpoint = TouchpointData(
                    touchpoint_id=f"tp_{tp_id}",
                    lead_id=lead.lead_id,
                    account_id=opportunity.account_id,
                    timestamp=touchpoint_date,
                    touchpoint_type=tp_type,
                    channel=channel,
                    campaign_id=f"campaign_{np.random.randint(1, 10)}" if is_marketing else None,
                    content_id=f"content_{np.random.randint(1, 20)}" if tp_type == TouchpointType.CONTENT_DOWNLOAD else None,
                    engagement_score=np.random.uniform(30, 95),
                    stage_influence=np.random.choice(list(B2BStageType)),
                    cost=cost,
                    is_sales_touch=is_sales,
                    is_marketing_touch=is_marketing,
                    sales_rep_id=f"rep_{np.random.randint(1, 10)}" if is_sales else None
                )
                touchpoints.append(touchpoint)
                tp_id += 1
        
        return {
            'leads': leads,
            'opportunities': opportunities,
            'touchpoints': touchpoints
        }
    
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
    
    def _generate_alignment_recommendations(self, alignment_data: Dict) -> List[str]:
        """Generate alignment recommendations."""
        recommendations = []
        
        sales_pct = alignment_data['sales_percentage']
        marketing_pct = alignment_data['marketing_percentage']
        joint_pct = alignment_data['joint_percentage']
        
        if sales_pct > 60:
            recommendations.append("Increase marketing's role in lead nurturing and qualification")
        if marketing_pct > 60:
            recommendations.append("Enhance sales engagement in marketing-qualified opportunities")
        if joint_pct < 15:
            recommendations.append("Implement more collaborative sales-marketing activities")
        if alignment_data['alignment_score'] < 70:
            recommendations.append("Establish joint planning sessions and shared KPIs")
        
        return recommendations
    
    def _generate_channel_insights(self, channel_analysis: Dict) -> List[str]:
        """Generate channel optimization insights."""
        insights = []
        
        # Sort by ROI
        sorted_channels = sorted(
            channel_analysis.items(),
            key=lambda x: x[1]['roi'],
            reverse=True
        )
        
        if sorted_channels:
            best_channel = sorted_channels[0]
            insights.append(f"Top performing channel: {best_channel[0]} with {best_channel[1]['roi']:.1f}x ROI")
        
        # Find high-cost, low-ROI channels
        for channel, metrics in channel_analysis.items():
            if metrics['total_cost'] > 1000 and metrics['roi'] < 1.0:
                insights.append(f"Optimize {channel} channel - high cost (${metrics['total_cost']:.0f}) with low ROI")
        
        return insights
    
    def _print_demo_summary(self, results: Dict):
        """Print final demo summary."""
        print("\n" + "=" * 80)
        print("🎯 B2B MARKETING ATTRIBUTION PLATFORM - DEMO SUMMARY")
        print("=" * 80)
        
        print("\n✅ Capabilities Demonstrated:")
        capabilities = [
            "B2B-specific attribution models for complex sales cycles",
            "Enterprise account analysis across deal sizes",
            "Sales-marketing alignment measurement and optimization",
            "Channel performance analysis with ROI insights",
            "Pipeline velocity tracking and acceleration",
            "System integration with existing marketing tech stack",
            "Quantified ROI impact and business value analysis"
        ]
        
        for capability in capabilities:
            print(f"   • {capability}")
        
        print("\n💰 Business Impact Summary:")
        if 'roi_impact_&_business_value' in results:
            roi_data = results['roi_impact_&_business_value']
            print(f"   • Total Deal Value Analyzed: ${roi_data['current_metrics']['deal_value']:,.2f}")
            print(f"   • Optimization Potential: ${roi_data['optimization_potential']:,.2f}")
            print(f"   • Projected Annual ROI: {roi_data['projected_roi']:,.1f}%")
        
        print("\n🚀 Next Steps:")
        next_steps = [
            "Schedule implementation planning session",
            "Define integration requirements with IT team",
            "Establish baseline metrics and KPIs",
            "Begin pilot program with selected accounts",
            "Plan full-scale deployment roadmap"
        ]
        
        for step in next_steps:
            print(f"   • {step}")
        
        print(f"\n📞 Ready to transform your B2B marketing attribution?")
        print(f"    Contact us to get started with your organization!")
        print("=" * 80)


def main():
    """Run the complete B2B Marketing Attribution Platform demo."""
    print("🚀 Starting B2B Marketing Attribution Platform Demo...")
    print("   This may take a moment to generate realistic B2B data...\n")
    
    try:
        # Initialize demo
        demo = B2BMarketingAttributionDemo()
        
        # Run complete demonstration
        results = demo.run_complete_demo()
        
        # Optional: Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"demo_results_{timestamp}.json", "w") as f:
            # Convert results to JSON-serializable format
            json_results = {}
            for key, value in results.items():
                try:
                    json.dumps(value)  # Test if serializable
                    json_results[key] = value
                except TypeError:
                    json_results[key] = str(value)  # Convert non-serializable to string
            
            json.dump(json_results, f, indent=2, default=str)
        
        print(f"\n📁 Demo results saved to: demo_results_{timestamp}.json")
        
    except Exception as e:
        print(f"❌ Demo error: {str(e)}")
        print("   Please ensure all dependencies are installed and services are running.")


if __name__ == "__main__":
    main()