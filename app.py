import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
import seaborn as sns
from flask import Flask, render_template, request, jsonify, send_file
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, calinski_harabasz_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
import plotly.graph_objs as go
import plotly.express as px
import plotly.offline as pyo
import plotly.io as pio
import json
import io
import base64
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
app.secret_key = 'market_research_segmentation_key'

# Set up plotting style
try:
    plt.style.use('seaborn-v0_8')
except OSError:
    plt.style.use('seaborn')
sns.set_palette("husl")

class MarketSegmentationAnalyzer:
    def __init__(self, data_path='customers.csv'):
        self.data_path = data_path
        self.data = None
        self.scaled_data = None
        self.scaler = None
        self.pca = None
        self.clusters = None
        self.segment_profiles = None
        
    def load_data(self):
        """Load and preprocess the customer data"""
        try:
            self.data = pd.read_csv(self.data_path)
            # Remove Channel and Region for analysis
            self.feature_data = self.data.drop(['Channel', 'Region'], axis=1, errors='ignore')
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def get_data_summary(self):
        """Get comprehensive data summary"""
        if self.data is None:
            return None
            
        summary = {
            'shape': self.data.shape,
            'columns': list(self.data.columns),
            'missing_values': self.data.isnull().sum().to_dict(),
            'data_types': self.data.dtypes.to_dict(),
            'basic_stats': self.feature_data.describe().to_dict(),
            'correlation_matrix': self.feature_data.corr().to_dict()
        }
        return summary
    
    def detect_outliers(self, method='iqr'):
        """Detect outliers using IQR or Z-score method"""
        outliers = {}
        
        for column in self.feature_data.columns:
            if method == 'iqr':
                Q1 = self.feature_data[column].quantile(0.25)
                Q3 = self.feature_data[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outlier_indices = self.feature_data[
                    (self.feature_data[column] < lower_bound) | 
                    (self.feature_data[column] > upper_bound)
                ].index.tolist()
            else:  # z-score
                z_scores = np.abs((self.feature_data[column] - self.feature_data[column].mean()) / self.feature_data[column].std())
                outlier_indices = self.feature_data[z_scores > 3].index.tolist()
            
            outliers[column] = outlier_indices
        
        return outliers
    
    def feature_relevance_analysis(self):
        """Analyze feature relevance using random forest"""
        relevance_scores = {}
        
        for feature in self.feature_data.columns:
            # Prepare data
            X = self.feature_data.drop(feature, axis=1)
            y = self.feature_data[feature]
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
            
            # Train model
            rf = RandomForestRegressor(n_estimators=100, random_state=42)
            rf.fit(X_train, y_train)
            
            # Predict and score
            y_pred = rf.predict(X_test)
            score = r2_score(y_test, y_pred)
            
            relevance_scores[feature] = {
                'r2_score': score,
                'feature_importance': dict(zip(X.columns, rf.feature_importances_))
            }
        
        return relevance_scores
    
    def scale_data(self, method='standard'):
        """Scale the feature data"""
        if method == 'standard':
            self.scaler = StandardScaler()
        else:
            self.scaler = RobustScaler()
        
        self.scaled_data = self.scaler.fit_transform(self.feature_data)
        return self.scaled_data
    
    def apply_pca(self, n_components=2):
        """Apply PCA for dimensionality reduction"""
        if self.scaled_data is None:
            self.scale_data()
        
        self.pca = PCA(n_components=n_components)
        pca_data = self.pca.fit_transform(self.scaled_data)
        
        # Create PCA results summary
        pca_results = {
            'explained_variance_ratio': self.pca.explained_variance_ratio_.tolist(),
            'cumulative_variance': np.cumsum(self.pca.explained_variance_ratio_).tolist(),
            'components': self.pca.components_.tolist(),
            'feature_names': list(self.feature_data.columns)
        }
        
        return pca_data, pca_results
    
    def find_optimal_clusters(self, max_clusters=10):
        """Find optimal number of clusters using elbow method and silhouette analysis"""
        if self.scaled_data is None:
            self.scale_data()
        
        inertias = []
        silhouette_scores = []
        calinski_scores = []
        k_range = range(2, max_clusters + 1)
        
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(self.scaled_data)
            
            inertias.append(kmeans.inertia_)
            silhouette_scores.append(silhouette_score(self.scaled_data, cluster_labels))
            calinski_scores.append(calinski_harabasz_score(self.scaled_data, cluster_labels))
        
        return {
            'k_range': list(k_range),
            'inertias': inertias,
            'silhouette_scores': silhouette_scores,
            'calinski_scores': calinski_scores
        }
    
    def perform_clustering(self, algorithm='kmeans', n_clusters=3, **kwargs):
        """Perform clustering using specified algorithm"""
        if self.scaled_data is None:
            self.scale_data()
        
        if algorithm == 'kmeans':
            clusterer = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        elif algorithm == 'dbscan':
            eps = kwargs.get('eps', 0.5)
            min_samples = kwargs.get('min_samples', 5)
            clusterer = DBSCAN(eps=eps, min_samples=min_samples)
        elif algorithm == 'hierarchical':
            clusterer = AgglomerativeClustering(n_clusters=n_clusters)
        
        self.clusters = clusterer.fit_predict(self.scaled_data)
        
        # Add cluster labels to original data
        cluster_data = self.feature_data.copy()
        cluster_data['Cluster'] = self.clusters
        
        return cluster_data
    
    def create_segment_profiles(self):
        """Create detailed profiles for each segment"""
        if self.clusters is None:
            return None
        
        cluster_data = self.feature_data.copy()
        cluster_data['Cluster'] = self.clusters
        
        profiles = {}
        unique_clusters = np.unique(self.clusters)
        
        for cluster in unique_clusters:
            if cluster == -1:  # DBSCAN noise points
                continue
                
            cluster_subset = cluster_data[cluster_data['Cluster'] == cluster]
            
            profile = {
                'size': len(cluster_subset),
                'percentage': len(cluster_subset) / len(cluster_data) * 100,
                'mean_values': cluster_subset.drop('Cluster', axis=1).mean().to_dict(),
                'median_values': cluster_subset.drop('Cluster', axis=1).median().to_dict(),
                'std_values': cluster_subset.drop('Cluster', axis=1).std().to_dict()
            }
            
            # Identify dominant characteristics
            overall_means = self.feature_data.mean()
            cluster_means = cluster_subset.drop('Cluster', axis=1).mean()
            
            # Calculate relative importance (how much above/below average)
            relative_importance = {}
            for feature in self.feature_data.columns:
                ratio = cluster_means[feature] / overall_means[feature]
                relative_importance[feature] = ratio
            
            profile['relative_importance'] = relative_importance
            profile['dominant_features'] = sorted(relative_importance.items(), 
                                                key=lambda x: x[1], reverse=True)[:3]
            
            profiles[f'Cluster_{cluster}'] = profile
        
        self.segment_profiles = profiles
        return profiles

# Initialize analyzer
analyzer = MarketSegmentationAnalyzer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/load_data', methods=['POST'])
def load_data():
    success = analyzer.load_data()
    if success:
        summary = analyzer.get_data_summary()
        return jsonify({'success': True, 'data_summary': summary})
    else:
        return jsonify({'success': False, 'error': 'Failed to load data'})

@app.route('/api/data_exploration')
def data_exploration():
    if analyzer.data is None:
        return jsonify({'error': 'Data not loaded'})
    
    # Get data summary
    summary = analyzer.get_data_summary()
    
    # Detect outliers
    outliers = analyzer.detect_outliers()
    
    # Feature relevance analysis
    relevance = analyzer.feature_relevance_analysis()
    
    return jsonify({
        'summary': summary,
        'outliers': outliers,
        'feature_relevance': relevance
    })

@app.route('/api/clustering_analysis', methods=['POST'])
def clustering_analysis():
    if analyzer.data is None:
        return jsonify({'error': 'Data not loaded'})
    
    data = request.json
    algorithm = data.get('algorithm', 'kmeans')
    n_clusters = data.get('n_clusters', 3)
    
    # Find optimal clusters if requested
    if data.get('find_optimal', False):
        optimal_info = analyzer.find_optimal_clusters()
    else:
        optimal_info = None
    
    # Perform clustering
    cluster_data = analyzer.perform_clustering(algorithm, n_clusters)
    
    # Create segment profiles
    profiles = analyzer.create_segment_profiles()
    
    # Apply PCA for visualization
    pca_data, pca_results = analyzer.apply_pca(n_components=2)
    
    return jsonify({
        'cluster_data': cluster_data.to_dict('records'),
        'segment_profiles': profiles,
        'pca_results': pca_results,
        'pca_data': pca_data.tolist(),
        'optimal_clusters': optimal_info
    })

@app.route('/api/visualizations/<viz_type>')
def generate_visualization(viz_type):
    if analyzer.data is None:
        return jsonify({'error': 'Data not loaded'})
    
    try:
        if viz_type == 'correlation_heatmap':
            fig = px.imshow(analyzer.feature_data.corr(), 
                          title='Feature Correlation Heatmap',
                          color_continuous_scale='RdBu_r')
        
        elif viz_type == 'feature_distributions':
            fig = px.box(analyzer.feature_data.melt(), 
                        x='variable', y='value',
                        title='Feature Distributions')
        
        elif viz_type == 'pca_scatter' and analyzer.clusters is not None:
            pca_data, _ = analyzer.apply_pca(n_components=2)
            df_plot = pd.DataFrame(pca_data, columns=['PC1', 'PC2'])
            df_plot['Cluster'] = analyzer.clusters
            
            fig = px.scatter(df_plot, x='PC1', y='PC2', color='Cluster',
                           title='Customer Segments in PCA Space')
        
        elif viz_type == 'cluster_profiles' and analyzer.segment_profiles is not None:
            # Create radar chart for cluster profiles
            categories = list(analyzer.feature_data.columns)
            
            fig = go.Figure()
            
            for cluster_name, profile in analyzer.segment_profiles.items():
                values = [profile['relative_importance'][cat] for cat in categories]
                values.append(values[0])  # Close the radar chart
                categories_closed = categories + [categories[0]]
                
                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=categories_closed,
                    fill='toself',
                    name=cluster_name
                ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True)
                ),
                title="Segment Profiles Radar Chart"
            )
        
        else:
            return jsonify({'error': 'Visualization type not supported or data not ready'})
        
        graphJSON = pio.to_json(fig)
        return jsonify({'plot': graphJSON})
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/export_results')
def export_results():
    if analyzer.segment_profiles is None:
        return jsonify({'error': 'No analysis results to export'})
    
    # Create comprehensive report
    report = {
        'timestamp': datetime.now().isoformat(),
        'data_summary': analyzer.get_data_summary(),
        'segment_profiles': analyzer.segment_profiles,
        'clustering_algorithm': 'kmeans',  # Default for this export
        'number_of_segments': len(analyzer.segment_profiles)
    }
    
    return jsonify(report)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)