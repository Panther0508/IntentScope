"""
Advanced AI Analytics Module for IntentScope
Includes: Anomaly Detection, Churn Prediction, User Segmentation, A/B Testing
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
import warnings
warnings.filterwarnings('ignore')


class AnomalyDetector:
    """
    Detects anomalous user behavior using Isolation Forest and statistical methods.
    """
    
    def __init__(self, contamination=0.1, random_state=42):
        self.contamination = contamination
        self.random_state = random_state
        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        self.is_fitted = False
        
    def fit(self, features_df, feature_columns):
        """Fit the anomaly detection model"""
        X = features_df[feature_columns].fillna(0).values
        X_scaled = self.scaler.fit_transform(X)
        
        self.model.fit(X_scaled)
        self.is_fitted = True
        
        return self
    
    def predict(self, features_df, feature_columns):
        """Predict anomalies (-1 for anomaly, 1 for normal)"""
        if not self.is_fitted:
            raise ValueError("Model not fitted yet!")
            
        X = features_df[feature_columns].fillna(0).values
        X_scaled = self.scaler.transform(X)
        
        predictions = self.model.predict(X_scaled)
        scores = self.model.decision_function(X_scaled)
        
        return predictions, scores
    
    def get_anomaly_profiles(self, features_df, predictions, scores):
        """Get detailed profiles of anomalous users"""
        features_df = features_df.copy()
        features_df['anomaly_label'] = predictions
        features_df['anomaly_score'] = scores
        
        anomalies = features_df[features_df['anomaly_label'] == -1]
        
        return {
            'total_anomalies': len(anomalies),
            'anomaly_percentage': len(anomalies) / len(features_df) * 100,
            'anomaly_profiles': anomalies.describe(),
            'common_characteristics': self._analyze_anomaly_patterns(anomalies)
        }
    
    def _analyze_anomaly_patterns(self, anomalies_df):
        """Analyze common patterns in anomalous behavior"""
        patterns = []
        
        if len(anomalies_df) > 0:
            if 'total_interactions' in anomalies_df.columns:
                if anomalies_df['total_interactions'].mean() < 3:
                    patterns.append("Very low interaction count")
            if 'success_rate' in anomalies_df.columns:
                if anomalies_df['success_rate'].mean() < 0.3:
                    patterns.append("Low success rate")
            if 'session_duration_mean' in anomalies_df.columns:
                if anomalies_df['session_duration_mean'].mean() > 30:
                    patterns.append("Unusually long sessions")
                    
        return patterns if patterns else ["Unusual behavior patterns detected"]


class ChurnPredictor:
    """
    Predicts user churn probability using ensemble methods.
    """
    
    def __init__(self, threshold=0.5, random_state=42):
        self.threshold = threshold
        self.random_state = random_state
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=random_state
        )
        self.scaler = StandardScaler()
        self.is_fitted = False
        
    def create_churn_labels(self, user_behavior_df, days_inactive=30):
        """
        Create churn labels based on inactivity.
        Users inactive for more than 'days_inactive' are labeled as churned.
        """
        df = user_behavior_df.copy()
        df['last_activity'] = df.groupby('user_id')['timestamp'].transform('max')
        
        reference_date = df['timestamp'].max()
        df['days_inactive'] = (reference_date - df['last_activity']).dt.days
        
        # Aggregate to user level
        user_churn = df.groupby('user_id').agg({
            'days_inactive': 'first',
            'action': 'count'
        }).reset_index()
        
        user_churn['churned'] = (user_churn['days_inactive'] > days_inactive).astype(int)
        
        return user_churn
    
    def fit(self, features_df, labels_df, feature_columns):
        """Train the churn prediction model"""
        X = features_df[feature_columns].fillna(0).values
        X_scaled = self.scaler.fit_transform(X)
        
        # Merge with labels
        merged = features_df.merge(labels_df[['user_id', 'churned']], on='user_id', how='left')
        y = merged['churned'].fillna(0).values
        
        self.model.fit(X_scaled, y)
        self.is_fitted = True
        
        return self
    
    def predict_churn_probability(self, features_df, feature_columns):
        """Predict churn probability for each user"""
        if not self.is_fitted:
            raise ValueError("Model not fitted yet!")
            
        X = features_df[feature_columns].fillna(0).values
        X_scaled = self.scaler.transform(X)
        
        churn_probability = self.model.predict_proba(X_scaled)[:, 1]
        churn_prediction = (churn_probability > self.threshold).astype(int)
        
        return churn_probability, churn_prediction
    
    def get_risk_segments(self, features_df, churn_probability):
        """Segment users by churn risk level"""
        features_df = features_df.copy()
        features_df['churn_probability'] = churn_probability
        
        def categorize_risk(prob):
            if prob >= 0.7:
                return 'High Risk'
            elif prob >= 0.4:
                return 'Medium Risk'
            else:
                return 'Low Risk'
        
        features_df['risk_segment'] = features_df['churn_probability'].apply(categorize_risk)
        
        risk_distribution = features_df['risk_segment'].value_counts()
        
        return features_df, risk_distribution


class UserSegmenter:
    """
    Segments users using K-Means and DBSCAN clustering algorithms.
    """
    
    def __init__(self, n_clusters=5, method='kmeans', random_state=42):
        self.n_clusters = n_clusters
        self.method = method
        self.random_state = random_state
        
        if method == 'kmeans':
            self.model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
        elif method == 'dbscan':
            self.model = DBSCAN(eps=0.5, min_samples=5)
        else:
            raise ValueError("Method must be 'kmeans' or 'dbscan'")
            
        self.scaler = StandardScaler()
        
    def fit_segment(self, features_df, feature_columns):
        """Fit the segmentation model and assign segments"""
        X = features_df[feature_columns].fillna(0).values
        X_scaled = self.scaler.fit_transform(X)
        
        # Fit the model
        segments = self.model.fit_predict(X_scaled)
        
        # Evaluate clustering
        if self.method == 'kmeans' and len(np.unique(segments)) > 1:
            metrics = {
                'silhouette_score': silhouette_score(X_scaled, segments),
                'calinski_harabasz_score': calinski_harabasz_score(X_scaled, segments),
                'davies_bouldin_score': davies_bouldin_score(X_scaled, segments)
            }
        else:
            metrics = {}
        
        # Add segment labels to features
        features_df = features_df.copy()
        features_df['segment'] = segments
        
        # Create segment profiles
        segment_profiles = features_df.groupby('segment')[feature_columns].mean()
        
        return features_df, segment_profiles, metrics
    
    def get_segment_characteristics(self, segment_profiles):
        """Analyze and describe each segment"""
        characteristics = {}
        
        for segment in segment_profiles.index:
            profile = segment_profiles.loc[segment]
            
            # Determine segment type based on feature patterns
            traits = []
            
            if 'total_interactions' in profile.index:
                if profile['total_interactions'] > segment_profiles['total_interactions'].mean():
                    traits.append('High Activity')
                else:
                    traits.append('Low Activity')
                    
            if 'success_rate' in profile.index:
                if profile['success_rate'] > segment_profiles['success_rate'].mean():
                    traits.append('High Success')
                else:
                    traits.append('Learning')
                    
            if 'session_duration_mean' in profile.index:
                if profile['session_duration_mean'] > segment_profiles['session_duration_mean'].mean():
                    traits.append('Long Sessions')
                else:
                    traits.append('Quick Sessions')
            
            characteristics[f'Segment_{segment}'] = {
                'traits': traits,
                'size': 'Medium',
                'recommended_actions': self._get_segment_recommendations(traits)
            }
            
        return characteristics
    
    def _get_segment_recommendations(self, traits):
        """Get recommended actions based on segment traits"""
        recommendations = []
        
        if 'High Activity' in traits and 'High Success' in traits:
            recommendations.append('Nurture as power users')
            recommendations.append('Offer advanced features')
        elif 'Low Activity' in traits:
            recommendations.append('Send re-engagement campaigns')
            recommendations.append('Simplify onboarding')
        elif 'Learning' in traits:
            recommendations.append('Provide tutorials')
            recommendations.append('Offer guided workflows')
            
        return recommendations


class ABTestEngine:
    """
    A/B testing framework for experimenting with recommendation strategies.
    """
    
    def __init__(self, confidence_level=0.95):
        self.confidence_level = confidence_level
        self.experiments = {}
        
    def create_experiment(self, experiment_id, variants, metric_name):
        """Create a new A/B test experiment"""
        self.experiments[experiment_id] = {
            'variants': variants,  # e.g., {'control': [], 'treatment_a': [], 'treatment_b': []}
            'metric_name': metric_name,
            'results': {}
        }
        
    def add_observations(self, experiment_id, variant, observations):
        """Add observations to a specific variant"""
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found!")
            
        self.experiments[experiment_id]['variants'][variant].extend(observations)
        
    def calculate_statistics(self, experiment_id):
        """Calculate statistical significance for the experiment"""
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found!")
            
        variants = self.experiments[experiment_id]['variants']
        
        results = {}
        for variant_name, observations in variants.items():
            if len(observations) > 0:
                results[variant_name] = {
                    'n': len(observations),
                    'mean': np.mean(observations),
                    'std': np.std(observations),
                    'sem': np.std(observations) / np.sqrt(len(observations))
                }
                
        # Calculate confidence intervals
        for variant_name in results:
            mean = results[variant_name]['mean']
            sem = results[variant_name]['sem']
            n = results[variant_name]['n']
            
            # 95% CI
            ci = 1.96 * sem
            results[variant_name]['ci_lower'] = mean - ci
            results[variant_name]['ci_upper'] = mean + ci
            
        self.experiments[experiment_id]['results'] = results
        
        return results
    
    def determine_winner(self, experiment_id):
        """Determine the winning variant based on statistical significance"""
        results = self.experiments[experiment_id].get('results', {})
        
        if len(results) < 2:
            return None, "Insufficient data"
            
        # Find variant with highest mean
        best_variant = max(results.keys(), key=lambda x: results[x]['mean'])
        best_mean = results[best_variant]['mean']
        
        # Check if statistically significant compared to control
        control_results = results.get('control', None)
        
        if control_results is None:
            return best_variant, "No control group for comparison"
            
        # Simple comparison (would use proper t-test in production)
        control_mean = control_results['mean']
        pooled_se = np.sqrt(control_results['sem']**2 + results[best_variant]['sem']**2)
        
        if pooled_se > 0:
            z_score = (best_mean - control_mean) / pooled_se
            p_value = 2 * (1 - 0.5 * (1 + np.tanh(z_score / 2)))  # Approximate p-value
            
            if p_value < (1 - self.confidence_level):
                return best_variant, f"Winner with p-value: {p_value:.4f}"
                
        return best_variant, "No significant difference detected"


def run_advanced_analytics():
    """Run complete advanced analytics pipeline"""
    print("=" * 70)
    print("ADVANCED AI ANALYTICS MODULE")
    print("=" * 70)
    
    # Create sample data
    np.random.seed(42)
    n_users = 500
    
    # Sample features
    features_df = pd.DataFrame({
        'user_id': range(1, n_users + 1),
        'total_interactions': np.random.randint(1, 100, n_users),
        'unique_actions': np.random.randint(1, 10, n_users),
        'success_rate': np.random.uniform(0.3, 1.0, n_users),
        'session_duration_mean': np.random.exponential(scale=15, size=n_users),
        'action_diversity_ratio': np.random.uniform(0.1, 1.0, n_users),
        'pct_advanced_premium': np.random.uniform(0, 0.8, n_users),
        'days_active': np.random.randint(1, 90, n_users),
        'complete_sessions': np.random.randint(0, 10, n_users),
        'advanced_user': np.random.choice([0, 1], n_users)
    })
    
    feature_cols = [
        'total_interactions', 'unique_actions', 'success_rate',
        'session_duration_mean', 'action_diversity_ratio', 'pct_advanced_premium',
        'days_active', 'complete_sessions', 'advanced_user'
    ]
    
    # 1. Anomaly Detection
    print("\n🔍 Running Anomaly Detection...")
    anomaly_detector = AnomalyDetector(contamination=0.1)
    anomaly_detector.fit(features_df, feature_cols)
    predictions, scores = anomaly_detector.predict(features_df, feature_cols)
    anomaly_info = anomaly_detector.get_anomaly_profiles(features_df, predictions, scores)
    
    print(f"  ✓ Detected {anomaly_info['total_anomalies']} anomalies ({anomaly_info['anomaly_percentage']:.1f}%)")
    if anomaly_info['common_characteristics']:
        print(f"  ✓ Common patterns: {', '.join(anomaly_info['common_characteristics'])}")
    
    # 2. Churn Prediction
    print("\n📉 Running Churn Prediction...")
    churn_predictor = ChurnPredictor(threshold=0.5)
    
    # Create sample labels
    labels_df = pd.DataFrame({
        'user_id': features_df['user_id'],
        'churned': np.random.choice([0, 1], n_users, p=[0.7, 0.3])
    })
    
    churn_predictor.fit(features_df, labels_df, feature_cols)
    churn_prob, churn_pred = churn_predictor.predict_churn_probability(features_df, feature_cols)
    features_df, risk_dist = churn_predictor.get_risk_segments(features_df, churn_prob)
    
    print(f"  ✓ Risk Distribution: {dict(risk_dist)}")
    print(f"  ✓ High Risk Users: {(risk_dist.get('High Risk', 0))}")
    print(f"  ✓ Medium Risk Users: {(risk_dist.get('Medium Risk', 0))}")
    print(f"  ✓ Low Risk Users: {(risk_dist.get('Low Risk', 0))}")
    
    # 3. User Segmentation
    print("\n👥 Running User Segmentation...")
    segmenter = UserSegmenter(n_clusters=4, method='kmeans')
    segmented_df, segment_profiles, metrics = segmenter.fit_segment(features_df, feature_cols)
    characteristics = segmenter.get_segment_characteristics(segment_profiles)
    
    print(f"  ✓ Silhouette Score: {metrics.get('silhouette_score', 'N/A'):.3f}")
    print(f"  ✓ Segments identified: {len(segment_profiles)}")
    for seg, info in characteristics.items():
        print(f"  ✓ {seg}: {', '.join(info['traits'])}")
    
    # 4. A/B Testing
    print("\n🧪 Running A/B Test Simulation...")
    ab_test = ABTestEngine(confidence_level=0.95)
    ab_test.create_experiment('rec_test', 
                              {'control': [], 'treatment_a': [], 'treatment_b': []},
                              'conversion_rate')
    
    # Simulate observations
    for _ in range(100):
        ab_test.add_observations('rec_test', 'control', [np.random.normal(0.12, 0.02)])
        ab_test.add_observations('rec_test', 'treatment_a', [np.random.normal(0.15, 0.02)])
        ab_test.add_observations('rec_test', 'treatment_b', [np.random.normal(0.18, 0.02)])
    
    results = ab_test.calculate_statistics('rec_test')
    winner, reason = ab_test.determine_winner('rec_test')
    
    print(f"  ✓ Control mean: {results['control']['mean']:.3f}")
    print(f"  ✓ Treatment A mean: {results['treatment_a']['mean']:.3f}")
    print(f"  ✓ Treatment B mean: {results['treatment_b']['mean']:.3f}")
    print(f"  ✓ Winner: {winner} ({reason})")
    
    print("\n" + "=" * 70)
    print("✅ ADVANCED ANALYTICS COMPLETE")
    print("=" * 70)
    
    return {
        'anomaly_detector': anomaly_detector,
        'churn_predictor': churn_predictor,
        'segmenter': segmenter,
        'ab_test': ab_test,
        'segmented_df': segmented_df
    }


if __name__ == "__main__":
    results = run_advanced_analytics()
