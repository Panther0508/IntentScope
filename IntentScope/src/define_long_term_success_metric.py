import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Try to import from upstream modules, create sample data if not available
try:
    from .load_dataset import user_behavior_df
except ImportError:
    # Create sample data for standalone execution
    print("[OK] Running in standalone mode - creating sample data")
    np.random.seed(42)
    n_users = 500
    n_interactions = 3000
    
    timestamps = [datetime.now() - timedelta(days=np.random.randint(0, 90)) for _ in range(n_interactions)]
    user_behavior_df = pd.DataFrame({
        'user_id': np.random.choice(range(1, n_users + 1), n_interactions),
        'timestamp': timestamps,
        'action': np.random.choice(['login', 'view_dashboard', 'run_analysis', 'create_visualization', 
                                   'export_data', 'share_result', 'logout'], n_interactions),
        'success': np.random.choice([True, False], n_interactions, p=[0.85, 0.15]),
        'session_duration_minutes': np.random.exponential(scale=15, size=n_interactions),
        'feature_tier': np.random.choice(['basic', 'advanced', 'premium'], n_interactions)
    })

print("=" * 70)
print("DEFINING LONG-TERM SUCCESS METRIC")
print("=" * 70)

# Sort data by user and timestamp for temporal analysis
df_sorted = user_behavior_df.sort_values(['user_id', 'timestamp']).reset_index(drop=True)

# Calculate user-level metrics to identify long-term success patterns
user_metrics = df_sorted.groupby('user_id').agg({
    'timestamp': ['min', 'max', 'count'],
    'success': 'mean',
    'session_duration_minutes': 'sum',
    'action': lambda x: x.nunique(),
    'feature_tier': lambda x: (x == 'premium').sum() + (x == 'advanced').sum()
}).reset_index()

user_metrics.columns = ['user_id', 'first_interaction', 'last_interaction', 'total_interactions',
                        'success_rate', 'total_session_time', 'unique_actions', 'advanced_usage_count']

# Calculate days active
user_metrics['days_active'] = (user_metrics['last_interaction'] - user_metrics['first_interaction']).dt.days + 1
user_metrics['interactions_per_day'] = user_metrics['total_interactions'] / user_metrics['days_active']

# Calculate retention (users who came back after first day)
user_metrics['returned_after_first_day'] = user_metrics['days_active'] > 1

print("\nUser-Level Success Indicators:")
print("* Users who returned after first day: {} ({}%)".format(
    user_metrics['returned_after_first_day'].sum(), 
    user_metrics['returned_after_first_day'].mean()*100))
print("* Median days active: {:.1f} days".format(user_metrics['days_active'].median()))
print("* Mean total interactions: {:.1f}".format(user_metrics['total_interactions'].mean()))
print("* Mean success rate: {:.1f}%".format(user_metrics['success_rate'].mean()*100))

# Define Long-Term Success Metric based on behavioral indicators
median_interactions = user_metrics['total_interactions'].median()
mean_success_rate = user_metrics['success_rate'].mean()

user_metrics['long_term_success'] = (
    (user_metrics['returned_after_first_day']) &  # Retention
    (user_metrics['total_interactions'] >= median_interactions) &  # Engagement
    (user_metrics['success_rate'] >= mean_success_rate) &  # Quality
    ((user_metrics['advanced_usage_count'] >= 2) | (user_metrics['unique_actions'] >= 5))  # Progression
).astype(int)

print("\n" + "=" * 70)
print("LONG-TERM SUCCESS METRIC DEFINITION")
print("=" * 70)
print("\n[OK] Long-Term Success Criteria (ALL must be met):")
print("  1. Retention: User returned after first interaction")
print("  2. Engagement: >= {} total interactions (median)".format(median_interactions))
print("  3. Quality: >= {:.1f}% success rate (mean)".format(mean_success_rate*100))
print("  4. Progression: Used advanced/premium features (>=2 times) OR explored diverse actions (>=5 types)")

success_count = user_metrics['long_term_success'].sum()
success_rate_overall = user_metrics['long_term_success'].mean()

print("\n[OK] Long-Term Success Distribution:")
print("  * Successful users: {} ({:.1f}%)".format(success_count, success_rate_overall*100))
print("  * Non-successful users: {} ({:.1f}%)".format(
    len(user_metrics) - success_count, (1-success_rate_overall)*100))

print("\n[OK] Comparison of Success vs Non-Success Users:")
success_users = user_metrics[user_metrics['long_term_success']==1]
non_success_users = user_metrics[user_metrics['long_term_success']==0]

print("  * Avg Days Active: {:.2f} vs {:.2f}".format(
    success_users['days_active'].mean(), non_success_users['days_active'].mean()))
print("  * Avg Total Interactions: {:.2f} vs {:.2f}".format(
    success_users['total_interactions'].mean(), non_success_users['total_interactions'].mean()))
print("  * Avg Success Rate: {:.2f}% vs {:.2f}%".format(
    success_users['success_rate'].mean()*100, non_success_users['success_rate'].mean()*100))
print("  * Avg Advanced Usage: {:.2f} vs {:.2f}".format(
    success_users['advanced_usage_count'].mean(), non_success_users['advanced_usage_count'].mean()))
print("  * Avg Unique Actions: {:.2f} vs {:.2f}".format(
    success_users['unique_actions'].mean(), non_success_users['unique_actions'].mean()))
print("  * Avg Total Session Time (hrs): {:.2f} vs {:.2f}".format(
    success_users['total_session_time'].mean()/60, non_success_users['total_session_time'].mean()/60))

print("\n" + "=" * 70)
print("SUCCESS METRIC OUTPUT")
print("=" * 70)
print("[OK] Created 'user_metrics' DataFrame with {} users".format(len(user_metrics)))
print("[OK] Added 'long_term_success' target variable (0/1)")
print("[OK] Ready for feature engineering in next step")
