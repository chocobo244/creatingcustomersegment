// Market Research Segmentation Application JavaScript

class MarketSegmentationApp {
    constructor() {
        this.currentData = null;
        this.currentSegments = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.setupTooltips();
    }

    bindEvents() {
        // Data loading
        document.getElementById('loadDataBtn').addEventListener('click', () => this.loadData());
        
        // Analysis
        document.getElementById('runAnalysisBtn').addEventListener('click', () => this.runAnalysis());
        
        // Clustering
        document.getElementById('clusteringForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.runClustering();
        });
        
        // Algorithm change handler
        document.getElementById('algorithmSelect').addEventListener('change', (e) => {
            this.handleAlgorithmChange(e.target.value);
        });
        
        // Export results
        document.getElementById('exportResultsBtn').addEventListener('click', () => this.exportResults());
        
        // Navigation
        this.setupSmoothScrolling();
    }

    setupTooltips() {
        // Initialize Bootstrap tooltips if needed
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    setupSmoothScrolling() {
        // Smooth scrolling for navigation links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    showLoading() {
        document.getElementById('loadingSpinner').style.display = 'block';
    }

    hideLoading() {
        document.getElementById('loadingSpinner').style.display = 'none';
    }

    showSection(sectionId) {
        document.getElementById(sectionId).style.display = 'block';
        document.getElementById(sectionId).classList.add('fade-in');
    }

    hideSection(sectionId) {
        document.getElementById(sectionId).style.display = 'none';
    }

    async loadData() {
        this.showLoading();
        
        try {
            const response = await fetch('/api/load_data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.currentData = result.data_summary;
                this.displayDataOverview(result.data_summary);
                this.loadInitialVisualizations();
                this.showSection('data-overview');
                this.showSection('analysis');
                this.showSection('segmentation');
                
                // Show success message
                this.showAlert('Data loaded successfully!', 'success');
            } else {
                this.showAlert('Failed to load data: ' + result.error, 'error');
            }
        } catch (error) {
            console.error('Error loading data:', error);
            this.showAlert('Error loading data: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    displayDataOverview(dataSummary) {
        // Update stats cards
        document.getElementById('totalCustomers').textContent = dataSummary.shape[0];
        document.getElementById('totalFeatures').textContent = dataSummary.shape[1] - 2; // Excluding Channel and Region
        
        const totalMissing = Object.values(dataSummary.missing_values).reduce((sum, val) => sum + val, 0);
        document.getElementById('missingValues').textContent = totalMissing;
        
        // Calculate data quality score
        const qualityScore = totalMissing === 0 ? 'Excellent' : totalMissing < 10 ? 'Good' : 'Fair';
        document.getElementById('dataQuality').textContent = qualityScore;
    }

    async loadInitialVisualizations() {
        try {
            // Load distribution plot
            const distResponse = await fetch('/api/visualizations/feature_distributions');
            const distResult = await distResponse.json();
            
            if (!distResult.error) {
                Plotly.newPlot('distributionPlot', JSON.parse(distResult.plot).data, 
                              JSON.parse(distResult.plot).layout, {responsive: true});
            }
            
            // Load correlation heatmap
            const corrResponse = await fetch('/api/visualizations/correlation_heatmap');
            const corrResult = await corrResponse.json();
            
            if (!corrResult.error) {
                Plotly.newPlot('correlationPlot', JSON.parse(corrResult.plot).data, 
                              JSON.parse(corrResult.plot).layout, {responsive: true});
            }
        } catch (error) {
            console.error('Error loading visualizations:', error);
        }
    }

    async runAnalysis() {
        this.showLoading();
        
        try {
            const response = await fetch('/api/data_exploration');
            const result = await response.json();
            
            if (!result.error) {
                this.displayAnalysisResults(result);
                this.showAlert('Analysis completed successfully!', 'success');
            } else {
                this.showAlert('Analysis failed: ' + result.error, 'error');
            }
        } catch (error) {
            console.error('Error running analysis:', error);
            this.showAlert('Error running analysis: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    displayAnalysisResults(results) {
        // Display outlier results
        this.displayOutlierResults(results.outliers);
        
        // Display feature relevance
        this.displayFeatureRelevance(results.feature_relevance);
        
        // Display general analysis results
        this.displayGeneralResults(results.summary);
    }

    displayOutlierResults(outliers) {
        const container = document.getElementById('outlierResults');
        let html = '<div class="table-responsive"><table class="table table-striped">';
        html += '<thead><tr><th>Feature</th><th>Outliers Count</th><th>Percentage</th></tr></thead><tbody>';
        
        for (const [feature, outlierIndices] of Object.entries(outliers)) {
            const count = outlierIndices.length;
            const percentage = ((count / this.currentData.shape[0]) * 100).toFixed(2);
            html += `<tr><td><strong>${feature}</strong></td><td>${count}</td><td>${percentage}%</td></tr>`;
        }
        
        html += '</tbody></table></div>';
        container.innerHTML = html;
    }

    displayFeatureRelevance(relevance) {
        const container = document.getElementById('relevanceResults');
        let html = '<div class="table-responsive"><table class="table table-striped">';
        html += '<thead><tr><th>Feature</th><th>Predictability Score</th><th>Quality</th></tr></thead><tbody>';
        
        for (const [feature, data] of Object.entries(relevance)) {
            const score = (data.r2_score * 100).toFixed(2);
            const quality = data.r2_score > 0.7 ? 'High' : data.r2_score > 0.4 ? 'Medium' : 'Low';
            const qualityClass = data.r2_score > 0.7 ? 'text-success' : data.r2_score > 0.4 ? 'text-warning' : 'text-danger';
            
            html += `<tr><td><strong>${feature}</strong></td><td>${score}%</td><td class="${qualityClass}">${quality}</td></tr>`;
        }
        
        html += '</tbody></table></div>';
        container.innerHTML = html;
    }

    displayGeneralResults(summary) {
        const container = document.getElementById('analysisResults');
        
        let html = '<div class="alert alert-info">';
        html += '<h5><i class="fas fa-info-circle me-2"></i>Data Summary</h5>';
        html += `<p><strong>Dataset Shape:</strong> ${summary.shape[0]} customers × ${summary.shape[1]} features</p>`;
        html += '<p><strong>Product Categories:</strong> Fresh, Milk, Grocery, Frozen, Detergents_Paper, Delicatessen</p>';
        html += '</div>';
        
        container.innerHTML = html;
    }

    handleAlgorithmChange(algorithm) {
        const nClustersGroup = document.getElementById('nClustersGroup');
        
        if (algorithm === 'dbscan') {
            nClustersGroup.style.display = 'none';
        } else {
            nClustersGroup.style.display = 'block';
        }
    }

    async runClustering() {
        this.showLoading();
        
        const algorithm = document.getElementById('algorithmSelect').value;
        const nClusters = parseInt(document.getElementById('nClusters').value);
        const findOptimal = document.getElementById('findOptimal').checked;
        
        try {
            const response = await fetch('/api/clustering_analysis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    algorithm: algorithm,
                    n_clusters: nClusters,
                    find_optimal: findOptimal
                })
            });
            
            const result = await response.json();
            
            if (!result.error) {
                this.currentSegments = result.segment_profiles;
                this.displayClusteringResults(result);
                this.showSection('insights');
                this.showAlert('Segmentation completed successfully!', 'success');
            } else {
                this.showAlert('Segmentation failed: ' + result.error, 'error');
            }
        } catch (error) {
            console.error('Error running clustering:', error);
            this.showAlert('Error running clustering: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    async displayClusteringResults(results) {
        // Display PCA scatter plot
        if (results.pca_data && results.cluster_data) {
            await this.createPCAScatterPlot(results.pca_data, results.cluster_data);
        }
        
        // Display optimal clusters analysis if available
        if (results.optimal_clusters) {
            this.displayOptimalClustersAnalysis(results.optimal_clusters);
            document.getElementById('optimalClustersSection').style.display = 'block';
        }
        
        // Display segment insights
        if (results.segment_profiles) {
            await this.displaySegmentInsights(results.segment_profiles);
        }
    }

    async createPCAScatterPlot(pcaData, clusterData) {
        try {
            const response = await fetch('/api/visualizations/pca_scatter');
            const result = await response.json();
            
            if (!result.error) {
                Plotly.newPlot('segmentationPlot', JSON.parse(result.plot).data, 
                              JSON.parse(result.plot).layout, {responsive: true});
            }
        } catch (error) {
            console.error('Error creating PCA plot:', error);
        }
    }

    displayOptimalClustersAnalysis(optimalData) {
        const trace1 = {
            x: optimalData.k_range,
            y: optimalData.inertias,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Inertia (Elbow Method)',
            line: {color: '#3498db', width: 3},
            marker: {size: 8}
        };
        
        const trace2 = {
            x: optimalData.k_range,
            y: optimalData.silhouette_scores,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Silhouette Score',
            yaxis: 'y2',
            line: {color: '#e74c3c', width: 3},
            marker: {size: 8}
        };
        
        const layout = {
            title: 'Optimal Number of Clusters Analysis',
            xaxis: {title: 'Number of Clusters'},
            yaxis: {title: 'Inertia'},
            yaxis2: {
                title: 'Silhouette Score',
                overlaying: 'y',
                side: 'right'
            },
            hovermode: 'x unified'
        };
        
        Plotly.newPlot('optimalClustersPlot', [trace1, trace2], layout, {responsive: true});
    }

    async displaySegmentInsights(segmentProfiles) {
        // Create radar chart
        await this.createRadarChart(segmentProfiles);
        
        // Create segment distribution pie chart
        this.createSegmentDistribution(segmentProfiles);
        
        // Create detailed segment cards
        this.createSegmentDetailCards(segmentProfiles);
    }

    async createRadarChart(segmentProfiles) {
        try {
            const response = await fetch('/api/visualizations/cluster_profiles');
            const result = await response.json();
            
            if (!result.error) {
                Plotly.newPlot('radarPlot', JSON.parse(result.plot).data, 
                              JSON.parse(result.plot).layout, {responsive: true});
            }
        } catch (error) {
            console.error('Error creating radar chart:', error);
        }
    }

    createSegmentDistribution(segmentProfiles) {
        const labels = Object.keys(segmentProfiles);
        const sizes = Object.values(segmentProfiles).map(profile => profile.size);
        const colors = ['#3498db', '#e74c3c', '#27ae60', '#f39c12', '#9b59b6', '#1abc9c'];
        
        const trace = {
            labels: labels,
            values: sizes,
            type: 'pie',
            marker: {colors: colors.slice(0, labels.length)},
            hovertemplate: '<b>%{label}</b><br>' +
                          'Size: %{value}<br>' +
                          'Percentage: %{percent}<br>' +
                          '<extra></extra>'
        };
        
        const layout = {
            title: 'Segment Size Distribution',
            showlegend: true
        };
        
        Plotly.newPlot('segmentDistribution', [trace], layout, {responsive: true});
    }

    createSegmentDetailCards(segmentProfiles) {
        const container = document.getElementById('segmentDetailsSection');
        let html = '';
        
        Object.entries(segmentProfiles).forEach(([clusterName, profile], index) => {
            const clusterNumber = index + 1;
            const icon = ['fas fa-store', 'fas fa-utensils', 'fas fa-shopping-cart'][index] || 'fas fa-users';
            
            html += `
                <div class="col-lg-4 col-md-6 mb-4">
                    <div class="segment-card scale-in">
                        <div class="segment-header">
                            <div class="segment-icon">
                                <i class="${icon}"></i>
                            </div>
                            <div>
                                <h5 class="segment-title">Segment ${clusterNumber}</h5>
                                <p class="segment-size">${profile.size} customers (${profile.percentage.toFixed(1)}%)</p>
                            </div>
                        </div>
                        
                        <h6><i class="fas fa-star me-2"></i>Key Characteristics</h6>
                        <div class="mb-3">
                            ${profile.dominant_features.map(([feature, value]) => `
                                <div class="feature-bar">
                                    <span class="feature-name">${feature}</span>
                                    <div class="feature-progress">
                                        <div class="feature-progress-bar" style="width: ${Math.min(value * 50, 100)}%"></div>
                                    </div>
                                    <span class="feature-value">${value.toFixed(2)}x</span>
                                </div>
                            `).join('')}
                        </div>
                        
                        <h6><i class="fas fa-chart-bar me-2"></i>Average Spending</h6>
                        <div class="small">
                            ${Object.entries(profile.mean_values).map(([feature, value]) => `
                                <div class="d-flex justify-content-between mb-1">
                                    <span>${feature}:</span>
                                    <strong>${Math.round(value).toLocaleString()}</strong>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
    }

    async exportResults() {
        try {
            const response = await fetch('/api/export_results');
            const result = await response.json();
            
            if (!result.error) {
                // Create and download JSON file
                const dataStr = JSON.stringify(result, null, 2);
                const dataBlob = new Blob([dataStr], {type: 'application/json'});
                const url = URL.createObjectURL(dataBlob);
                
                const link = document.createElement('a');
                link.href = url;
                link.download = `market_segmentation_results_${new Date().toISOString().split('T')[0]}.json`;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                URL.revokeObjectURL(url);
                
                this.showAlert('Results exported successfully!', 'success');
            } else {
                this.showAlert('Export failed: ' + result.error, 'error');
            }
        } catch (error) {
            console.error('Error exporting results:', error);
            this.showAlert('Error exporting results: ' + error.message, 'error');
        }
    }

    showAlert(message, type = 'info') {
        // Create alert element
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert at the top of the container
        const container = document.querySelector('.container-fluid');
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const app = new MarketSegmentationApp();
});

// Additional utility functions
function formatNumber(num) {
    return new Intl.NumberFormat().format(Math.round(num));
}

function formatPercentage(num) {
    return (num * 100).toFixed(1) + '%';
}

function getColorByIndex(index) {
    const colors = ['#3498db', '#e74c3c', '#27ae60', '#f39c12', '#9b59b6', '#1abc9c'];
    return colors[index % colors.length];
}