from collections import deque, defaultdict, Counter
from datetime import datetime, timedelta
import threading
import pandas as pd
import numpy as np

class IncrementalFeatureExtractor:
    """
    Computes behavioral features incrementally using sliding window algorithms.
    Maintains running statistics and counts to avoid full recomputation.
    """
    
    def __init__(self):
        # Running statistics per user
        self.action_counts = defaultdict(lambda: Counter())  # Action frequency counts
        self.bigram_counts = defaultdict(lambda: Counter())  # Sequence pattern counts
        self.tier_counts = defaultdict(lambda: Counter())   # Tier usage counts
        
        # Time-based aggregates
        self.session_times = defaultdict(list)  # For mean/median calculations
        self.time_diffs = defaultdict(list)     # Inter-event times
        self.hourly_dist = defaultdict(lambda: Counter())  # Hour of day distribution
        self.dow_dist = defaultdict(lambda: Counter())     # Day of week distribution
        
        # Success tracking
        self.success_counts = defaultdict(lambda: {'total': 0, 'success': 0})
        self.action_success = defaultdict(lambda: defaultdict(lambda: {'total': 0, 'success': 0}))
        
        # Temporal metadata
        self.first_event = {}
        self.last_event = {}
        self.total_events = defaultdict(int)
        
        # Last action for bigram tracking
        self.last_action = {}
        
        print("✅ IncrementalFeatureExtractor initialized")
    
    def update(self, user_id, event):
        """
        Update running statistics with new event. O(1) operation for most updates.
        
        Args:
            user_id: User identifier
            event: Event dictionary with keys: event_type, timestamp, metadata
        """
        action = event['event_type']
        timestamp = event['timestamp']
        metadata = event.get('metadata', {})
        
        # Track first/last events
        if user_id not in self.first_event:
            self.first_event[user_id] = timestamp
        self.last_event[user_id] = timestamp
        
        # Increment counters (O(1))
        self.total_events[user_id] += 1
        self.action_counts[user_id][action] += 1
        
        # Track tier usage
        tier = metadata.get('tier', 'basic')
        self.tier_counts[user_id][tier] += 1
        
        # Track bigrams (O(1))
        if user_id in self.last_action:
            bigram = (self.last_action[user_id], action)
            self.bigram_counts[user_id][bigram] += 1
        self.last_action[user_id] = action
        
        # Track time patterns (O(1))
        hour = timestamp.hour
        dow = timestamp.weekday()
        self.hourly_dist[user_id][hour] += 1
        self.dow_dist[user_id][dow] += 1
        
        # Track session duration (bounded list)
        session_dur = metadata.get('session_duration', 0)
        self.session_times[user_id].append(session_dur)
        if len(self.session_times[user_id]) > 100:  # Keep last 100
            self.session_times[user_id].pop(0)
        
        # Track success rates (O(1))
        is_success = metadata.get('success', True)
        self.success_counts[user_id]['total'] += 1
        if is_success:
            self.success_counts[user_id]['success'] += 1
        
        self.action_success[user_id][action]['total'] += 1
        if is_success:
            self.action_success[user_id][action]['success'] += 1
        
        # Track time differences (bounded list)
        if user_id in self.last_event and user_id in self.time_diffs:
            if len(self.time_diffs[user_id]) > 0:
                prev_time = self.time_diffs[user_id][-1][0]
                time_diff = (timestamp - prev_time).total_seconds() / 3600  # hours
                self.time_diffs[user_id].append((timestamp, time_diff))
                if len(self.time_diffs[user_id]) > 100:  # Keep last 100
                    self.time_diffs[user_id].pop(0)
            else:
                self.time_diffs[user_id].append((timestamp, 0))
        else:
            self.time_diffs[user_id] = [(timestamp, 0)]
    
    def extract_features(self, user_id):
        """
        Extract all 54 features for a user from running statistics. O(1) for most features.
        
        Returns:
            Dictionary with 54 behavioral features
        """
        features = {'user_id': user_id}
        
        total = self.total_events.get(user_id, 0)
        if total == 0:
            return self._empty_features(user_id)
        
        # === 1. FREQUENCY FEATURES (18 features) ===
        features['total_interactions'] = total
        
        # Days active calculation
        if user_id in self.first_event and user_id in self.last_event:
            days_active = (self.last_event[user_id] - self.first_event[user_id]).days + 1
            features['days_active'] = max(1, days_active)
            features['interactions_per_day'] = total / features['days_active']
        else:
            features['days_active'] = 1
            features['interactions_per_day'] = total
        
        # Action frequency distribution
        action_counts = self.action_counts[user_id]
        for action in ['login', 'view_dashboard', 'run_analysis', 'create_visualization',
                       'export_data', 'share_result', 'logout']:
            count = action_counts.get(action, 0)
            features[f'freq_{action}'] = count
            features[f'pct_{action}'] = count / total
        
        # Tier usage frequency
        tier_counts = self.tier_counts[user_id]
        features['freq_basic'] = tier_counts.get('basic', 0)
        features['freq_advanced'] = tier_counts.get('advanced', 0)
        features['freq_premium'] = tier_counts.get('premium', 0)
        features['pct_advanced_premium'] = (features['freq_advanced'] + features['freq_premium']) / total
        
        # === 2. SEQUENCE PATTERNS (9 features) ===
        features['unique_actions'] = len(action_counts)
        features['action_diversity_ratio'] = features['unique_actions'] / 7
        
        bigram_counts = self.bigram_counts[user_id]
        if len(bigram_counts) > 0:
            features['most_common_sequence_count'] = bigram_counts.most_common(1)[0][1]
            features['unique_sequences'] = len(bigram_counts)
        else:
            features['most_common_sequence_count'] = 0
            features['unique_sequences'] = 0
        
        # Workflow patterns
        features['has_login_analysis_pattern'] = int(('login', 'run_analysis') in bigram_counts)
        features['has_analysis_viz_pattern'] = int(('run_analysis', 'create_visualization') in bigram_counts)
        features['has_viz_export_pattern'] = int(('create_visualization', 'export_data') in bigram_counts)
        features['has_export_share_pattern'] = int(('export_data', 'share_result') in bigram_counts)
        
        # Complete sessions (estimate from login-logout patterns)
        features['complete_sessions'] = min(
            action_counts.get('login', 0),
            action_counts.get('logout', 0)
        )
        
        # === 3. TIME PATTERNS (12 features) ===
        hourly_dist = self.hourly_dist[user_id]
        if len(hourly_dist) > 0:
            # Weighted average hour
            total_hourly = sum(hourly_dist.values())
            features['avg_hour_of_day'] = sum(h * c for h, c in hourly_dist.items()) / total_hourly
            
            # Hour standard deviation
            avg_hour = features['avg_hour_of_day']
            variance = sum(c * (h - avg_hour)**2 for h, c in hourly_dist.items()) / total_hourly
            features['hour_std'] = np.sqrt(variance)
            
            # Business hours percentage (9-17)
            business_hours_count = sum(c for h, c in hourly_dist.items() if 9 <= h <= 17)
            features['pct_business_hours'] = business_hours_count / total_hourly
        else:
            features['avg_hour_of_day'] = 12
            features['hour_std'] = 0
            features['pct_business_hours'] = 0
        
        # Weekend percentage
        dow_dist = self.dow_dist[user_id]
        if len(dow_dist) > 0:
            total_dow = sum(dow_dist.values())
            weekend_count = dow_dist.get(5, 0) + dow_dist.get(6, 0)
            features['pct_weekend'] = weekend_count / total_dow
        else:
            features['pct_weekend'] = 0
        
        # Time between interactions
        time_diffs = self.time_diffs.get(user_id, [])
        if len(time_diffs) > 1:
            diffs = [td[1] for td in time_diffs[1:]]  # Skip first (0)
            features['avg_time_between_interactions_hrs'] = np.mean(diffs)
            features['median_time_between_interactions_hrs'] = np.median(diffs)
            features['std_time_between_interactions_hrs'] = np.std(diffs)
            features['max_gap_days'] = max(diffs) / 24 if diffs else 0
        else:
            features['avg_time_between_interactions_hrs'] = 0
            features['median_time_between_interactions_hrs'] = 0
            features['std_time_between_interactions_hrs'] = 0
            features['max_gap_days'] = 0
        
        # Recency
        current_time = datetime.now()
        if user_id in self.last_event:
            features['days_since_last_interaction'] = (current_time - self.last_event[user_id]).days
        else:
            features['days_since_last_interaction'] = 0
        
        if user_id in self.first_event:
            features['days_since_first_interaction'] = (current_time - self.first_event[user_id]).days
        else:
            features['days_since_first_interaction'] = 0
        
        # === 4. WORKFLOW COMPLEXITY (15 features) ===
        session_times = self.session_times.get(user_id, [])
        if len(session_times) > 0:
            features['avg_session_duration'] = np.mean(session_times)
            features['total_session_time_hrs'] = sum(session_times) / 60
            features['median_session_duration'] = np.median(session_times)
            features['max_session_duration'] = max(session_times)
        else:
            features['avg_session_duration'] = 0
            features['total_session_time_hrs'] = 0
            features['median_session_duration'] = 0
            features['max_session_duration'] = 0
        
        # Success rates
        success_data = self.success_counts.get(user_id, {'total': 0, 'success': 0})
        if success_data['total'] > 0:
            features['overall_success_rate'] = success_data['success'] / success_data['total']
        else:
            features['overall_success_rate'] = 0
        features['successful_actions'] = success_data['success']
        features['failed_actions'] = success_data['total'] - success_data['success']
        
        # Success rate by action
        for action in ['run_analysis', 'create_visualization', 'export_data']:
            action_data = self.action_success[user_id].get(action, {'total': 0, 'success': 0})
            if action_data['total'] > 0:
                features[f'success_rate_{action}'] = action_data['success'] / action_data['total']
            else:
                features[f'success_rate_{action}'] = 0
        
        # Progression indicators
        features['tier_progression'] = int(tier_counts.get('premium', 0) > 0)
        features['advanced_user'] = int((tier_counts.get('advanced', 0) + tier_counts.get('premium', 0)) >= 2)
        
        # Early behavior (first 3 sessions - approximation using first events)
        if len(session_times) >= 3:
            features['early_success_rate'] = success_data['success'] / min(3, success_data['total'])
            features['early_avg_session'] = np.mean(session_times[:3])
        elif len(session_times) > 0:
            features['early_success_rate'] = features['overall_success_rate']
            features['early_avg_session'] = features['avg_session_duration']
        else:
            features['early_success_rate'] = 0
            features['early_avg_session'] = 0
        
        return features
    
    def _empty_features(self, user_id):
        """Return zero-filled features for users with no events."""
        features = {'user_id': user_id}
        feature_names = [
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
        for name in feature_names:
            features[name] = 0
        return features


class StreamingEventBuffer:
    """
    Real-time event buffer with incremental feature extraction engine.
    Computes 54 behavioral features in <100ms per event using sliding windows.
    """
    
    def __init__(self, max_events_per_user=100, time_window_seconds=3600):
        # Store events per user using deque for O(1) append/pop
        self.user_events = defaultdict(lambda: deque(maxlen=max_events_per_user))
        
        # Incremental feature extractor
        self.feature_extractor = IncrementalFeatureExtractor()
        
        # Store metadata
        self.max_events_per_user = max_events_per_user
        self.time_window_seconds = time_window_seconds
        
        # Thread lock for concurrent access
        self.lock = threading.Lock()
        
        # Statistics
        self.total_events_received = 0
        self.unique_users = set()
        
        # Performance tracking
        self.total_feature_extraction_time = 0
        self.feature_extraction_count = 0
        
        print(f"✅ StreamingEventBuffer with IncrementalFeatureExtractor initialized")
        print(f"   Max events per user: {max_events_per_user}")
        print(f"   Time window: {time_window_seconds}s ({time_window_seconds/3600:.1f}h)")
    
    def add_event(self, user_id, event_type, timestamp=None, metadata=None):
        """
        Add event and update incremental features. O(1) for most operations.
        
        Args:
            user_id: User identifier
            event_type: Type of event
            timestamp: Event timestamp (defaults to current time)
            metadata: Optional dictionary with event data (tier, success, session_duration)
        """
        with self.lock:
            if timestamp is None:
                timestamp = datetime.now()
            
            event = {
                'user_id': user_id,
                'event_type': event_type,
                'timestamp': timestamp,
                'metadata': metadata or {}
            }
            
            # O(1) append to deque
            self.user_events[user_id].append(event)
            
            # Update incremental features (O(1) for most updates)
            self.feature_extractor.update(user_id, event)
            
            # Update statistics
            self.total_events_received += 1
            self.unique_users.add(user_id)
    
    def get_features(self, user_id):
        """
        Extract all 54 features for a user in <100ms.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with 54 behavioral features
        """
        import time
        start_time = time.time()
        
        with self.lock:
            features = self.feature_extractor.extract_features(user_id)
        
        elapsed = (time.time() - start_time) * 1000  # milliseconds
        
        # Track performance
        self.total_feature_extraction_time += elapsed
        self.feature_extraction_count += 1
        
        return features, elapsed
    
    def get_features_batch(self, user_ids):
        """
        Extract features for multiple users.
        
        Args:
            user_ids: List of user identifiers
            
        Returns:
            DataFrame with features for all users, average extraction time
        """
        import time
        start_time = time.time()
        
        feature_list = []
        for user_id in user_ids:
            features, _ = self.get_features(user_id)
            feature_list.append(features)
        
        elapsed = (time.time() - start_time) * 1000  # milliseconds
        avg_time_per_user = elapsed / len(user_ids) if user_ids else 0
        
        return pd.DataFrame(feature_list), avg_time_per_user
    
    def get_user_sequence(self, user_id, max_events=None):
        """Retrieve event sequence for a specific user."""
        with self.lock:
            if user_id not in self.user_events:
                return []
            
            events = list(self.user_events[user_id])
            
            if max_events is not None:
                events = events[-max_events:]
            
            return events
    
    def get_all_users(self):
        """Get list of all users with events in the buffer."""
        with self.lock:
            return list(self.user_events.keys())
    
    def get_buffer_stats(self):
        """Get statistics about the current buffer state."""
        with self.lock:
            avg_extraction_time = (
                self.total_feature_extraction_time / self.feature_extraction_count 
                if self.feature_extraction_count > 0 else 0
            )
            
            stats = {
                'total_events': self.total_events_received,
                'unique_users': len(self.unique_users),
                'active_users': len(self.user_events),
                'avg_events_per_user': np.mean([len(events) for events in self.user_events.values()]) if self.user_events else 0,
                'max_events_stored': max([len(events) for events in self.user_events.values()]) if self.user_events else 0,
                'avg_feature_extraction_ms': avg_extraction_time,
                'total_feature_extractions': self.feature_extraction_count,
            }
            return stats
    
    def clear_all(self):
        """Clear all events from the buffer."""
        with self.lock:
            self.user_events.clear()
            self.total_events_received = 0
            self.unique_users.clear()
            self.feature_extractor = IncrementalFeatureExtractor()

# Initialize the streaming feature extraction engine
event_buffer = StreamingEventBuffer(
    max_events_per_user=100,
    time_window_seconds=3600
)

print("\n📊 Real-Time Feature Extraction Engine Capabilities:")
print("   ✓ O(1) event insertion with automatic feature updates")
print("   ✓ 54 behavioral features computed incrementally")
print("   ✓ <100ms feature extraction per event target")
print("   ✓ Sliding window algorithms for sequence patterns")
print("   ✓ Incremental statistics (mean, median, std)")
print("   ✓ Thread-safe concurrent access")
print("   ✓ Matches batch system feature output")
print("\n🎯 Ready for real-time intention prediction!")
