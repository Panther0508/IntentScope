import pandas as pd
import numpy as np
from collections import Counter

print("=" * 70)
print("BEHAVIORAL FEATURE ENGINEERING")
print("=" * 70)

# Sort data for temporal analysis
df_sorted = user_behavior_df.sort_values(['user_id', 'timestamp']).reset_index(drop=True)

# Initialize feature dictionary for each user
behavioral_features = {}

# Process each user
for _feat_user_id in df_sorted['user_id'].unique():
    _feat_user_data = df_sorted[df_sorted['user_id'] == _feat_user_id].reset_index(drop=True)
    
    _feat_features = {'user_id': _feat_user_id}
    
    # === 1. FREQUENCY FEATURES ===
    _feat_features['total_interactions'] = len(_feat_user_data)
    _feat_features['days_active'] = (_feat_user_data['timestamp'].max() - _feat_user_data['timestamp'].min()).days + 1
    _feat_features['interactions_per_day'] = _feat_features['total_interactions'] / _feat_features['days_active']
    
    # Action frequency distribution
    _feat_action_counts = _feat_user_data['action'].value_counts()
    for _feat_action in ['login', 'view_dashboard', 'run_analysis', 'create_visualization', 
                   'export_data', 'share_result', 'logout']:
        _feat_features[f'freq_{_feat_action}'] = _feat_action_counts.get(_feat_action, 0)
        _feat_features[f'pct_{_feat_action}'] = _feat_action_counts.get(_feat_action, 0) / len(_feat_user_data)
    
    # Feature tier usage frequency
    _feat_tier_counts = _feat_user_data['feature_tier'].value_counts()
    _feat_features['freq_basic'] = _feat_tier_counts.get('basic', 0)
    _feat_features['freq_advanced'] = _feat_tier_counts.get('advanced', 0)
    _feat_features['freq_premium'] = _feat_tier_counts.get('premium', 0)
    _feat_features['pct_advanced_premium'] = (_feat_features['freq_advanced'] + _feat_features['freq_premium']) / len(_feat_user_data)
    
    # === 2. SEQUENCE PATTERNS ===
    _feat_actions_list = _feat_user_data['action'].tolist()
    
    # Action diversity
    _feat_features['unique_actions'] = _feat_user_data['action'].nunique()
    _feat_features['action_diversity_ratio'] = _feat_features['unique_actions'] / 7  # 7 total action types
    
    # Common action sequences (bigrams)
    _feat_bigrams = [(_feat_actions_list[i], _feat_actions_list[i+1]) for i in range(len(_feat_actions_list)-1)]
    _feat_bigram_counts = Counter(_feat_bigrams)
    _feat_features['most_common_sequence_count'] = _feat_bigram_counts.most_common(1)[0][1] if _feat_bigrams else 0
    _feat_features['unique_sequences'] = len(_feat_bigram_counts)
    
    # Check for key workflow patterns
    _feat_features['has_login_analysis_pattern'] = int(('login', 'run_analysis') in _feat_bigrams)
    _feat_features['has_analysis_viz_pattern'] = int(('run_analysis', 'create_visualization') in _feat_bigrams)
    _feat_features['has_viz_export_pattern'] = int(('create_visualization', 'export_data') in _feat_bigrams)
    _feat_features['has_export_share_pattern'] = int(('export_data', 'share_result') in _feat_bigrams)
    
    # Session completeness (login -> analysis -> logout pattern)
    _feat_features['complete_sessions'] = sum(1 for i in range(len(_feat_actions_list)-2) 
                                       if 'login' in _feat_actions_list[i:i+3] and 'logout' in _feat_actions_list[i:i+3])
    
    # === 3. TIME PATTERNS ===
    _feat_user_data['hour'] = _feat_user_data['timestamp'].dt.hour
    _feat_user_data['day_of_week'] = _feat_user_data['timestamp'].dt.dayofweek
    _feat_user_data['is_weekend'] = _feat_user_data['day_of_week'].isin([5, 6]).astype(int)
    
    # Time of day preferences
    _feat_features['avg_hour_of_day'] = _feat_user_data['hour'].mean()
    _feat_features['hour_std'] = _feat_user_data['hour'].std()
    _feat_features['pct_business_hours'] = ((_feat_user_data['hour'] >= 9) & (_feat_user_data['hour'] <= 17)).mean()
    _feat_features['pct_weekend'] = _feat_user_data['is_weekend'].mean()
    
    # Time between interactions (recency and regularity)
    if len(_feat_user_data) > 1:
        _feat_time_diffs = _feat_user_data['timestamp'].diff().dt.total_seconds() / 3600  # hours
        _feat_features['avg_time_between_interactions_hrs'] = _feat_time_diffs.mean()
        _feat_features['median_time_between_interactions_hrs'] = _feat_time_diffs.median()
        _feat_features['std_time_between_interactions_hrs'] = _feat_time_diffs.std()
        _feat_features['max_gap_days'] = _feat_time_diffs.max() / 24 if not pd.isna(_feat_time_diffs.max()) else 0
    else:
        _feat_features['avg_time_between_interactions_hrs'] = 0
        _feat_features['median_time_between_interactions_hrs'] = 0
        _feat_features['std_time_between_interactions_hrs'] = 0
        _feat_features['max_gap_days'] = 0
    
    # Recency (days since last interaction)
    _feat_features['days_since_last_interaction'] = (df_sorted['timestamp'].max() - _feat_user_data['timestamp'].max()).days
    _feat_features['days_since_first_interaction'] = (df_sorted['timestamp'].max() - _feat_user_data['timestamp'].min()).days
    
    # === 4. WORKFLOW COMPLEXITY ===
    _feat_features['avg_session_duration'] = _feat_user_data['session_duration_minutes'].mean()
    _feat_features['total_session_time_hrs'] = _feat_user_data['session_duration_minutes'].sum() / 60
    _feat_features['median_session_duration'] = _feat_user_data['session_duration_minutes'].median()
    _feat_features['max_session_duration'] = _feat_user_data['session_duration_minutes'].max()
    
    # Success and quality metrics
    _feat_features['overall_success_rate'] = _feat_user_data['success'].mean()
    _feat_features['successful_actions'] = _feat_user_data['success'].sum()
    _feat_features['failed_actions'] = (~_feat_user_data['success']).sum()
    
    # Success rate by action type (for key actions)
    for _feat_action2 in ['run_analysis', 'create_visualization', 'export_data']:
        _feat_action_data = _feat_user_data[_feat_user_data['action'] == _feat_action2]
        if len(_feat_action_data) > 0:
            _feat_features[f'success_rate_{_feat_action2}'] = _feat_action_data['success'].mean()
        else:
            _feat_features[f'success_rate_{_feat_action2}'] = 0
    
    # Progression indicators
    _feat_features['tier_progression'] = int(any(_feat_user_data['feature_tier'] == 'premium'))
    _feat_features['advanced_user'] = int(_feat_features['freq_advanced'] + _feat_features['freq_premium'] >= 2)
    
    # Early behavior (first 3 interactions)
    _feat_first_3 = _feat_user_data.head(3)
    _feat_features['early_success_rate'] = _feat_first_3['success'].mean() if len(_feat_first_3) > 0 else 0
    _feat_features['early_avg_session'] = _feat_first_3['session_duration_minutes'].mean() if len(_feat_first_3) > 0 else 0
    
    behavioral_features[_feat_user_id] = _feat_features

