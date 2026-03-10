import numpy as np
import pandas as pd
import time
from datetime import datetime
import random

print("=" * 70)
print("REAL-TIME PREDICTION ENGINE")
print("=" * 70)

class RealtimePredictionEngine:
    """
    Real-time prediction engine that processes simulated streaming events,
    extracts features incrementally, and predicts intentions and success probability.
    """
    
    def __init__(self, event_buffer, gb_model, scaler, kmeans_model, tfidf_vectorizer, 
                 scaler_embed, intention_labels_map):
        """
        Initialize the prediction engine with trained models.
        
        Parameters:
        -----------
        event_buffer : StreamingEventBuffer
            Buffer for managing streaming events and incremental feature extraction
        gb_model : GradientBoostingClassifier
            Trained success predictor
        scaler : StandardScaler
            Feature scaler for GB model
        kmeans_model : KMeans
            Trained intention clustering model
        tfidf_vectorizer : TfidfVectorizer
            Fitted vectorizer for sequence embeddings
        scaler_embed : StandardScaler
            Scaler for behavioral features in embeddings
        intention_labels_map : dict
            Mapping from cluster ID to intention label
        """
        self.buffer = event_buffer
        self.gb_model = gb_model
        self.scaler = scaler
        self.kmeans_model = kmeans_model
        self.tfidf_vectorizer = tfidf_vectorizer
        self.scaler_embed = scaler_embed
        self.intention_labels_map = intention_labels_map
        
        # Store predictions
        self.predictions = []
        
        # Performance tracking
        self.total_prediction_time = 0
        self.prediction_count = 0
        
        print("✓ RealtimePredictionEngine initialized")
        print("  • Event buffer configured")
        print("  • GB success predictor loaded")
        print("  • K-Means intention classifier loaded")
        print("  • TF-IDF vectorizer loaded")
    
    def process_event(self, user_id, action, tier, session_duration, success, feature_used):
        """
        Process a single streaming event and generate predictions.
        
        Returns:
        --------
        dict with prediction results including intention, success probability, and latency
        """
        start_time = time.time()
        
        # Add event to buffer (incremental feature update)
        timestamp = datetime.now()
        metadata = {
            'tier': tier,
            'success': success,
            'session_duration': session_duration,
            'feature_used': feature_used
        }
        
        self.buffer.add_event(user_id, action, timestamp, metadata)
        
        # Extract features for this user (<100ms target)
        features_dict, feature_extraction_time = self.buffer.get_features(user_id)
        
        # Convert to DataFrame for model input (54 features)
        feature_cols = [
            'total_interactions', 'days_active', 'interactions_per_day',
            'freq_login', 'pct_login', 'freq_view_dashboard', 'pct_view_dashboard',
            'freq_run_analysis', 'pct_run_analysis', 'freq_create_visualization', 
            'pct_create_visualization', 'freq_export_data', 'pct_export_data',
            'freq_share_result', 'pct_share_result', 'freq_logout', 'pct_logout',
            'freq_basic', 'freq_advanced', 'freq_premium', 'pct_advanced_premium',
            'unique_actions', 'action_diversity_ratio', 'most_common_sequence_count',
            'unique_sequences', 'has_login_analysis_pattern', 'has_analysis_viz_pattern',
            'has_viz_export_pattern', 'has_export_share_pattern', 'complete_sessions',
            'avg_hour_of_day', 'hour_std', 'pct_business_hours', 'pct_weekend',
            'avg_time_between_interactions_hrs', 'median_time_between_interactions_hrs',
            'std_time_between_interactions_hrs', 'max_gap_days', 'days_since_last_interaction',
            'days_since_first_interaction', 'avg_session_duration', 'total_session_time_hrs',
            'median_session_duration', 'max_session_duration', 'overall_success_rate',
            'successful_actions', 'failed_actions', 'success_rate_run_analysis',
            'success_rate_create_visualization', 'success_rate_export_data',
            'tier_progression', 'advanced_user', 'early_success_rate', 'early_avg_session'
        ]
        
        features_df = pd.DataFrame([{col: features_dict.get(col, 0) for col in feature_cols}])
        
        # Scale features
        features_scaled = self.scaler.transform(features_df)
        
        # Predict success probability
        success_prob = self.gb_model.predict_proba(features_scaled)[0, 1]
        
        # Predict intention
        # Get action sequence for this user
        user_events = self.buffer.get_user_sequence(user_id)
        action_sequence = ' '.join([e['event_type'] for e in user_events])
        
        # Create TF-IDF embedding
        sequence_embedding = self.tfidf_vectorizer.transform([action_sequence]).toarray()
        
        # Get behavioral features for embedding
        behavioral_features = np.array([[
            features_dict.get('total_interactions', 0),
            features_dict.get('unique_actions', 0),
            features_dict.get('overall_success_rate', 0),
            features_dict.get('pct_advanced_premium', 0),
            features_dict.get('interactions_per_day', 0),
            features_dict.get('days_active', 0),
            features_dict.get('complete_sessions', 0),
            features_dict.get('action_diversity_ratio', 0)
        ]])
        
        behavioral_scaled = self.scaler_embed.transform(behavioral_features)
        
        # Combine embeddings
        combined_embedding = np.hstack([sequence_embedding, behavioral_scaled])
        
        # Predict intention cluster
        intention_cluster = self.kmeans_model.predict(combined_embedding)[0]
        intention_label = self.intention_labels_map.get(intention_cluster, 'Unknown')
        
        # Calculate total latency
        total_latency = (time.time() - start_time) * 1000  # milliseconds
        
        # Create prediction result
        prediction = {
            'timestamp': timestamp,
            'user_id': user_id,
            'action': action,
            'tier': tier,
            'success': success,
            'intention_label': intention_label,
            'success_probability': success_prob * 100,  # as percentage
            'feature_extraction_time_ms': feature_extraction_time,
            'total_latency_ms': total_latency,
            'event_sequence_length': len(user_events),
            'confidence_score': self._calculate_confidence(features_dict, success_prob)
        }
        
        self.predictions.append(prediction)
        self.total_prediction_time += total_latency
        self.prediction_count += 1
        
        return prediction
    
    def _calculate_confidence(self, features_dict, success_prob):
        """
        Calculate confidence score based on data quality and model certainty.
        Higher confidence when more data available and probability is extreme (near 0 or 1).
        """
        # Data quality: more interactions = higher confidence
        interactions = features_dict.get('total_interactions', 0)
        data_quality = min(interactions / 10, 1.0)  # Max at 10 interactions
        
        # Model certainty: probabilities near 0 or 1 are more confident
        model_certainty = abs(success_prob - 0.5) * 2  # Range [0, 1]
        
        # Combined confidence
        confidence = (data_quality * 0.6 + model_certainty * 0.4) * 100
        
        return round(confidence, 1)
    
    def get_performance_stats(self):
        """Get performance statistics."""
        avg_latency = self.total_prediction_time / self.prediction_count if self.prediction_count > 0 else 0
        
        return {
            'total_predictions': self.prediction_count,
            'avg_latency_ms': round(avg_latency, 2),
            'total_time_seconds': round(self.total_prediction_time / 1000, 2),
            'throughput_per_second': round(1000 / avg_latency, 2) if avg_latency > 0 else 0
        }
    
    def get_predictions_dataframe(self):
        """Get all predictions as a DataFrame."""
        return pd.DataFrame(self.predictions)


# Initialize the real-time prediction engine
prediction_engine = RealtimePredictionEngine(
    event_buffer=event_buffer,
    gb_model=gb_classifier,
    scaler=scaler_model,
    kmeans_model=kmeans_intent,
    tfidf_vectorizer=tfidf_vectorizer,
    scaler_embed=scaler_embed,
    intention_labels_map=intention_labels_map
)

print("\n" + "=" * 70)
print("✅ REAL-TIME PREDICTION ENGINE READY")
print("=" * 70)
print("\n🎯 Capabilities:")
print("  • Processes streaming events in real-time")
print("  • Extracts 54 behavioral features incrementally")
print("  • Predicts user intentions (Builder/Explorer/Learner/Abandoner)")
print("  • Predicts success probability (0-100%)")
print("  • Tracks confidence scores and latency")
print("  • Target latency: <100ms per event")
print("\n✓ Models loaded:")
print(f"  • Gradient Boosting success predictor (Test AUC: {gb_test_auc:.4f})")
print(f"  • K-Means intention classifier ({n_clusters_intent} clusters)")
print(f"  • TF-IDF sequence embeddings ({sequence_embeddings_tfidf.shape[1]} features)")
print("\n✓ Ready to process live streaming events!")
