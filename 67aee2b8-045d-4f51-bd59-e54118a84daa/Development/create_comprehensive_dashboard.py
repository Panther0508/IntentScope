import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Zerve design system colors
BACKGROUND = '#1D1D20'
PRIMARY_TEXT = '#fbfbff'
SECONDARY_TEXT = '#909094'
COLORS = ['#A1C9F4', '#FFB482', '#8DE5A1', '#FF9F9B', '#D0BBFF', '#1F77B4', '#9467BD', '#8C564B']
HIGHLIGHT = '#ffd400'
SUCCESS = '#17b26a'
WARNING = '#f04438'

plt.rcParams['figure.facecolor'] = BACKGROUND
plt.rcParams['axes.facecolor'] = BACKGROUND
plt.rcParams['axes.edgecolor'] = PRIMARY_TEXT
plt.rcParams['text.color'] = PRIMARY_TEXT
plt.rcParams['axes.labelcolor'] = PRIMARY_TEXT
plt.rcParams['xtick.color'] = PRIMARY_TEXT
plt.rcParams['ytick.color'] = PRIMARY_TEXT
plt.rcParams['legend.facecolor'] = BACKGROUND
plt.rcParams['legend.edgecolor'] = PRIMARY_TEXT

# ===============================
# 1. INTENTION DISTRIBUTION PIE CHART
# ===============================
dashboard_fig1, dashboard_ax1 = plt.subplots(figsize=(10, 8))

dashboard_intention_dist = intention_distribution.sort_values(ascending=False)
# Use the actual index values from intention_distribution instead of hardcoded labels
dashboard_labels = dashboard_intention_dist.index.tolist()
dashboard_values = dashboard_intention_dist.values.tolist()
dashboard_colors_pie = [COLORS[_i % len(COLORS)] for _i in range(len(dashboard_labels))]

wedges, texts, autotexts = dashboard_ax1.pie(dashboard_values, labels=dashboard_labels, autopct='%1.1f%%',
                                     colors=dashboard_colors_pie, startangle=90,
                                     textprops={'color': PRIMARY_TEXT, 'fontsize': 12, 'weight': 'bold'})

for autotext in autotexts:
    autotext.set_color(BACKGROUND)
    autotext.set_fontsize(11)
    autotext.set_weight('bold')

dashboard_ax1.set_title('IntentScope: User Intention Distribution', 
              fontsize=16, weight='bold', color=PRIMARY_TEXT, pad=20)
plt.tight_layout()
print("✓ Chart 1: Intention Distribution Pie Chart created")

# ===============================
# 2. SUCCESS PROBABILITY HISTOGRAM
# ===============================
dashboard_fig2, dashboard_ax2 = plt.subplots(figsize=(12, 7))

# Use correct column name from gb_results_df
dashboard_success_probs = gb_results_df['gb_success_prob'].values
dashboard_ax2.hist(dashboard_success_probs, bins=30, color=COLORS[3], edgecolor=PRIMARY_TEXT, alpha=0.85, linewidth=1.5)

dashboard_ax2.axvline(dashboard_success_probs.mean(), color=HIGHLIGHT, linestyle='--', linewidth=2.5, 
            label=f'Mean: {dashboard_success_probs.mean():.2%}')
dashboard_ax2.axvline(np.median(dashboard_success_probs), color=SUCCESS, linestyle='--', linewidth=2.5,
            label=f'Median: {np.median(dashboard_success_probs):.2%}')

dashboard_ax2.set_xlabel('Success Probability', fontsize=13, weight='bold', color=PRIMARY_TEXT)
dashboard_ax2.set_ylabel('Number of Users', fontsize=13, weight='bold', color=PRIMARY_TEXT)
dashboard_ax2.set_title('Distribution of User Success Probabilities', 
              fontsize=16, weight='bold', color=PRIMARY_TEXT, pad=20)
dashboard_ax2.legend(loc='upper left', fontsize=11, framealpha=0.9)
dashboard_ax2.spines['top'].set_visible(False)
dashboard_ax2.spines['right'].set_visible(False)
plt.tight_layout()
print("✓ Chart 2: Success Probability Histogram created")

# ===============================
# 3. TOP PREDICTIVE BEHAVIORS BAR CHART
# ===============================
dashboard_fig3, dashboard_ax3 = plt.subplots(figsize=(12, 8))

dashboard_top_behaviors = feature_importance_gb.nlargest(12, 'importance')
dashboard_bars = dashboard_ax3.barh(range(len(dashboard_top_behaviors)), dashboard_top_behaviors['importance'], 
                color=COLORS[4], edgecolor=PRIMARY_TEXT, linewidth=1.2)

for _i, (_idx, _row) in enumerate(dashboard_top_behaviors.iterrows()):
    dashboard_ax3.text(_row['importance'] + 0.002, _i, f"{_row['importance']:.3f}", 
             va='center', fontsize=10, color=PRIMARY_TEXT, weight='bold')

