import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.gridspec import GridSpec

# Zerve design system
DARK_BG = '#1D1D20'
PRIMARY_TEXT = '#fbfbff'
SECONDARY_TEXT = '#909094'
HIGHLIGHT_YELLOW = '#ffd400'
SUCCESS_GREEN = '#17b26a'
WARNING_RED = '#f04438'
ZERVE_COLORS = ['#A1C9F4', '#FFB482', '#8DE5A1', '#FF9F9B', '#D0BBFF', 
                '#1F77B4', '#9467BD', '#8C564B', '#C49C94', '#E377C2']

plt.rcParams.update({
    'figure.facecolor': DARK_BG,
    'axes.facecolor': DARK_BG,
    'axes.edgecolor': PRIMARY_TEXT,
    'axes.labelcolor': PRIMARY_TEXT,
    'text.color': PRIMARY_TEXT,
    'xtick.color': PRIMARY_TEXT,
    'ytick.color': PRIMARY_TEXT,
    'grid.color': SECONDARY_TEXT,
    'grid.alpha': 0.2,
    'legend.facecolor': DARK_BG,
    'legend.edgecolor': PRIMARY_TEXT
})

def setup_dark_axis(ax):
    """Apply Zerve styling to axis."""
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(PRIMARY_TEXT)
    ax.spines['left'].set_color(PRIMARY_TEXT)
    ax.tick_params(colors=PRIMARY_TEXT)

print("=" * 70)
print("REAL-TIME PREDICTION VISUALIZATION")
print("=" * 70)

# Create comprehensive visualization
viz_fig = plt.figure(figsize=(16, 12))
gs = GridSpec(3, 3, figure=viz_fig, hspace=0.35, wspace=0.35)

# 1. Intention Distribution Pie Chart
ax1 = viz_fig.add_subplot(gs[0, 0])
intention_counts = predictions_df['intention_label'].value_counts()
colors_intention = [ZERVE_COLORS[i % len(ZERVE_COLORS)] for i in range(len(intention_counts))]
wedges, texts, autotexts = ax1.pie(
    intention_counts, 
    labels=intention_counts.index, 
    autopct='%1.1f%%',
    colors=colors_intention,
    startangle=90,
    textprops={'color': PRIMARY_TEXT, 'fontsize': 10, 'fontweight': 'bold'}
)
for autotext in autotexts:
    autotext.set_color(DARK_BG)
    autotext.set_fontweight('bold')
ax1.set_title('User Intention Distribution', fontsize=12, fontweight='bold', 
              color=PRIMARY_TEXT, pad=15)

# 2. Success Probability Distribution
ax2 = viz_fig.add_subplot(gs[0, 1])
ax2.hist(predictions_df['success_probability'], bins=30, color=ZERVE_COLORS[0], 
         edgecolor=PRIMARY_TEXT, linewidth=0.5, alpha=0.8)
ax2.axvline(predictions_df['success_probability'].mean(), color=HIGHLIGHT_YELLOW, 
            linestyle='--', linewidth=2, label=f"Mean: {predictions_df['success_probability'].mean():.1f}%")
ax2.set_xlabel('Success Probability (%)', fontsize=11, fontweight='bold', color=PRIMARY_TEXT)
ax2.set_ylabel('Count', fontsize=11, fontweight='bold', color=PRIMARY_TEXT)
ax2.set_title('Success Probability Distribution', fontsize=12, fontweight='bold', 
              color=PRIMARY_TEXT, pad=15)
ax2.legend(framealpha=0.9, labelcolor=PRIMARY_TEXT, fontsize=9)
setup_dark_axis(ax2)

# 3. Confidence Score Distribution
ax3 = viz_fig.add_subplot(gs[0, 2])
ax3.hist(predictions_df['confidence_score'], bins=30, color=ZERVE_COLORS[2], 
         edgecolor=PRIMARY_TEXT, linewidth=0.5, alpha=0.8)
ax3.axvline(predictions_df['confidence_score'].mean(), color=WARNING_RED, 
            linestyle='--', linewidth=2, label=f"Mean: {predictions_df['confidence_score'].mean():.1f}%")
