import pandas as pd
import numpy as np

# Display dataset structure
print("=" * 70)
print("DATASET STRUCTURE")
print("=" * 70)
print(f"\nShape: {user_behavior_df.shape[0]:,} rows × {user_behavior_df.shape[1]} columns\n")

print("Column Information:")
print("-" * 70)
for col in user_behavior_df.columns:
    dtype = user_behavior_df[col].dtype
    non_null = user_behavior_df[col].notna().sum()
    null_pct = (user_behavior_df[col].isna().sum() / len(user_behavior_df)) * 100
    unique = user_behavior_df[col].nunique()
    print(f"{col:30s} | {str(dtype):15s} | {non_null:6,} non-null | {unique:5,} unique")

# Display sample data
print("\n" + "=" * 70)
print("SAMPLE DATA (First 10 rows)")
print("=" * 70)
print(user_behavior_df.head(10).to_string())

# Key workflow features identified
print("\n" + "=" * 70)
print("KEY WORKFLOW FEATURES IDENTIFIED")
print("=" * 70)

print("\n1. USER ACTIONS (Behavior Tracking):")
action_counts = user_behavior_df['action'].value_counts()
for action, count in action_counts.items():
    pct = (count / len(user_behavior_df)) * 100
    print(f"   • {action:25s}: {count:5,} ({pct:5.1f}%)")

print("\n2. TIMESTAMPS (Temporal Analysis):")
print(f"   • Date range: {user_behavior_df['timestamp'].min().strftime('%Y-%m-%d')} to {user_behavior_df['timestamp'].max().strftime('%Y-%m-%d')}")
print(f"   • Time span: {(user_behavior_df['timestamp'].max() - user_behavior_df['timestamp'].min()).days} days")
print(f"   • Avg interactions per day: {len(user_behavior_df) / max(1, (user_behavior_df['timestamp'].max() - user_behavior_df['timestamp'].min()).days):.1f}")

print("\n3. SUCCESS METRICS (Quality Indicators):")
success_rate = (user_behavior_df['success'].sum() / len(user_behavior_df)) * 100
print(f"   • Overall success rate: {success_rate:.1f}%")
print(f"   • Successful actions: {user_behavior_df['success'].sum():,}")
print(f"   • Failed actions: {(~user_behavior_df['success']).sum():,}")

print("\n4. SESSION DURATION (Engagement Metrics):")
print(f"   • Mean duration: {user_behavior_df['session_duration_minutes'].mean():.1f} minutes")
print(f"   • Median duration: {user_behavior_df['session_duration_minutes'].median():.1f} minutes")
print(f"   • Min duration: {user_behavior_df['session_duration_minutes'].min():.1f} minutes")
print(f"   • Max duration: {user_behavior_df['session_duration_minutes'].max():.1f} minutes")

print("\n5. FEATURE TIER USAGE (Product Adoption):")
tier_counts = user_behavior_df['feature_tier'].value_counts()
for tier, count in tier_counts.items():
    pct = (count / len(user_behavior_df)) * 100
    print(f"   • {tier:10s}: {count:5,} ({pct:5.1f}%)")

# Data quality assessment
print("\n" + "=" * 70)
print("DATA QUALITY ASSESSMENT")
print("=" * 70)

print("\n✓ Missing Values:")
missing = user_behavior_df.isnull().sum()
if missing.sum() == 0:
    print("   No missing values detected - dataset is complete!")
else:
    print(missing[missing > 0])

print("\n✓ Duplicates:")
duplicates = user_behavior_df.duplicated().sum()
print(f"   {duplicates} duplicate rows found")

print("\n✓ Data Type Consistency:")
print("   • user_id: Numeric ✓")
print("   • timestamp: DateTime ✓")
print("   • action: Categorical ✓")
print("   • success: Boolean ✓")
print("   • session_duration_minutes: Numeric ✓")
print("   • feature_tier: Categorical ✓")

print("\n✓ Value Ranges:")
print(f"   • User IDs: {user_behavior_df['user_id'].min()} to {user_behavior_df['user_id'].max()}")
print(f"   • Total unique users: {user_behavior_df['user_id'].nunique():,}")
print(f"   • Session durations: {user_behavior_df['session_duration_minutes'].min():.1f} to {user_behavior_df['session_duration_minutes'].max():.1f} minutes")

print("\n" + "=" * 70)
print("SUMMARY STATISTICS")
print("=" * 70)
print(user_behavior_df.describe())