dashboard_ax3.set_yticks(range(len(dashboard_top_behaviors)))
dashboard_ax3.set_yticklabels(dashboard_top_behaviors['feature'], fontsize=11)
dashboard_ax3.set_xlabel('Feature Importance Score', fontsize=13, weight='bold', color=PRIMARY_TEXT)
dashboard_ax3.set_title('Top 12 Predictive Behaviors for User Success', 
              fontsize=16, weight='bold', color=PRIMARY_TEXT, pad=20)
dashboard_ax3.spines['top'].set_visible(False)
dashboard_ax3.spines['right'].set_visible(False)
dashboard_ax3.grid(axis='x', alpha=0.2, color=SECONDARY_TEXT)
plt.tight_layout()
print("✓ Chart 3: Top Predictive Behaviors Bar Chart created")

# ===============================
# 4. BEHAVIOR SEQUENCE FLOW DIAGRAM
# ===============================
dashboard_fig4, dashboard_ax4 = plt.subplots(figsize=(14, 8))

# Get most common action sequences
dashboard_action_sequence_patterns = user_behavior_df.groupby('user_id')['action'].apply(lambda x: ' → '.join(x.head(5))).value_counts().head(10)

dashboard_y_positions = np.arange(len(dashboard_action_sequence_patterns))
dashboard_bars4 = dashboard_ax4.barh(dashboard_y_positions, dashboard_action_sequence_patterns.values, 
                color=COLORS[5], edgecolor=PRIMARY_TEXT, alpha=0.85, linewidth=1.2)

dashboard_ax4.set_yticks(dashboard_y_positions)
dashboard_ax4.set_yticklabels([seq[:50] + '...' if len(seq) > 50 else seq 
                      for seq in dashboard_action_sequence_patterns.index], fontsize=9)
dashboard_ax4.set_xlabel('Frequency', fontsize=13, weight='bold', color=PRIMARY_TEXT)
dashboard_ax4.set_title('Top 10 Most Common User Behavior Sequences', 
              fontsize=16, weight='bold', color=PRIMARY_TEXT, pad=20)

for _i, _val in enumerate(dashboard_action_sequence_patterns.values):
    dashboard_ax4.text(_val + 0.5, _i, str(_val), va='center', fontsize=10, 
             color=PRIMARY_TEXT, weight='bold')

dashboard_ax4.spines['top'].set_visible(False)
dashboard_ax4.spines['right'].set_visible(False)
dashboard_ax4.grid(axis='x', alpha=0.2, color=SECONDARY_TEXT)
plt.tight_layout()
print("✓ Chart 4: Behavior Sequence Flow Diagram created")

# ===============================
# 5. CORRELATION HEATMAP: INTENTIONS VS SUCCESS
# ===============================
dashboard_fig5, dashboard_ax5 = plt.subplots(figsize=(12, 8))

# Create correlation matrix using existing columns in results_intent_df
dashboard_intention_features = results_intent_df.groupby('intention_label')[
    ['total_interactions', 'unique_actions', 'advanced_usage_count', 'long_term_success']
].mean()

# Heatmap data
dashboard_heatmap_data = dashboard_intention_features.T
dashboard_im = dashboard_ax5.imshow(dashboard_heatmap_data.values, cmap='YlOrRd', aspect='auto')

dashboard_ax5.set_xticks(range(len(dashboard_heatmap_data.columns)))
dashboard_ax5.set_xticklabels(dashboard_heatmap_data.columns, fontsize=11, rotation=45, ha='right')
dashboard_ax5.set_yticks(range(len(dashboard_heatmap_data.index)))
dashboard_ax5.set_yticklabels(dashboard_heatmap_data.index, fontsize=11)

for _i in range(len(dashboard_heatmap_data.index)):
    for _j in range(len(dashboard_heatmap_data.columns)):
        _text = dashboard_ax5.text(_j, _i, f'{dashboard_heatmap_data.values[_i, _j]:.2f}',
                       ha='center', va='center', color=BACKGROUND, 
                       fontsize=10, weight='bold')

dashboard_ax5.set_title('User Intention Profiles: Key Metrics Heatmap', 
              fontsize=16, weight='bold', color=PRIMARY_TEXT, pad=20)
dashboard_cbar = plt.colorbar(dashboard_im, ax=dashboard_ax5)
dashboard_cbar.set_label('Metric Value', fontsize=12, color=PRIMARY_TEXT)
dashboard_cbar.ax.yaxis.set_tick_params(color=PRIMARY_TEXT)
plt.setp(plt.getp(dashboard_cbar.ax.axes, 'yticklabels'), color=PRIMARY_TEXT)
plt.tight_layout()
print("✓ Chart 5: Correlation Heatmap created")

# ===============================
# 6. USER SEGMENT COMPARISON CHARTS
# ===============================
dashboard_fig6, (dashboard_ax6a, dashboard_ax6b) = plt.subplots(1, 2, figsize=(16, 7))

# 6a: Success rate by intention (using gb_intention_label from gb_results_df)
dashboard_intention_success = gb_results_df.groupby('gb_intention_label')['true_success'].mean().sort_values(ascending=False)
dashboard_bars_6a = dashboard_ax6a.bar(range(len(dashboard_intention_success)), dashboard_intention_success.values, 
                   color=[COLORS[_i % len(COLORS)] for _i in range(len(dashboard_intention_success))], 
                   edgecolor=PRIMARY_TEXT, linewidth=1.5)