# Convert to DataFrame
feature_matrix = pd.DataFrame.from_dict(behavioral_features, orient='index').reset_index(drop=True)

# Merge with target variable
feature_matrix = feature_matrix.merge(
    user_metrics[['user_id', 'long_term_success']], 
    on='user_id', 
    how='left'
)

print(f"\n✓ Feature Engineering Complete!")
print(f"  • Total users: {len(feature_matrix)}")
print(f"  • Total features: {len(feature_matrix.columns) - 2} (excluding user_id and target)")
print(f"  • Target variable: long_term_success")

print("\n" + "=" * 70)
print("FEATURE CATEGORIES")
print("=" * 70)

print("\n1. FREQUENCY FEATURES (18 features):")
freq_features = [col for col in feature_matrix.columns if col.startswith('freq_') or col.startswith('pct_') 
                 or col in ['total_interactions', 'days_active', 'interactions_per_day']]
print(f"   {', '.join(freq_features[:10])}")
print(f"   ... and {len(freq_features)-10} more")

print("\n2. SEQUENCE PATTERN FEATURES (9 features):")
seq_features = [col for col in feature_matrix.columns if 'pattern' in col or 'sequence' in col 
                or col in ['unique_actions', 'action_diversity_ratio', 'complete_sessions']]
print(f"   {', '.join(seq_features)}")

print("\n3. TIME PATTERN FEATURES (12 features):")
time_features = [col for col in feature_matrix.columns if 'hour' in col or 'weekend' in col 
                 or 'time_between' in col or 'gap' in col or 'since' in col or 'business_hours' in col]
print(f"   {', '.join(time_features)}")

print("\n4. WORKFLOW COMPLEXITY FEATURES (15 features):")
workflow_features = [col for col in feature_matrix.columns if 'session' in col or 'success' in col 
                     or 'tier' in col or 'early' in col or col in ['successful_actions', 'failed_actions', 'advanced_user']]
print(f"   {', '.join(workflow_features[:10])}")
print(f"   ... and {len(workflow_features)-10} more")

print("\n" + "=" * 70)
print("FEATURE MATRIX SUMMARY")
print("=" * 70)
print(feature_matrix.describe().round(3))

print("\n" + "=" * 70)
print("SAMPLE FEATURE MATRIX (First 5 Users)")
print("=" * 70)
print(feature_matrix.head().to_string())

print("\n✓ Feature matrix ready for modeling!")
print(f"✓ Output variable: 'feature_matrix' ({feature_matrix.shape[0]} rows × {feature_matrix.shape[1]} columns)")
