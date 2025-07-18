#!/usr/bin/env python3
"""
Demo script for Market Segmentation Application
This script demonstrates the core functionality without the web interface.
"""

import pandas as pd
import numpy as np
from app import MarketSegmentationAnalyzer

def run_demo():
    print("🚀 Market Research Segmentation Demo")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = MarketSegmentationAnalyzer()
    
    # Load data
    print("\n📊 Loading customer data...")
    success = analyzer.load_data()
    
    if not success:
        print("❌ Failed to load data. Make sure customers.csv exists.")
        return
    
    print(f"✅ Data loaded successfully!")
    print(f"   - Shape: {analyzer.data.shape}")
    print(f"   - Features: {list(analyzer.feature_data.columns)}")
    
    # Get data summary
    print("\n📈 Data Summary:")
    summary = analyzer.get_data_summary()
    print(f"   - Total customers: {summary['shape'][0]}")
    print(f"   - Product categories: {len(analyzer.feature_data.columns)}")
    
    # Detect outliers
    print("\n🔍 Detecting outliers...")
    outliers = analyzer.detect_outliers()
    for feature, outlier_indices in outliers.items():
        print(f"   - {feature}: {len(outlier_indices)} outliers ({len(outlier_indices)/len(analyzer.data)*100:.1f}%)")
    
    # Feature relevance analysis
    print("\n⭐ Analyzing feature relevance...")
    relevance = analyzer.feature_relevance_analysis()
    print("   Feature predictability scores:")
    for feature, data in relevance.items():
        score = data['r2_score'] * 100
        quality = "High" if score > 70 else "Medium" if score > 40 else "Low"
        print(f"   - {feature}: {score:.1f}% ({quality})")
    
    # Find optimal clusters
    print("\n🎯 Finding optimal number of clusters...")
    optimal_info = analyzer.find_optimal_clusters(max_clusters=8)
    
    # Find the best k using silhouette score
    best_k_idx = np.argmax(optimal_info['silhouette_scores'])
    best_k = optimal_info['k_range'][best_k_idx]
    best_silhouette = optimal_info['silhouette_scores'][best_k_idx]
    
    print(f"   - Recommended clusters: {best_k}")
    print(f"   - Silhouette score: {best_silhouette:.3f}")
    
    # Perform clustering
    print(f"\n🔬 Performing K-Means clustering with {best_k} clusters...")
    cluster_data = analyzer.perform_clustering('kmeans', best_k)
    
    # Create segment profiles
    print("\n📋 Creating segment profiles...")
    profiles = analyzer.create_segment_profiles()
    
    print(f"\n📊 Segment Analysis Results:")
    print("=" * 50)
    
    for cluster_name, profile in profiles.items():
        cluster_num = cluster_name.split('_')[1]
        print(f"\n🏷️  SEGMENT {cluster_num}")
        print(f"   Size: {profile['size']} customers ({profile['percentage']:.1f}%)")
        
        print(f"   🌟 Top characteristics:")
        for i, (feature, ratio) in enumerate(profile['dominant_features'][:3], 1):
            print(f"      {i}. {feature}: {ratio:.2f}x average")
        
        print(f"   💰 Average spending:")
        for feature, value in profile['mean_values'].items():
            print(f"      - {feature}: {value:,.0f}")
        
        # Interpret the segment
        interpretation = interpret_segment(profile)
        print(f"   📝 Business interpretation: {interpretation}")
    
    print("\n" + "=" * 50)
    print("✅ Demo completed successfully!")
    print("💡 Run the full web application with: python app.py")

def interpret_segment(profile):
    """Provide business interpretation for a segment based on its characteristics."""
    dominant_features = [feature for feature, _ in profile['dominant_features'][:2]]
    
    if 'Fresh' in dominant_features and 'Frozen' in dominant_features:
        return "Restaurant/Food Service - High fresh and frozen product usage"
    elif 'Grocery' in dominant_features and 'Detergents_Paper' in dominant_features:
        return "Retail Store - Focus on packaged goods and cleaning supplies"
    elif 'Delicatessen' in dominant_features:
        return "Specialty/Gourmet - Premium delicatessen products"
    elif 'Milk' in dominant_features:
        return "Dairy-focused Business - High milk product consumption"
    else:
        return "General Customer - Balanced spending across categories"

if __name__ == "__main__":
    run_demo()