dashboard_ax6a.set_xticks(range(len(dashboard_intention_success)))
dashboard_ax6a.set_xticklabels(dashboard_intention_success.index, fontsize=11, rotation=45, ha='right')
dashboard_ax6a.set_ylabel('Success Rate', fontsize=12, weight='bold', color=PRIMARY_TEXT)
dashboard_ax6a.set_title('Success Rate by User Intention', fontsize=14, weight='bold', 
               color=PRIMARY_TEXT, pad=15)

for _i, _bar in enumerate(dashboard_bars_6a):
    _height = _bar.get_height()
    dashboard_ax6a.text(_bar.get_x() + _bar.get_width()/2., _height,
             f'{_height:.1%}', ha='center', va='bottom', 
             fontsize=11, color=PRIMARY_TEXT, weight='bold')

dashboard_ax6a.spines['top'].set_visible(False)
dashboard_ax6a.spines['right'].set_visible(False)
dashboard_ax6a.set_ylim(0, max(dashboard_intention_success.values) * 1.15)

# 6b: Engagement metrics by intention
dashboard_engagement_metrics = gb_results_df.groupby('gb_intention_label')[
    ['total_interactions', 'unique_actions']].mean()

dashboard_x_positions = np.arange(len(dashboard_engagement_metrics))
dashboard_width = 0.35

dashboard_bars1_6b = dashboard_ax6b.bar(dashboard_x_positions - dashboard_width/2, dashboard_engagement_metrics['total_interactions'], 
                    dashboard_width, label='Total Interactions', color=COLORS[0], 
                    edgecolor=PRIMARY_TEXT, linewidth=1.2)
dashboard_bars2_6b = dashboard_ax6b.bar(dashboard_x_positions + dashboard_width/2, dashboard_engagement_metrics['unique_actions'], 
                    dashboard_width, label='Unique Actions', color=COLORS[1], 
                    edgecolor=PRIMARY_TEXT, linewidth=1.2)

dashboard_ax6b.set_xticks(dashboard_x_positions)
dashboard_ax6b.set_xticklabels(dashboard_engagement_metrics.index, fontsize=11, rotation=45, ha='right')
dashboard_ax6b.set_ylabel('Count', fontsize=12, weight='bold', color=PRIMARY_TEXT)
dashboard_ax6b.set_title('Engagement Metrics by User Intention', fontsize=14, 
               weight='bold', color=PRIMARY_TEXT, pad=15)
dashboard_ax6b.legend(loc='upper left', fontsize=11, framealpha=0.9)
dashboard_ax6b.spines['top'].set_visible(False)
dashboard_ax6b.spines['right'].set_visible(False)

plt.tight_layout()
print("✓ Chart 6: User Segment Comparison Charts created")

# ===============================
# SUMMARY STATISTICS
# ===============================
print("\n" + "="*70)
print("INTENTSCOPE ANALYSIS: KEY INSIGHTS & SUMMARY STATISTICS")
print("="*70)

print(f"\n📊 OVERALL METRICS:")
print(f"   • Total Users Analyzed: {len(gb_results_df):,}")
print(f"   • Total Interactions: {len(user_behavior_df):,}")
print(f"   • Average Success Probability: {dashboard_success_probs.mean():.1%}")
print(f"   • Median Success Probability: {np.median(dashboard_success_probs):.1%}")

print(f"\n🎯 INTENTION DISTRIBUTION:")
for dashboard_intent, dashboard_count in intention_distribution.items():
    dashboard_pct = (dashboard_count / len(results_intent_df)) * 100
    print(f"   • {dashboard_intent}: {dashboard_count} users ({dashboard_pct:.1f}%)")

print(f"\n⭐ TOP 5 PREDICTIVE BEHAVIORS:")
for _i, (_idx, _row) in enumerate(feature_importance_gb.head(5).iterrows(), 1):
    print(f"   {_i}. {_row['feature']}: {_row['importance']:.4f}")

print(f"\n💡 USER SEGMENT PERFORMANCE:")
for dashboard_intent in dashboard_intention_success.index:
    dashboard_success_rate = dashboard_intention_success[dashboard_intent]
    dashboard_avg_interactions = dashboard_engagement_metrics.loc[dashboard_intent, 'total_interactions']
    print(f"   • {dashboard_intent}:")
    print(f"     - Success Rate: {dashboard_success_rate:.1%}")
    print(f"     - Avg Interactions: {dashboard_avg_interactions:.1f}")

print(f"\n🔍 MODEL PERFORMANCE:")
print(f"   • Test Accuracy: {gb_test_acc:.1%}")
print(f"   • Test AUC-ROC: {gb_test_auc:.1%}")
print(f"   • Test F1 Score: {gb_test_f1:.1%}")

print("\n" + "="*70)
print("Dashboard complete! All visualizations generated successfully.")
print("="*70)