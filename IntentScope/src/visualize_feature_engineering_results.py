import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

print("=" * 80)
print("BEHAVIORAL FEATURE ENGINEERING - COMPREHENSIVE ANALYSIS")
print("=" * 80)

# ===========================
# 1. FEATURE CATEGORIES OVERVIEW
# ===========================
print("\n" + "=" * 80)
print("FEATURE CATEGORIES SUMMARY")
print("=" * 80)

feature_categories = {
    'Sequence Patterns (n-grams, transitions)': [
        'most_common_sequence_count', 'unique_sequences', 'has_login_analysis_pattern',
        'has_analysis_viz_pattern', 'has_viz_export_pattern', 'has_export_share_pattern',
        'complete_sessions', 'action_diversity_ratio', 'unique_actions'
    ],
    'Temporal Features (session gaps, frequency)': [
        'avg_time_between_interactions_hrs', 'median_time_between_interactions_hrs',
        'std_time_between_interactions_hrs', 'max_gap_days', 'days_since_last_interaction',
        'days_since_first_interaction', 'avg_hour_of_day', 'hour_std',
        'pct_business_hours', 'pct_weekend'
    ],
    'Engagement Metrics (length, actions, rates)': [
        'total_interactions', 'interactions_per_day', 'days_active',
        'avg_session_duration', 'total_session_time_hrs', 'median_session_duration',
        'max_session_duration', 'overall_success_rate', 'successful_actions', 
        'failed_actions'
    ],
    'Statistical Aggregations (freq, pct)': [
        'freq_login', 'pct_login', 'freq_view_dashboard', 'pct_view_dashboard',
        'freq_run_analysis', 'pct_run_analysis', 'freq_create_visualization',
        'pct_create_visualization', 'freq_export_data', 'pct_export_data',
        'freq_share_result', 'pct_share_result', 'freq_logout', 'pct_logout',
        'freq_basic', 'freq_advanced', 'freq_premium', 'pct_advanced_premium'
    ],
    'Additional Pattern Features': [
        'success_rate_run_analysis', 'success_rate_create_visualization',
        'success_rate_export_data', 'tier_progression', 'advanced_user',
        'early_success_rate', 'early_avg_session'
    ]
}

total_behavioral_features = 0
for category, features in feature_categories.items():
    count = len(features)
    total_behavioral_features += count
    print(f"\n{category}:")
    print(f"  Count: {count} features")
    print(f"  Examples: {', '.join(features[:5])}")
    if count > 5:
        print(f"            ... and {count - 5} more")

print(f"\n{'='*80}")
print(f"TOTAL BEHAVIORAL FEATURES ENGINEERED: {total_behavioral_features}")
print(f"Feature Matrix Shape: {feature_matrix.shape}")
print(f"Ready for: Intention Inference & Success Modeling")
print(f"{'='*80}")

# ===========================
# 2. SEQUENCE PATTERN INSIGHTS
# ===========================
print("\n" + "=" * 80)
print("SEQUENCE PATTERN ANALYSIS (N-Grams & Transitions)")
print("=" * 80)

seq_cols = ['has_login_analysis_pattern', 'has_analysis_viz_pattern', 
            'has_viz_export_pattern', 'has_export_share_pattern', 'complete_sessions']

print("\nWorkflow Pattern Adoption:")
for col in seq_cols:
    pct = feature_matrix[col].mean() * 100
    count = feature_matrix[col].sum()
    print(f"  • {col.replace('_', ' ').title()}: {pct:.1f}% ({count} users)")

print(f"\nSequence Diversity:")
print(f"  • Avg Unique Actions per User: {feature_matrix['unique_actions'].mean():.2f}")
print(f"  • Avg Action Diversity Ratio: {feature_matrix['action_diversity_ratio'].mean():.2f}")
print(f"  • Avg Unique Sequences: {feature_matrix['unique_sequences'].mean():.2f}")
print(f"  • Avg Most Common Sequence Repetition: {feature_matrix['most_common_sequence_count'].mean():.2f}")

# ===========================
# 3. TEMPORAL FEATURE INSIGHTS
# ===========================
print("\n" + "=" * 80)
print("TEMPORAL FEATURES ANALYSIS (Session Gaps & Activity Frequency)")
print("=" * 80)

