import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from collections import Counter

# Zerve design system colors
DARK_BG = '#1D1D20'
PRIMARY_TEXT = '#fbfbff'
SECONDARY_TEXT = '#909094'
HIGHLIGHT_YELLOW = '#ffd400'
SUCCESS_GREEN = '#17b26a'
WARNING_RED = '#f04438'
ZERVE_COLORS = ['#A1C9F4', '#FFB482', '#8DE5A1', '#FF9F9B', '#D0BBFF', 
                '#1F77B4', '#9467BD', '#8C564B', '#C49C94', '#E377C2']

print("=" * 80)
print("MULTI-USER ANALYTICS ENGINE: REAL-TIME AGGREGATE METRICS")
print("=" * 80)

# ============================================================================
# 1. AGGREGATE METRICS ACROSS ALL USERS
# ============================================================================
print("\n" + "=" * 80)
print("GLOBAL AGGREGATE METRICS")
print("=" * 80)

# Overall platform statistics
aggregate_total_users = len(results_intent_df)
aggregate_total_interactions = results_intent_df['total_interactions'].sum()
aggregate_avg_interactions_per_user = results_intent_df['total_interactions'].mean()
aggregate_median_interactions_per_user = results_intent_df['total_interactions'].median()
aggregate_overall_success_rate = feature_matrix['overall_success_rate'].mean()
aggregate_total_active_days = results_intent_df['days_active'].sum()
aggregate_avg_session_duration = feature_matrix['avg_session_duration'].mean()
aggregate_total_session_time = feature_matrix['total_session_time_hrs'].sum()

print(f"\n📊 Platform-Wide Statistics:")
print(f"  • Total Active Users: {aggregate_total_users:,}")
print(f"  • Total Interactions: {aggregate_total_interactions:,}")
print(f"  • Avg Interactions per User: {aggregate_avg_interactions_per_user:.2f}")
print(f"  • Median Interactions per User: {aggregate_median_interactions_per_user:.1f}")
print(f"  • Overall Success Rate: {aggregate_overall_success_rate:.2%}")
print(f"  • Avg Session Duration: {aggregate_avg_session_duration:.1f} minutes")
print(f"  • Total Platform Usage Time: {aggregate_total_session_time:.1f} hours")

# Action distribution across all users
aggregate_action_frequencies = {}
for action_col in ['freq_login', 'freq_view_dashboard', 'freq_run_analysis', 
                   'freq_create_visualization', 'freq_export_data', 'freq_share_result', 'freq_logout']:
    action_name = action_col.replace('freq_', '')
    aggregate_action_frequencies[action_name] = feature_matrix[action_col].sum()

print(f"\n📈 Action Distribution (Total Counts):")
for action, count in sorted(aggregate_action_frequencies.items(), key=lambda x: x[1], reverse=True):
    pct = 100 * count / aggregate_total_interactions
    print(f"  • {action}: {count:,} ({pct:.1f}%)")

# Feature tier usage
aggregate_basic_usage = feature_matrix['freq_basic'].sum()
aggregate_advanced_usage = feature_matrix['freq_advanced'].sum()
aggregate_premium_usage = feature_matrix['freq_premium'].sum()
aggregate_total_feature_usage = aggregate_basic_usage + aggregate_advanced_usage + aggregate_premium_usage

print(f"\n🎯 Feature Tier Usage:")
print(f"  • Basic: {aggregate_basic_usage:,} ({100*aggregate_basic_usage/aggregate_total_feature_usage:.1f}%)")
print(f"  • Advanced: {aggregate_advanced_usage:,} ({100*aggregate_advanced_usage/aggregate_total_feature_usage:.1f}%)")
print(f"  • Premium: {aggregate_premium_usage:,} ({100*aggregate_premium_usage/aggregate_total_feature_usage:.1f}%)")

# ============================================================================
# 2. COHORT ANALYSIS - USER SEGMENTS BY INTENTION
# ============================================================================
print("\n" + "=" * 80)
print("COHORT ANALYSIS: USER SEGMENTATION BY INTENTION")
print("=" * 80)

