"""
Generate Synthetic Multimodal Dataset for IntentScope Training
Creates time-series sequences of facial, vocal, and keyboard features
corresponding to 8 distinct intention classes.

Historical pattern: Uses try/except fallback, np.random.seed(42),
and extensive print statements with ASCII borders.
"""

import numpy as np
import pandas as pd
import json
import os
from datetime import datetime

print("=" * 70)
print("MULTIMODAL DATASET GENERATOR")
print("=" * 70)

# Configuration
SEQUENCE_LENGTH = 50
N_FEATURES = 28
N_CLASSES = 8
N_TRAIN_SAMPLES = 5000
N_VAL_SAMPLES = 500
RANDOM_SEED = 42

# Intention class mapping
INTENT_LABELS = [
    'Exploring',
    'BuyIntent',
    'Hesitation',
    'Deception',
    'ActionConfirm',
    'RobotPick',
    'RobotPlace',
    'RobotIdle'
]

# Feature index mapping
FEATURE_NAMES = (
    # Action Units (6) - facial muscle activations
    ['AU1', 'AU2', 'AU12', 'AU15', 'AU20', 'AU26'] +
    # Gaze (2)
    ['gaze_x', 'gaze_y'] +
    # MFCC coefficients (13)
    [f'mfcc_{i}' for i in range(13)] +
    # Other audio features (4)
    ['pitch', 'loudness', 'jitter', 'shimmer'] +
    # Keyboard stats (4)
    ['inter_key_interval', 'hold_duration', 'key_variance', 'typing_speed']
)

print(f"\nConfiguration:")
print(f"  • Sequence length: {SEQUENCE_LENGTH} timesteps")
print(f"  • Features per timestep: {N_FEATURES}")
print(f"  • Number of classes: {N_CLASSES}")
print(f"  • Training samples: {N_TRAIN_SAMPLES}")
print(f"  • Validation samples: {N_VAL_SAMPLES}")
print(f"  • Total shape: ({N_TRAIN_SAMPLES + N_VAL_SAMPLES}, {SEQUENCE_LENGTH}, {N_FEATURES})")