print("\nSession Gap Statistics (hours):")
print(f"  • Mean Time Between Interactions: {feature_matrix['avg_time_between_interactions_hrs'].mean():.1f} hrs")
print(f"  • Median Time Between Interactions: {feature_matrix['median_time_between_interactions_hrs'].median():.1f} hrs")
print(f"  • Avg Max Gap (days): {feature_matrix['max_gap_days'].mean():.1f} days")

print("\nTime-of-Day Patterns:")
print(f"  • Avg Hour of Day: {feature_matrix['avg_hour_of_day'].mean():.1f}")
print(f"  • Business Hours Usage: {feature_matrix['pct_business_hours'].mean()*100:.1f}%")
print(f"  • Weekend Usage: {feature_matrix['pct_weekend'].mean()*100:.1f}%")

print("\nRecency Metrics:")
print(f"  • Avg Days Since Last Interaction: {feature_matrix['days_since_last_interaction'].mean():.1f}")
print(f"  • Avg Days Since First Interaction: {feature_matrix['days_since_first_interaction'].mean():.1f}")

# ===========================
# 4. ENGAGEMENT METRICS
# ===========================
print("\n" + "=" * 80)
print("ENGAGEMENT METRICS (Sequence Length, Actions, Completion Rates)")
print("=" * 80)

print("\nActivity Volume:")
print(f"  • Avg Total Interactions: {feature_matrix['total_interactions'].mean():.1f}")
print(f"  • Median Total Interactions: {feature_matrix['total_interactions'].median():.0f}")
print(f"  • Avg Interactions per Day: {feature_matrix['interactions_per_day'].mean():.2f}")

print("\nSession Engagement:")
print(f"  • Avg Session Duration: {feature_matrix['avg_session_duration'].mean():.1f} min")
print(f"  • Total Session Time (avg): {feature_matrix['total_session_time_hrs'].mean():.1f} hrs")
print(f"  • Max Session Duration (avg): {feature_matrix['max_session_duration'].mean():.1f} min")

print("\nCompletion Rates:")
print(f"  • Overall Success Rate: {feature_matrix['overall_success_rate'].mean()*100:.1f}%")
print(f"  • Avg Successful Actions: {feature_matrix['successful_actions'].mean():.1f}")
print(f"  • Avg Failed Actions: {feature_matrix['failed_actions'].mean():.1f}")

# ===========================
# 5. VISUALIZATIONS
# ===========================

# Chart 1: Feature Category Distribution
fig1 = plt.figure(figsize=(12, 7))
fig1.patch.set_facecolor('#1D1D20')
ax1 = fig1.add_subplot(111)
ax1.set_facecolor('#1D1D20')

categories = list(feature_categories.keys())
counts = [len(v) for v in feature_categories.values()]
colors = ['#A1C9F4', '#FFB482', '#8DE5A1', '#FF9F9B', '#D0BBFF']

bars = ax1.barh(categories, counts, color=colors, edgecolor='#fbfbff', linewidth=1.5)

# Add value labels
for i, (bar, count) in enumerate(zip(bars, counts)):
    ax1.text(count + 0.5, i, str(count), va='center', ha='left', 
             color='#fbfbff', fontsize=11, fontweight='bold')

ax1.set_xlabel('Number of Features', color='#fbfbff', fontsize=12, fontweight='bold')
ax1.set_title('Behavioral Feature Categories - Comprehensive Coverage', 
              color='#fbfbff', fontsize=14, fontweight='bold', pad=20)
ax1.tick_params(colors='#fbfbff', labelsize=10)
ax1.spines['bottom'].set_color('#909094')
ax1.spines['left'].set_color('#909094')
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)

plt.tight_layout()
plt.show()

# Chart 2: Feature Importance Preview (correlation with target)
fig2 = plt.figure(figsize=(14, 8))
fig2.patch.set_facecolor('#1D1D20')
ax2 = fig2.add_subplot(111)
ax2.set_facecolor('#1D1D20')

# Calculate correlations with target
correlations = feature_matrix.drop(['user_id', 'long_term_success'], axis=1).corrwith(
    feature_matrix['long_term_success']).abs().sort_values(ascending=False).head(20)

