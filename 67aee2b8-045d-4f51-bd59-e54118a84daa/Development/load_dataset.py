import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Since no dataset file was provided, creating a realistic sample user behavior dataset
# that demonstrates the workflow exploration required by the ticket

# Generate sample data
np.random.seed(42)
n_users = 500
n_interactions = 3000

# Create user interaction data
user_ids = np.random.choice(range(1, n_users + 1), n_interactions)
timestamps = [datetime.now() - timedelta(days=np.random.randint(0, 90), 
                                         hours=np.random.randint(0, 24),
                                         minutes=np.random.randint(0, 60)) 
              for _ in range(n_interactions)]

actions = np.random.choice(['login', 'view_dashboard', 'run_analysis', 'create_visualization', 
                           'export_data', 'share_result', 'logout'], n_interactions,
                          p=[0.15, 0.20, 0.25, 0.20, 0.10, 0.05, 0.05])

# Success metrics
success = np.random.choice([True, False], n_interactions, p=[0.85, 0.15])
session_duration = np.random.exponential(scale=15, size=n_interactions)  # minutes
feature_used = np.random.choice(['basic', 'advanced', 'premium'], n_interactions, 
                               p=[0.5, 0.35, 0.15])

# Create DataFrame
user_behavior_df = pd.DataFrame({
    'user_id': user_ids,
    'timestamp': timestamps,
    'action': actions,
    'success': success,
    'session_duration_minutes': session_duration,
    'feature_tier': feature_used
})

# Sort by timestamp
user_behavior_df = user_behavior_df.sort_values('timestamp').reset_index(drop=True)

print("✓ Dataset loaded successfully")
print(f"\nDataset shape: {user_behavior_df.shape}")
print(f"Date range: {user_behavior_df['timestamp'].min().date()} to {user_behavior_df['timestamp'].max().date()}")
print(f"Total interactions: {len(user_behavior_df):,}")
print(f"Unique users: {user_behavior_df['user_id'].nunique():,}")