def generate_intention_pattern(intent_label, base_intensity=1.0):
    """
    Generate a time-series pattern for a specific intention.
    Each intention class has characteristic temporal dynamics.

    Returns a function that, given (t, timesteps), returns a feature vector
    with class-specific activations.
    """
    patterns = {
        'Exploring': {
            # Eyes scanning around: high gaze movement, moderate AUs, variable typing
            'gaze': lambda t: (
                0.5 + 0.4 * np.sin(2 * np.pi * t / SEQUENCE_LENGTH),
                0.5 + 0.4 * np.cos(1.5 * np.pi * t / SEQUENCE_LENGTH)
            ),
            'au': lambda t: np.array([
                0.2 + 0.1 * np.sin(t * 0.5),          # AU1 (inner brow raise)
                0.2 + 0.1 * np.cos(t * 0.5),          # AU2
                0.3 + 0.15 * np.sin(t * 0.3),         # AU12 (lip corner pull - curiosity)
                0.1,                                   # AU15
                0.1,                                   # AU20
                0.1                                    # AU26
            ]),
            'audio': lambda t: np.array([
                0.3 + 0.1 * np.random.randn(13).std(),  # MFCCs: moderate variation
                200 + 30 * np.sin(t * 0.2),             # pitch: slightly modulated
                0.3 + 0.1 * np.random.rand(),           # loudness
                0.02,                                    # jitter
                0.03                                     # shimmer
            ]),
            'keyboard': lambda t: np.array([
                150 + 50 * np.random.randn(),           # inter-key interval (medium)
                100 + 30 * np.random.randn(),           # hold duration
                20 + 10 * np.random.rand(),             # variance
                2.5 + 0.8 * np.random.rand()           # typing speed
            ])
        },
        'BuyIntent': {
            # Focused gaze on one spot, high AU12 (smile), higher pitch, fast typing
            'gaze': lambda t: (
                0.5 + 0.05 * np.sin(t * 0.1),          # stable central gaze
                0.5 + 0.05 * np.cos(t * 0.1)
            ),
            'au': lambda t: np.array([
                0.1,                                    # AU1 low
                0.1,                                    # AU2 low
                0.6 + 0.2 * np.sin(t * 0.5),           # AU12 high (smile)
                0.2,                                    # AU15 slight
                0.2,                                    # AU20
                0.1                                     # AU26
            ]),
            'audio': lambda t: np.array([
                0.2 + 0.05 * np.random.randn(13).std(), # MFCCs: stable
                250 + 20 * np.sin(t * 0.3),            # pitch: elevated
                0.4 + 0.1 * np.random.rand(),          # loudness: higher
                0.01,                                   # jitter low
                0.02                                    # shimmer low
            ]),
            'keyboard': lambda t: np.array([
                80 + 20 * np.random.randn(),           # fast inter-key
                60 + 15 * np.random.randn(),           # short holds
                15 + 5 * np.random.rand(),             # low variance
                4.2 + 0.5 * np.random.rand()           # fast typing
            ])
        },
        'Hesitation': {
            # Wandering gaze, high AU1+AU2 (brow furrow), irregular typing, voice tremor
            'gaze': lambda t: (
                0.3 + 0.3 * np.random.randn(),         # erratic x
                0.3 + 0.3 * np.random.randn()          # erratic y
            ),
            'au': lambda t: np.array([
                0.4 + 0.2 * np.random.rand(),          # AU1 high (brow raise)
                0.4 + 0.2 * np.random.rand(),          # AU2 high
                0.2,                                   # AU12 moderate
                0.3,                                   # AU15 (lip bite)
                0.3,                                   # AU20
                0.4                                    # AU26 (jaw drop - uncertainty)
            ]),
            'audio': lambda t: np.array([
                0.3 + 0.15 * np.random.randn(13).std(),
                180 + 50 * np.random.randn(),          # pitch varies a lot
                0.25 + 0.1 * np.random.rand(),
                0.04 + 0.02 * np.random.rand(),        # higher jitter
                0.05 + 0.02 * np.random.rand()         # higher shimmer
            ]),
            'keyboard': lambda t: np.array([
                300 + 150 * np.random.randn(),         # long irregular pauses
                200 + 100 * np.random.randn(),
                40 + 20 * np.random.rand(),
                1.2 + 0.6 * np.random.rand()           # slow typing
            ])
        },
        'Deception': {
            # Avoidant gaze (looking away), controlled AUs, stiff voice, deliberate typing
            'gaze': lambda t: (
                0.2 + 0.1 * np.random.randn(),         # left side (avoidance)
                0.3 + 0.1 * np.random.randn()
            ),
            'au': lambda t: np.array([
                0.2,                                   # AU1 - trying to appear neutral
                0.2,
                0.2,
                0.1,
                0.1,
                0.3                                    # AU26 (jaw drop - tension)
            ]),
            'audio': lambda t: np.array([
                0.15 + 0.05 * np.random.randn(13).std(),  # very stable MFCCs
                220 + 15 * np.random.randn(),            # pitch controlled
                0.3 + 0.05 * np.random.rand(),
                0.01,                                    # low jitter (controlled)
                0.015                                    # low shimmer
            ]),
            'keyboard': lambda t: np.array([
                120 + 30 * np.random.randn(),           # deliberate pace
                90 + 20 * np.random.randn(),
                10 + 5 * np.random.rand(),
                3.0 + 0.4 * np.random.rand()
            ])
        },
        'ActionConfirm': {
            # Direct gaze, sharp AU spikes (confirmation), voice assertion, decisive typing
            'gaze': lambda t: (
                0.5 + 0.1 * np.sin(t * 0.5),          # focused central
                0.5 + 0.1 * np.cos(t * 0.5)
            ),
            'au': lambda t: np.array([
                0.3,                                   # AU1 moderate
                0.3,
                0.5 + 0.2 * (t > SEQUENCE_LENGTH//2), # AU12 spike on decision
                0.2,
                0.2,
                0.3
            ]),
            'audio': lambda t: np.array([
                0.25 + 0.1 * np.random.randn(13).std(),
                230 + 25 * np.sin(t * 0.4),           # pitch peaks
                0.45 + 0.1 * np.random.rand(),
                0.015,                                 # low jitter
                0.02
            ]),
            'keyboard': lambda t: np.array([
                70 + 15 * np.random.randn(),          # quick decisive strokes
                50 + 10 * np.random.randn(),
                8 + 3 * np.random.rand(),
                5.0 + 0.5 * np.random.rand()
            ])
        },
        'RobotPick': {
            # Intense focused gaze, controlled facial expression, voice commands, minimal typing
            'gaze': lambda t: (
                0.5 + 0.15 * np.sin(t * 0.3) if t < 40 else 0.7 + 0.05 * np.random.randn(),  # gaze shifts to target
                0.5 + 0.15 * np.cos(t * 0.3) if t < 40 else 0.3 + 0.05 * np.random.randn()
            ),
            'au': lambda t: np.array([
                0.2,                                   # neutral brow
                0.2,
                0.3,
                0.1,
                0.2,                                   # slight concentration
                0.2
            ]),
            'audio': lambda t: np.array([
                0.2 + 0.08 * np.random.randn(13).std(),
                210 + 20 * (t / SEQUENCE_LENGTH),     # rising pitch as robot reaches
                0.35 + 0.08 * np.random.rand(),
                0.012,
                0.018
            ]),
            'keyboard': lambda t: np.array([
                200 + 100 * np.random.randn() if t > 30 else 1000,  # few keystrokes
                150 + 80 * np.random.randn() if t > 30 else 800,
                30 + 15 * np.random.rand(),
                0.5 + 0.3 * np.random.rand()          # very low typing rate
            ])
        },
        'RobotPlace': {
            # Similar to Pick but with relaxation phase at the end
            'gaze': lambda t: (
                0.7 + 0.05 * np.random.randn() if 20 <= t < 30 else  # look at destination
                0.5 + 0.1 * np.sin(t * 0.2),                         # then return to center
                0.3 + 0.05 * np.random.randn() if 20 <= t < 30 else
                0.5 + 0.1 * np.cos(t * 0.2)
            ),
            'au': lambda t: np.array([
                0.2,
                0.2,
                0.3 + 0.1 * (20 <= t < 40),            # smile on completion
                0.1,
                0.2,
                0.1
            ]),
            'audio': lambda t: np.array([
                0.18 + 0.07 * np.random.randn(13).std(),
                200 + 30 * np.sin(t * 0.25),
                0.3 + 0.1 * np.random.rand(),
                0.01,
                0.015
            ]),
            'keyboard': lambda t: np.array([
                1000 if t < 20 else
                300 + 100 * np.random.randn() if 20 <= t < 50 else
                1000,                                   # few keystrokes throughout
                800,
                30,
                0.3
            ])
        },
        'RobotIdle': {
            # Minimal activity, neutral face, no specific pattern
            'gaze': lambda t: (
                0.5 + 0.1 * np.random.randn(),
                0.5 + 0.1 * np.random.randn()
            ),
            'au': lambda t: np.array([0.1] * 6),      # all AUs low
            'audio': lambda t: np.array([
                0.1 + 0.03 * np.random.randn(13).std(),
                150 + 30 * np.random.randn(),         # lower pitch baseline
                0.2 + 0.05 * np.random.rand(),
                0.008,
                0.012
            ]),
            'keyboard': lambda t: np.array([
                1000 + 500 * np.random.randn(),        # very infrequent
                800 + 400 * np.random.randn(),
                50,
                0.1
            ])
        }
    }

    return patterns[intent_label]


def generate_sequence_for_class(intent_idx, timesteps=SEQUENCE_LENGTH, intensity=1.0):
    """
    Generate a complete time-series sequence for a given intention class.

    Args:
        intent_idx: integer class index [0, N_CLASSES-1]
        timesteps: sequence length
        intensity: amplitude scaling factor

    Returns:
        sequence: numpy array of shape (timesteps, N_FEATURES)
    """
    intent_label = INTENT_LABELS[intent_idx]
    pattern = generate_intention_pattern(intent_label, intensity)

    sequence = np.zeros((timesteps, N_FEATURES), dtype=np.float32)
    time_indices = np.arange(timesteps)

    for t in range(timesteps):
        # Gaze (2 features, indices 6-7)
        gaze_x, gaze_y = pattern['gaze'](t)
        sequence[t, 6] = gaze_x
        sequence[t, 7] = gaze_y

        # Action Units (6 features, indices 0-5)
        au_vals = pattern['au'](t)
        sequence[t, 0:6] = au_vals

        # Audio features
        audio_vals = pattern['audio'](t)
        # MFCCs (13 features, indices 8-20)
        base_mfcc = np.array([0.3, 0.2, 0.15, 0.1, 0.08, 0.05, 0.03, 0.02, 0.015, 0.01, 0.008, 0.005, 0.003])
        mfcc_noise = np.random.randn(13) * 0.05
        sequence[t, 8:21] = base_mfcc + audio_vals[0] + mfcc_noise
        # Pitch, loudness, jitter, shimmer (indices 21-24)
        sequence[t, 21] = audio_vals[1]
        sequence[t, 22] = audio_vals[2]
        sequence[t, 23] = audio_vals[3]
        sequence[t, 24] = audio_vals[4]

        # Keyboard stats (4 features, indices 25-28)
        kb_vals = pattern['keyboard'](t)
        sequence[t, 25] = kb_vals[0]   # inter_key_interval
        sequence[t, 26] = kb_vals[1]   # hold_duration
        sequence[t, 27] = kb_vals[2]   # key_variance
        sequence[t, 28] = kb_vals[3]   # typing_speed

    # Apply intensity scaling to non-binary features
    sequence[:, :6] *= intensity        # AUs
    sequence[:, 8:25] *= intensity      # audio
    sequence[:, 25:] *= intensity       # keyboard

    # Add Gaussian noise to simulate sensor noise
    noise_scale = 0.03
    sequence += np.random.randn(*sequence.shape) * noise_scale

    # Clip values to physiological ranges
    sequence[:, 0:6] = np.clip(sequence[:, 0:6], 0, 1)         # AUs [0,1]
    sequence[:, 6:8] = np.clip(sequence[:, 6:8], 0, 1)         # gaze [0,1]
    sequence[:, 8:21] = np.clip(sequence[:, 8:21], -1, 1)      # MFCCs approx
    sequence[:, 21] = np.clip(sequence[:, 21], 80, 500)        # pitch Hz
    sequence[:, 22] = np.clip(sequence[:, 22], 0, 1)           # loudness
    sequence[:, 23] = np.clip(sequence[:, 23], 0, 0.1)         # jitter
    sequence[:, 24] = np.clip(sequence[:, 24], 0, 0.2)         # shimmer
    sequence[:, 25] = np.maximum(sequence[:, 25], 30)          # inter-key minimum
    sequence[:, 26] = np.maximum(sequence[:, 26], 20)          # hold minimum
    sequence[:, 27] = np.maximum(sequence[:, 27], 0)           # variance non-negative
    sequence[:, 28] = np.maximum(sequence[:, 28], 0)           # speed non-negative

    return sequence.astype(np.float32)


# Set seed for reproducibility
np.random.seed(RANDOM_SEED)
print(f"\n✓ Random seed set to {RANDOM_SEED}")

# Generate training data
print(f"\nGenerating {N_TRAIN_SAMPLES} training sequences...")
X_train = np.zeros((N_TRAIN_SAMPLES, SEQUENCE_LENGTH, N_FEATURES), dtype=np.float32)
y_train = np.zeros(N_TRAIN_SAMPLES, dtype=np.int64)

for i in range(N_TRAIN_SAMPLES):
    intent_idx = np.random.choice(N_CLASSES)
    intensity = 0.8 + 0.4 * np.random.rand()  # random intensity factor
    X_train[i] = generate_sequence_for_class(intent_idx, intensity=intensity)
    y_train[i] = intent_idx

print(f"✓ Training data generated: {X_train.shape}")

# Generate validation data
print(f"\nGenerating {N_VAL_SAMPLES} validation sequences...")
X_val = np.zeros((N_VAL_SAMPLES, SEQUENCE_LENGTH, N_FEATURES), dtype=np.float32)
y_val = np.zeros(N_VAL_SAMPLES, dtype=np.int64)

for i in range(N_VAL_SAMPLES):
    intent_idx = np.random.choice(N_CLASSES)
    intensity = 0.8 + 0.4 * np.random.rand()
    X_val[i] = generate_sequence_for_class(intent_idx, intensity=intensity)
    y_val[i] = intent_idx

print(f"✓ Validation data generated: {X_val.shape}")

# Save to disk
output_dir = 'training/data'
os.makedirs(output_dir, exist_ok=True)

np.save(os.path.join(output_dir, 'X_train.npy'), X_train)
np.save(os.path.join(output_dir, 'y_train.npy'), y_train)
np.save(os.path.join(output_dir, 'X_val.npy'), X_val)
np.save(os.path.join(output_dir, 'y_val.npy'), y_val)

# Save label mapping
label_map = {str(i): label for i, label in enumerate(INTENT_LABELS)}
with open(os.path.join(output_dir, 'label_map.json'), 'w') as f:
    json.dump(label_map, f, indent=2)

print(f"\n✓ Data saved to {output_dir}/")
print(f"  • X_train.npy: {X_train.nbytes / 1024 / 1024:.2f} MB")
print(f"  • y_train.npy: {y_train.nbytes / 1024:.2f} KB")
print(f"  • X_val.npy:   {X_val.nbytes / 1024 / 1024:.2f} MB")
print(f"  • y_val.npy:   {y_val.nbytes / 1024:.2f} KB")

# Class distribution
print("\n" + "=" * 70)
print("CLASS DISTRIBUTION")
print("=" * 70)
train_counts = pd.Series(y_train).value_counts().sort_index()
val_counts = pd.Series(y_val).value_counts().sort_index()
for idx in range(N_CLASSES):
    label = INTENT_LABELS[idx]
    train_pct = train_counts.get(idx, 0) / len(y_train) * 100
    val_pct = val_counts.get(idx, 0) / len(y_val) * 100
    print(f"  {label:15s}: train={train_counts.get(idx, 0):4d} ({train_pct:5.1f}%) | "
          f"val={val_counts.get(idx, 0):4d} ({val_pct:5.1f}%)")

# Feature statistics
print("\n" + "=" * 70)
print("FEATURE STATISTICS (Training Set – First Timestep)")
print("=" * 70)
stats_df = pd.DataFrame({
    'feature': FEATURE_NAMES,
    'mean': X_train[:, 0, :].mean(axis=0),
    'std': X_train[:, 0, :].std(axis=0),
    'min': X_train[:, 0, :].min(axis=0),
    'max': X_train[:, 0, :].max(axis=0)
})
print(stats_df.round(4).to_string(index=False))

print("\n" + "=" * 70)
print("✅ DATASET GENERATION COMPLETE")
print("=" * 70)
print("\nFiles created:")
print(f"  {output_dir}/X_train.npy")
print(f"  {output_dir}/y_train.npy")
print(f"  {output_dir}/X_val.npy")
print(f"  {output_dir}/y_val.npy")
print(f"  {output_dir}/label_map.json")
print("\nNext: run 'python train_fusion_model.py' to train and export the ONNX model.")