# Group users by intention label
cohort_stats = results_intent_df.groupby('intention_label').agg({
    'user_id': 'count',
    'total_interactions': ['mean', 'median', 'sum'],
    'success_rate': 'mean',
    'days_active': 'mean',
    'interactions_per_day': 'mean',
    'long_term_success': 'mean'
}).round(2)

cohort_stats.columns = ['user_count', 'avg_interactions', 'median_interactions', 'total_interactions',
                        'avg_success_rate', 'avg_days_active', 'avg_interactions_per_day', 'long_term_success_rate']

print(f"\n📊 Cohort Breakdown:")
for intention in cohort_stats.index:
    stats = cohort_stats.loc[intention]
    pct_users = 100 * stats['user_count'] / aggregate_total_users
    print(f"\n🔹 {intention.upper()} ({stats['user_count']} users, {pct_users:.1f}%)")
    print(f"  • Avg Interactions: {stats['avg_interactions']:.1f}")
    print(f"  • Median Interactions: {stats['median_interactions']:.1f}")
    print(f"  • Total Interactions: {stats['total_interactions']:.0f}")
    print(f"  • Success Rate: {stats['avg_success_rate']:.2%}")
    print(f"  • Avg Days Active: {stats['avg_days_active']:.1f}")
    print(f"  • Interactions/Day: {stats['avg_interactions_per_day']:.2f}")
    print(f"  • Long-term Success: {stats['long_term_success_rate']:.2%}")

# ============================================================================
# 3. BEHAVIORAL CLUSTERING - FEATURE USAGE PATTERNS
# ============================================================================
print("\n" + "=" * 80)
print("BEHAVIORAL CLUSTERING: USAGE PATTERN ANALYSIS")
print("=" * 80)

# Merge intention labels with feature matrix
behavioral_clusters = feature_matrix.merge(
    results_intent_df[['user_id', 'intention_label']], 
    on='user_id', 
    how='left'
)

# Analyze behavioral patterns by cohort
print(f"\n📈 Feature Usage Patterns by Cohort:")
for intention in results_intent_df['intention_label'].unique():
    cohort_data = behavioral_clusters[behavioral_clusters['intention_label'] == intention]
    
    print(f"\n🔹 {intention.upper()}:")
    print(f"  • Unique Actions Diversity: {cohort_data['action_diversity_ratio'].mean():.2%}")
    print(f"  • Complete Sessions: {cohort_data['complete_sessions'].mean():.1f}")
    print(f"  • Advanced/Premium Usage: {cohort_data['pct_advanced_premium'].mean():.2%}")
    print(f"  • Business Hours Usage: {cohort_data['pct_business_hours'].mean():.2%}")
    print(f"  • Weekend Usage: {cohort_data['pct_weekend'].mean():.2%}")
    print(f"  • Workflow Pattern Adoption:")
    print(f"    - Login→Analysis: {cohort_data['has_login_analysis_pattern'].mean():.2%}")
    print(f"    - Analysis→Viz: {cohort_data['has_analysis_viz_pattern'].mean():.2%}")
    print(f"    - Viz→Export: {cohort_data['has_viz_export_pattern'].mean():.2%}")

# ============================================================================
# 4. ENGAGEMENT TRENDS - TIME-BASED ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("ENGAGEMENT TRENDS: TEMPORAL PATTERNS")
print("=" * 80)

# User lifecycle metrics
engagement_metrics = {
    'new_users': len(results_intent_df[results_intent_df['days_active'] <= 7]),
    'active_users': len(results_intent_df[results_intent_df['days_active'].between(8, 30)]),
    'established_users': len(results_intent_df[results_intent_df['days_active'] > 30]),
    'returned_users': results_intent_df['returned_after_first_day'].sum(),
    'one_time_users': len(results_intent_df[results_intent_df['total_interactions'] == 1])
}

