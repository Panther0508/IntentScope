import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

print("=" * 70)
print("PREPARING SEQUENCE DATA FOR LSTM/TRANSFORMER MODELS")
print("=" * 70)

# Get raw sequence data sorted by user and time
df_seq = df_sorted.copy()

# Encode actions as integers for neural networks
action_encoder = LabelEncoder()
df_seq['action_encoded'] = action_encoder.fit_transform(df_seq['action'])

# Encode feature tiers
tier_encoder = LabelEncoder()
df_seq['tier_encoded'] = tier_encoder.fit_transform(df_seq['feature_tier'])

print(f"\n✓ Action Encoding Mapping:")
for i, action in enumerate(action_encoder.classes_):
    print(f"  {i}: {action}")

print(f"\n✓ Feature Tier Encoding Mapping:")
for i, tier in enumerate(tier_encoder.classes_):
    print(f"  {i}: {tier}")

# Create time-based features for each interaction
df_seq['hour'] = df_seq['timestamp'].dt.hour
df_seq['day_of_week'] = df_seq['timestamp'].dt.dayofweek
df_seq['is_weekend'] = df_seq['day_of_week'].isin([5, 6]).astype(int)

# Calculate time since previous interaction per user
df_seq['time_since_prev_hrs'] = df_seq.groupby('user_id')['timestamp'].diff().dt.total_seconds() / 3600
df_seq['time_since_prev_hrs'] = df_seq['time_since_prev_hrs'].fillna(0)

# Get sequence position for each user
df_seq['sequence_position'] = df_seq.groupby('user_id').cumcount()

print(f"\n✓ Sequence Data Shape: {df_seq.shape}")
print(f"✓ Total Users: {df_seq['user_id'].nunique()}")
print(f"✓ Total Interactions: {len(df_seq)}")
print(f"✓ Avg Interactions per User: {len(df_seq) / df_seq['user_id'].nunique():.1f}")

# Create sequences for each user with padding
max_seq_length = df_seq.groupby('user_id').size().max()
median_seq_length = df_seq.groupby('user_id').size().median()

print(f"\n✓ Sequence Length Statistics:")
print(f"  • Maximum sequence length: {max_seq_length}")
print(f"  • Median sequence length: {median_seq_length}")
print(f"  • Min sequence length: {df_seq.groupby('user_id').size().min()}")

# Create sequence arrays for LSTM input
# Features: action_encoded, tier_encoded, success, session_duration, hour, time_since_prev
sequence_features = ['action_encoded', 'tier_encoded', 'success', 
                     'session_duration_minutes', 'hour', 'time_since_prev_hrs', 
                     'is_weekend', 'day_of_week']

print(f"\n✓ Sequence Features (per timestep): {len(sequence_features)}")
for feat in sequence_features:
    print(f"  • {feat}")

# Build user sequences with labels
user_sequences = []
user_ids_seq = []
labels_seq = []

# Get user labels from user_metrics
user_labels = user_metrics.set_index('user_id')['long_term_success'].to_dict()

for user_id in df_seq['user_id'].unique():
    if user_id in user_labels:
        user_data = df_seq[df_seq['user_id'] == user_id][sequence_features].values
        user_sequences.append(user_data)
        user_ids_seq.append(user_id)
        labels_seq.append(user_labels[user_id])

print(f"\n✓ Built {len(user_sequences)} user sequences")
print(f"✓ Positive class (successful users): {sum(labels_seq)} ({100*np.mean(labels_seq):.1f}%)")

# Set target sequence length (use 75th percentile to balance between coverage and efficiency)
target_seq_length = int(np.percentile([len(seq) for seq in user_sequences], 75))
print(f"\n✓ Using target sequence length: {target_seq_length} (75th percentile)")
print(f"  This covers {100 * np.mean([len(seq) >= target_seq_length for seq in user_sequences]):.1f}% of users fully")

# For sequences longer than target, we'll take the most recent interactions
# For shorter sequences, we'll pad with zeros
sequences_padded = []
for seq in user_sequences:
    if len(seq) > target_seq_length:
        # Take most recent interactions
        sequences_padded.append(seq[-target_seq_length:])
    else:
        # Pad with zeros at the beginning
        pad_length = target_seq_length - len(seq)
        padding = np.zeros((pad_length, len(sequence_features)))
        sequences_padded.append(np.vstack([padding, seq]))

sequences_padded = np.array(sequences_padded)
labels_array = np.array(labels_seq)

print(f"\n✓ Padded Sequence Array Shape: {sequences_padded.shape}")
print(f"  • (num_users, max_sequence_length, num_features_per_timestep)")
print(f"  • {sequences_padded.shape[0]} users")
print(f"  • {sequences_padded.shape[1]} timesteps (sequence length)")
print(f"  • {sequences_padded.shape[2]} features per timestep")

# Create sequence masks to identify real vs padded data
sequence_masks = np.zeros((len(user_sequences), target_seq_length))
for i, seq in enumerate(user_sequences):
    actual_length = min(len(seq), target_seq_length)
    sequence_masks[i, -actual_length:] = 1

print(f"\n✓ Created sequence masks: {sequence_masks.shape}")

# Split into train/test (match the split from prepare_modeling_dataset)
X_seq_train, X_seq_test, y_seq_train, y_seq_test, mask_train, mask_test, ids_train, ids_test = train_test_split(
    sequences_padded, labels_array, sequence_masks, user_ids_seq,
    test_size=0.2, random_state=42, stratify=labels_array
)

print(f"\n✓ Train/Test Split:")
print(f"  • Training sequences: {X_seq_train.shape[0]} ({100*y_seq_train.mean():.1f}% positive)")
print(f"  • Test sequences: {X_seq_test.shape[0]} ({100*y_seq_test.mean():.1f}% positive)")

# Normalize continuous features (session_duration, hour, time_since_prev)
# Features at indices: 3, 4, 5
continuous_feature_indices = [3, 4, 5]

print(f"\n✓ Normalizing continuous features in sequences...")
for idx in continuous_feature_indices:
    # Calculate mean and std from training data only (exclude padding)
    train_values = X_seq_train[:, :, idx][mask_train == 1]
    feat_mean = train_values.mean()
    feat_std = train_values.std()
    
    if feat_std > 0:
        X_seq_train[:, :, idx] = (X_seq_train[:, :, idx] - feat_mean) / feat_std
        X_seq_test[:, :, idx] = (X_seq_test[:, :, idx] - feat_mean) / feat_std
    
    print(f"  • Feature {sequence_features[idx]}: mean={feat_mean:.2f}, std={feat_std:.2f}")

print("\n" + "=" * 70)
print("SEQUENCE DATA READY FOR LSTM/TRANSFORMER MODELS")
print("=" * 70)
print("\n✓ Available Variables:")
print("  • X_seq_train: Training sequences (3D array)")
print("  • X_seq_test: Test sequences (3D array)")
print("  • y_seq_train: Training labels")
print("  • y_seq_test: Test labels")
print("  • mask_train: Training sequence masks (1=real, 0=padding)")
print("  • mask_test: Test sequence masks")
print("  • action_encoder: LabelEncoder for actions")
print("  • tier_encoder: LabelEncoder for feature tiers")
print("  • sequence_features: List of feature names per timestep")
print("  • target_seq_length: Fixed sequence length for models")

print("\n✓ Next Steps:")
print("  1. Build LSTM model with masking layer")
print("  2. Build Transformer model with attention")
print("  3. Build HMM model for sequential patterns")
print("  4. Train and evaluate all models")
