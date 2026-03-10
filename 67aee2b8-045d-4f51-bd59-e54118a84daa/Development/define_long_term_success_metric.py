import pandas as pd
import numpy as np

# Define long-term success metric based on the available data
# We'll analyze user engagement patterns over time to determine what constitutes "success"

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
print(f"• Users who returned after first day: {user_metrics['returned_after_first_day'].sum()} ({user_metrics['returned_after_first_day'].mean()*100:.1f}%)")
print(f"• Median days active: {user_metrics['days_active'].median():.1f} days")
print(f"• Mean total interactions: {user_metrics['total_interactions'].mean():.1f}")
print(f"• Mean success rate: {user_metrics['success_rate'].mean()*100:.1f}%")

# Define Long-Term Success Metric based on behavioral indicators
# A user is considered a "long-term success" if they meet multiple criteria:
# 1. Return rate: Came back after first interaction (retention indicator)
# 2. Engagement: Above-median total interactions
# 3. Quality: Above-average success rate
# 4. Progression: Used advanced/premium features OR high diversity of actions

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
print("\n✓ Long-Term Success Criteria (ALL must be met):")
print(f"  1. Retention: User returned after first interaction")
print(f"  2. Engagement: >= {median_interactions:.0f} total interactions (median)")
print(f"  3. Quality: >= {mean_success_rate*100:.1f}% success rate (mean)")
print(f"  4. Progression: Used advanced/premium features (>=2 times) OR explored diverse actions (>=5 types)")

success_count = user_metrics['long_term_success'].sum()
success_rate_overall = user_metrics['long_term_success'].mean()

print(f"\n✓ Long-Term Success Distribution:")
print(f"  • Successful users: {success_count} ({success_rate_overall*100:.1f}%)")
print(f"  • Non-successful users: {len(user_metrics) - success_count} ({(1-success_rate_overall)*100:.1f}%)")

print("\n✓ Comparison of Success vs Non-Success Users:")
comparison_df = pd.DataFrame({
    'Metric': ['Avg Days Active', 'Avg Total Interactions', 'Avg Success Rate', 
               'Avg Advanced Usage', 'Avg Unique Actions', 'Avg Total Session Time (hrs)'],
    'Successful Users': [
        user_metrics[user_metrics['long_term_success']==1]['days_active'].mean(),
        user_metrics[user_metrics['long_term_success']==1]['total_interactions'].mean(),
        user_metrics[user_metrics['long_term_success']==1]['success_rate'].mean() * 100,
        user_metrics[user_metrics['long_term_success']==1]['advanced_usage_count'].mean(),
        user_metrics[user_metrics['long_term_success']==1]['unique_actions'].mean(),
        user_metrics[user_metrics['long_term_success']==1]['total_session_time'].mean() / 60
    ],
    'Non-Successful Users': [
        user_metrics[user_metrics['long_term_success']==0]['days_active'].mean(),
        user_metrics[user_metrics['long_term_success']==0]['total_interactions'].mean(),
        user_metrics[user_metrics['long_term_success']==0]['success_rate'].mean() * 100,
        user_metrics[user_metrics['long_term_success']==0]['advanced_usage_count'].mean(),
        user_metrics[user_metrics['long_term_success']==0]['unique_actions'].mean(),
        user_metrics[user_metrics['long_term_success']==0]['total_session_time'].mean() / 60
    ]
})

for _, row in comparison_df.iterrows():
    print(f"  • {row['Metric']:35s}: {row['Successful Users']:7.2f} vs {row['Non-Successful Users']:7.2f}")

print("\n" + "=" * 70)
print("SUCCESS METRIC OUTPUT")
print("=" * 70)
print(f"✓ Created 'user_metrics' DataFrame with {len(user_metrics)} users")
print(f"✓ Added 'long_term_success' target variable (0/1)")
print(f"✓ Ready for feature engineering in next step")