print(f"\n📅 User Lifecycle Distribution:")
print(f"  • New Users (≤7 days): {engagement_metrics['new_users']} ({100*engagement_metrics['new_users']/aggregate_total_users:.1f}%)")
print(f"  • Active Users (8-30 days): {engagement_metrics['active_users']} ({100*engagement_metrics['active_users']/aggregate_total_users:.1f}%)")
print(f"  • Established Users (>30 days): {engagement_metrics['established_users']} ({100*engagement_metrics['established_users']/aggregate_total_users:.1f}%)")
print(f"  • Returned After First Day: {engagement_metrics['returned_users']} ({100*engagement_metrics['returned_users']/aggregate_total_users:.1f}%)")
print(f"  • One-Time Users: {engagement_metrics['one_time_users']} ({100*engagement_metrics['one_time_users']/aggregate_total_users:.1f}%)")

# Recency analysis
recency_buckets = {
    'active_last_7_days': len(feature_matrix[feature_matrix['days_since_last_interaction'] <= 7]),
    'active_last_30_days': len(feature_matrix[feature_matrix['days_since_last_interaction'] <= 30]),
    'dormant_30_60_days': len(feature_matrix[feature_matrix['days_since_last_interaction'].between(31, 60)]),
    'at_risk_60_plus': len(feature_matrix[feature_matrix['days_since_last_interaction'] > 60])
}

print(f"\n📊 User Recency Distribution:")
print(f"  • Active Last 7 Days: {recency_buckets['active_last_7_days']} ({100*recency_buckets['active_last_7_days']/aggregate_total_users:.1f}%)")
print(f"  • Active Last 30 Days: {recency_buckets['active_last_30_days']} ({100*recency_buckets['active_last_30_days']/aggregate_total_users:.1f}%)")
print(f"  • Dormant (30-60 days): {recency_buckets['dormant_30_60_days']} ({100*recency_buckets['dormant_30_60_days']/aggregate_total_users:.1f}%)")
print(f"  • At Risk (60+ days): {recency_buckets['at_risk_60_plus']} ({100*recency_buckets['at_risk_60_plus']/aggregate_total_users:.1f}%)")

# ============================================================================
# 5. COMPARATIVE STATISTICS - SEGMENTATION INSIGHTS
# ============================================================================
print("\n" + "=" * 80)
print("COMPARATIVE STATISTICS: CROSS-SEGMENT ANALYSIS")
print("=" * 80)

# Compare high vs low engagement
high_engagement = feature_matrix[feature_matrix['total_interactions'] >= feature_matrix['total_interactions'].quantile(0.75)]
low_engagement = feature_matrix[feature_matrix['total_interactions'] <= feature_matrix['total_interactions'].quantile(0.25)]

print(f"\n📊 High vs Low Engagement Users:")
print(f"\nHigh Engagement (Top 25%, n={len(high_engagement)}):")
print(f"  • Avg Interactions: {high_engagement['total_interactions'].mean():.1f}")
print(f"  • Success Rate: {high_engagement['overall_success_rate'].mean():.2%}")
print(f"  • Session Duration: {high_engagement['avg_session_duration'].mean():.1f} min")
print(f"  • Advanced/Premium: {high_engagement['pct_advanced_premium'].mean():.2%}")

print(f"\nLow Engagement (Bottom 25%, n={len(low_engagement)}):")
print(f"  • Avg Interactions: {low_engagement['total_interactions'].mean():.1f}")
print(f"  • Success Rate: {low_engagement['overall_success_rate'].mean():.2%}")
print(f"  • Session Duration: {low_engagement['avg_session_duration'].mean():.1f} min")
print(f"  • Advanced/Premium: {low_engagement['pct_advanced_premium'].mean():.2%}")

# Success vs non-success comparison
successful_users = results_intent_df[results_intent_df['long_term_success'] == 1]
non_successful_users = results_intent_df[results_intent_df['long_term_success'] == 0]

print(f"\n📊 Long-term Successful vs Non-successful Users:")
print(f"\nSuccessful Users (n={len(successful_users)}, {100*len(successful_users)/aggregate_total_users:.1f}%):")
print(f"  • Avg Interactions: {successful_users['total_interactions'].mean():.1f}")
print(f"  • Days Active: {successful_users['days_active'].mean():.1f}")
print(f"  • Success Rate: {successful_users['success_rate'].mean():.2%}")
print(f"  • Interactions/Day: {successful_users['interactions_per_day'].mean():.2f}")