ax3.set_xlabel('Confidence Score (%)', fontsize=11, fontweight='bold', color=PRIMARY_TEXT)
ax3.set_ylabel('Count', fontsize=11, fontweight='bold', color=PRIMARY_TEXT)
ax3.set_title('Prediction Confidence Distribution', fontsize=12, fontweight='bold', 
              color=PRIMARY_TEXT, pad=15)
ax3.legend(framealpha=0.9, labelcolor=PRIMARY_TEXT, fontsize=9)
setup_dark_axis(ax3)

# 4. Latency Over Time
ax4 = viz_fig.add_subplot(gs[1, :])
time_points = range(len(predictions_df))
ax4.plot(time_points, predictions_df['total_latency_ms'], 
         color=ZERVE_COLORS[1], linewidth=1.5, alpha=0.7, label='Total Latency')
ax4.plot(time_points, predictions_df['feature_extraction_time_ms'], 
         color=ZERVE_COLORS[4], linewidth=1.5, alpha=0.7, label='Feature Extraction')
ax4.axhline(predictions_df['total_latency_ms'].median(), color=HIGHLIGHT_YELLOW, 
            linestyle='--', linewidth=2, label=f"Median: {predictions_df['total_latency_ms'].median():.1f}ms")
ax4.axhline(100, color=WARNING_RED, linestyle=':', linewidth=2, label='Target: 100ms')
ax4.set_xlabel('Event Number', fontsize=11, fontweight='bold', color=PRIMARY_TEXT)
ax4.set_ylabel('Latency (ms)', fontsize=11, fontweight='bold', color=PRIMARY_TEXT)
ax4.set_title('Real-Time Prediction Latency Over Time', fontsize=12, fontweight='bold', 
              color=PRIMARY_TEXT, pad=15)
ax4.legend(framealpha=0.9, labelcolor=PRIMARY_TEXT, fontsize=9, loc='upper right')
setup_dark_axis(ax4)
ax4.grid(True, alpha=0.2)

# 5. Success Probability by Intention
ax5 = viz_fig.add_subplot(gs[2, 0])
intention_success = predictions_df.groupby('intention_label')['success_probability'].mean().sort_values()
bars_success = ax5.barh(range(len(intention_success)), intention_success, 
                        color=[ZERVE_COLORS[i % len(ZERVE_COLORS)] for i in range(len(intention_success))],
                        edgecolor=PRIMARY_TEXT, linewidth=1)
ax5.set_yticks(range(len(intention_success)))
ax5.set_yticklabels(intention_success.index, fontsize=10, color=PRIMARY_TEXT)
ax5.set_xlabel('Avg Success Probability (%)', fontsize=11, fontweight='bold', color=PRIMARY_TEXT)
ax5.set_title('Success Probability by Intention', fontsize=12, fontweight='bold', 
              color=PRIMARY_TEXT, pad=15)
for i_bar, val in enumerate(intention_success):
    ax5.text(val + 1, i_bar, f'{val:.1f}%', va='center', fontsize=9, 
             color=PRIMARY_TEXT, fontweight='bold')
setup_dark_axis(ax5)

# 6. Confidence Score by Intention
ax6 = viz_fig.add_subplot(gs[2, 1])
intention_confidence = predictions_df.groupby('intention_label')['confidence_score'].mean().sort_values()
bars_conf = ax6.barh(range(len(intention_confidence)), intention_confidence, 
                     color=[ZERVE_COLORS[i % len(ZERVE_COLORS)] for i in range(len(intention_confidence))],
                     edgecolor=PRIMARY_TEXT, linewidth=1)
ax6.set_yticks(range(len(intention_confidence)))
ax6.set_yticklabels(intention_confidence.index, fontsize=10, color=PRIMARY_TEXT)
ax6.set_xlabel('Avg Confidence Score (%)', fontsize=11, fontweight='bold', color=PRIMARY_TEXT)
ax6.set_title('Confidence Score by Intention', fontsize=12, fontweight='bold', 
              color=PRIMARY_TEXT, pad=15)