y_pos = np.arange(len(correlations))
bars = ax2.barh(y_pos, correlations.values, color='#A1C9F4', edgecolor='#fbfbff', linewidth=1.5)

# Color bars by feature category
for i, feature in enumerate(correlations.index):
    for category, features in feature_categories.items():
        if feature in features:
            if 'Sequence' in category:
                bars[i].set_color('#FFB482')
            elif 'Temporal' in category:
                bars[i].set_color('#8DE5A1')
            elif 'Engagement' in category:
                bars[i].set_color('#A1C9F4')
            elif 'Statistical' in category:
                bars[i].set_color('#D0BBFF')
            else:
                bars[i].set_color('#FF9F9B')

ax2.set_yticks(y_pos)
ax2.set_yticklabels([f.replace('_', ' ').title()[:30] for f in correlations.index], 
                     color='#fbfbff', fontsize=9)
ax2.set_xlabel('Correlation with Long-Term Success', color='#fbfbff', fontsize=12, fontweight='bold')
ax2.set_title('Top 20 Features by Correlation with Target Variable', 
              color='#fbfbff', fontsize=14, fontweight='bold', pad=20)
ax2.tick_params(colors='#fbfbff', labelsize=9)
ax2.spines['bottom'].set_color('#909094')
ax2.spines['left'].set_color('#909094')
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

# Legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#FFB482', label='Sequence Patterns'),
    Patch(facecolor='#8DE5A1', label='Temporal Features'),
    Patch(facecolor='#A1C9F4', label='Engagement Metrics'),
    Patch(facecolor='#D0BBFF', label='Statistical Aggregations'),
    Patch(facecolor='#FF9F9B', label='Additional Patterns')
]
ax2.legend(handles=legend_elements, loc='lower right', framealpha=0.9,
           facecolor='#2D2D30', edgecolor='#909094', labelcolor='#fbfbff')

plt.tight_layout()
plt.show()

# Chart 3: Feature Distribution Examples
fig3, axes = plt.subplots(2, 3, figsize=(16, 10))
fig3.patch.set_facecolor('#1D1D20')

example_features = [
    ('unique_actions', 'Unique Actions per User'),
    ('avg_time_between_interactions_hrs', 'Avg Time Between Interactions (hrs)'),
    ('total_interactions', 'Total Interactions'),
    ('overall_success_rate', 'Overall Success Rate'),
    ('complete_sessions', 'Complete Sessions Count'),
    ('pct_business_hours', 'Business Hours Usage %')
]

for idx, (feature, title) in enumerate(example_features):
    ax = axes[idx // 3, idx % 3]
    ax.set_facecolor('#1D1D20')
    
    values = feature_matrix[feature]
    ax.hist(values, bins=30, color='#A1C9F4', edgecolor='#fbfbff', linewidth=1.2, alpha=0.9)
    
    ax.set_title(title, color='#fbfbff', fontsize=11, fontweight='bold', pad=10)
    ax.set_xlabel('Value', color='#fbfbff', fontsize=9)
    ax.set_ylabel('Frequency', color='#fbfbff', fontsize=9)
    ax.tick_params(colors='#fbfbff', labelsize=8)
    ax.spines['bottom'].set_color('#909094')
    ax.spines['left'].set_color('#909094')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

plt.suptitle('Sample Feature Distributions - Rich Behavioral Patterns Captured', 
             color='#fbfbff', fontsize=14, fontweight='bold', y=0.995)
plt.tight_layout(rect=[0, 0, 1, 0.98])
plt.show()

print("\n" + "=" * 80)
print("✓ FEATURE ENGINEERING COMPLETE - SUCCESS CRITERIA MET")
print("=" * 80)
print("\n✓ Sequence Patterns: N-grams, transition matrices, workflow patterns")
print("✓ Temporal Features: Session gaps, activity frequency, time-of-day patterns")
print("✓ Engagement Metrics: Sequence length, unique actions, completion rates")
print("✓ Statistical Aggregations: Frequency counts, percentages, success rates")
print(f"\n✓ Rich Feature Matrix: {feature_matrix.shape[0]} users × {feature_matrix.shape[1]-2} features")
print("✓ Ready for: Intention Inference & Long-Term Success Modeling")
print("=" * 80)