print(f"\nNon-successful Users (n={len(non_successful_users)}, {100*len(non_successful_users)/aggregate_total_users:.1f}%):")
print(f"  • Avg Interactions: {non_successful_users['total_interactions'].mean():.1f}")
print(f"  • Days Active: {non_successful_users['days_active'].mean():.1f}")
print(f"  • Success Rate: {non_successful_users['success_rate'].mean():.2%}")
print(f"  • Interactions/Day: {non_successful_users['interactions_per_day'].mean():.2f}")

# ============================================================================
# 6. CREATE AGGREGATE ANALYTICS DATAFRAME
# ============================================================================
print("\n" + "=" * 80)
print("AGGREGATE ANALYTICS DATA STRUCTURE")
print("=" * 80)

# Create comprehensive aggregate metrics dataframe
aggregate_metrics_df = pd.DataFrame({
    'metric_category': ['platform', 'platform', 'platform', 'platform', 'platform',
                        'engagement', 'engagement', 'engagement', 'engagement',
                        'cohort', 'cohort', 'cohort'],
    'metric_name': ['total_users', 'total_interactions', 'avg_interactions_per_user', 
                   'overall_success_rate', 'total_session_hours',
                   'new_users_7d', 'active_users_8_30d', 'established_users_30d_plus', 'returned_users',
                   'builder_count', 'explorer_count', 'learner_count'],
    'metric_value': [
        aggregate_total_users,
        aggregate_total_interactions,
        aggregate_avg_interactions_per_user,
        aggregate_overall_success_rate,
        aggregate_total_session_time,
        engagement_metrics['new_users'],
        engagement_metrics['active_users'],
        engagement_metrics['established_users'],
        engagement_metrics['returned_users'],
        len(results_intent_df[results_intent_df['intention_label'] == 'Builder']),
        len(results_intent_df[results_intent_df['intention_label'] == 'Explorer']),
        len(results_intent_df[results_intent_df['intention_label'] == 'Learner'])
    ]
})

print(f"\n✓ Aggregate Metrics DataFrame created:")
print(aggregate_metrics_df.to_string(index=False))

# Create user segments summary
user_segments_summary = results_intent_df.groupby('intention_label').agg({
    'user_id': 'count',
    'total_interactions': ['mean', 'sum'],
    'success_rate': 'mean',
    'long_term_success': 'mean'
}).round(3)
user_segments_summary.columns = ['user_count', 'avg_interactions', 'total_interactions', 
                                  'avg_success_rate', 'long_term_success_rate']

print(f"\n✓ User Segments Summary:")
print(user_segments_summary)

# Create trend analysis data (interaction distribution by cohort)
trend_analysis_df = results_intent_df.groupby('intention_label').agg({
    'total_interactions': ['min', 'max', 'mean', 'std'],
    'days_active': ['mean', 'std'],
    'interactions_per_day': ['mean', 'std']
}).round(2)

print(f"\n✓ Trend Analysis by Cohort:")
print(trend_analysis_df)

print("\n" + "=" * 80)
print("✓ MULTI-USER AGGREGATE ANALYTICS ENGINE COMPLETE")
print("=" * 80)
print(f"\n📊 Available Outputs:")
print(f"  • aggregate_metrics_df: Platform-wide KPIs ({len(aggregate_metrics_df)} metrics)")
print(f"  • user_segments_summary: Cohort statistics by intention")
print(f"  • cohort_stats: Detailed cohort breakdown")
print(f"  • behavioral_clusters: User-level features with intention labels")
print(f"  • trend_analysis_df: Temporal patterns by segment")
print(f"\n✓ Real-time updates: All metrics computed from latest user data")
print(f"✓ Segments: {len(results_intent_df['intention_label'].unique())} intention cohorts identified")
print(f"✓ Coverage: {aggregate_total_users} active users analyzed")