for i_bar, val in enumerate(intention_confidence):
    ax6.text(val + 1, i_bar, f'{val:.1f}%', va='center', fontsize=9, 
             color=PRIMARY_TEXT, fontweight='bold')
setup_dark_axis(ax6)

# 7. Scatter: Success Probability vs Confidence Score
ax7 = viz_fig.add_subplot(gs[2, 2])
intention_colors_map = {
    intention: ZERVE_COLORS[i % len(ZERVE_COLORS)] 
    for i, intention in enumerate(predictions_df['intention_label'].unique())
}
for intention in predictions_df['intention_label'].unique():
    mask = predictions_df['intention_label'] == intention
    ax7.scatter(
        predictions_df.loc[mask, 'success_probability'],
        predictions_df.loc[mask, 'confidence_score'],
        c=intention_colors_map[intention],
        label=intention,
        alpha=0.6,
        s=30,
        edgecolors=PRIMARY_TEXT,
        linewidth=0.5
    )
ax7.set_xlabel('Success Probability (%)', fontsize=11, fontweight='bold', color=PRIMARY_TEXT)
ax7.set_ylabel('Confidence Score (%)', fontsize=11, fontweight='bold', color=PRIMARY_TEXT)
ax7.set_title('Success Probability vs Confidence', fontsize=12, fontweight='bold', 
              color=PRIMARY_TEXT, pad=15)
ax7.legend(framealpha=0.9, labelcolor=PRIMARY_TEXT, fontsize=8, loc='lower right')
setup_dark_axis(ax7)
ax7.grid(True, alpha=0.2)

plt.suptitle('Real-Time Prediction System Analysis', fontsize=16, fontweight='bold', 
             color=PRIMARY_TEXT, y=0.995)

print("\n✅ Visualization created successfully!")
print(f"   • 7 charts showing prediction performance and distribution")
print(f"   • Analyzing {len(predictions_df)} predictions")
print(f"   • {predictions_df['intention_label'].nunique()} intention categories")

# Print detailed statistics
print("\n" + "=" * 70)
print("DETAILED STATISTICS")
print("=" * 70)

print(f"\n📊 Intention Analysis:")
for intention in predictions_df['intention_label'].unique():
    intention_data = predictions_df[predictions_df['intention_label'] == intention]
    print(f"\n  {intention}:")
    print(f"    • Count: {len(intention_data)} predictions")
    print(f"    • Avg success prob: {intention_data['success_probability'].mean():.1f}%")
    print(f"    • Avg confidence: {intention_data['confidence_score'].mean():.1f}%")
    print(f"    • Avg latency: {intention_data['total_latency_ms'].mean():.2f}ms")
    print(f"    • Avg sequence length: {intention_data['event_sequence_length'].mean():.1f}")

print(f"\n⚡ Performance Summary:")
print(f"  • Total predictions: {len(predictions_df)}")
print(f"  • Avg latency: {predictions_df['total_latency_ms'].mean():.2f}ms")
print(f"  • Median latency: {predictions_df['total_latency_ms'].median():.2f}ms")
print(f"  • P95 latency: {predictions_df['total_latency_ms'].quantile(0.95):.2f}ms")
print(f"  • Max latency: {predictions_df['total_latency_ms'].max():.2f}ms")
print(f"  • Latency target met: {predictions_df['total_latency_ms'].median() < 100}")

print(f"\n🎯 Prediction Quality:")
print(f"  • Avg success probability: {predictions_df['success_probability'].mean():.1f}%")
print(f"  • Success prob std: {predictions_df['success_probability'].std():.1f}%")
print(f"  • Avg confidence score: {predictions_df['confidence_score'].mean():.1f}%")
print(f"  • Confidence std: {predictions_df['confidence_score'].std():.1f}%")
print(f"  • Intention coverage: {predictions_df['intention_label'].nunique()} categories")

print("\n" + "=" * 70)
print("✅ REAL-TIME PREDICTION SYSTEM COMPLETE")
print("=" * 70)
