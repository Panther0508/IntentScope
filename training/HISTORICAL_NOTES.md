# Historical Pattern Analysis for IntentScope

**Date:** 2026-05-03  
**Phase:** 2 – Sensor Array & Training Pipeline  
**Analyst:** Kilo (automated agent)

---

## Commit Sources Examined

| Commit Hash | Date | Description |
|-------------|------|-------------|
| `97186740abb59d82173311484f7ef99ac5a872df` | 2026-03-10 | Comprehensive implementation commit (67,000+ lines across 40+ Python files) |
| `f37d93fb90e5b436e2e52c7292422dfb68db3767` | 2026-03-19 | CSV analysis and dashboard metrics |
| `58f48be5d4fa1b49a65e59a5b7eff461500762e9` | 2026-05-03 | Documentation expansion |

The key commit (`97186740...`) contains the core behavioral analytics engine, LSTM classifier, realtime prediction engine, and simulation scripts.

---

## 1. Coding Style & Conventions

### 1.1 Variable & Function Naming

**Pattern:** snake_case throughout.

```python
# Examples from original:
user_behavior_df           # DataFrame variable
total_interactions         # feature column
action_diversity_ratio     # derived metric
freq_login                 # frequency feature prefix
feat_user_data             # temporary variable prefix (internal to loops)
```

**Notable:** The code uses Hungarian-like prefixes in loop variables (`_feat_`) to denote temporary feature-engineering variables. This is a local convention to avoid naming collisions in dense notebooks/scripts.

### 1.2 Docstring Style

**No formal docstring standard** – functions and classes have descriptive multi-line comments instead:

```python
"""
LSTM Intention Classifier for IntentScope
Deep Learning approach using TensorFlow/Keras for sequence-based intention prediction
"""

class LSTMIntentionClassifier:
    """
    LSTM-based classifier for predicting user intention from behavioral sequences.
    Uses Bidirectional LSTM for capturing both forward and backward sequence patterns.
    """
```

Docstrings3 are **descriptive paragraphs**, not following Google/NumPy format. No Args/Returns sections – they're conveyed via inline comments.

### 1.3 Error Handling & Fallbacks

**Robust fallback pattern with try/except:**

```python
try:
    from .load_dataset import user_behavior_df
    from .define_long_term_success_metric import user_metrics
except ImportError:
    print("[OK] Running in standalone mode - creating sample data")
    # generate synthetic data...
```

The original code *gracefully degrades* if upstream modules aren't available, creating sample data with `np.random.seed(42)` to ensure reproducibility. Every script can run standalone.

### 1.4 Logging Style

**ASCII-bordered print statements** for visual separation:

```python
print("=" * 70)
print("BEHAVIORAL FEATURE ENGINEERING")
print("=" * 70)
print(f"\n✓ Feature Engineering Complete!")
print(f"  • Total users: {len(feature_matrix)}")
```

Checkmarks (`✓`), bullet points (`•`), and section headers are used extensively. Progress messages are verbose.

---

## 2. Library Dependencies

### Core Data Stack
| Library | Usage |
|---------|-------|
| `pandas` | Primary data structure (DataFrame) for all tabular data |
| `numpy` | Numerical operations, random generation, array manipulation |
| `scikit-learn` | `StandardScaler`, `train_test_split`, `LabelEncoder`, metrics (`accuracy_score`, `classification_report`, `confusion_matrix`, `roc_auc_score`) |

### Deep Learning
| Library | Usage |
|---------|-------|
| `tensorflow` / `keras` | LSTM model with `Bidirectional(LSTM(...))`, `BatchNormalization`, `Dropout`, callbacks (`EarlyStopping`, `ReduceLROnPlateau`, `ModelCheckpoint`) |

**Note:** TensorFlow is the official deep learning framework used, not PyTorch. Models are built with Keras Sequential API.

### Optional / Analysis
| Library | Usage |
|---------|-------|
| `shap` | Feature importance via SHAP values (imported conditionally) |
| `matplotlib` / `seaborn` | Visualization (not shown in snippets but referenced in README) |

**No usage of:** OpenCV (`cv2`), HuggingFace `transformers`, `huggingface_hub`, FastAPI in the core training code. The original project is **purely behavioral analytics** with no computer vision.

---

## 3. AI/ML Usage Patterns

### 3.1 Model Types

1. **Gradient Boosting Classifier** (`sklearn.ensemble.GradientBoostingClassifier`) for success prediction (AUC optimized)
2. **K-Means Clustering** (`sklearn.cluster.KMeans`) for intention grouping (4–8 clusters)
3. **LSTM Neural Network** (Keras) for sequence-based classification (4-class)

### 3.2 Sequence Processing

- Sequences are created via a sliding window: `X[i:i+sequence_length]` → label at `y[i+sequence_length]`
- Word2Vec or TF-IDF is used to embed **action sequences** (`'login search export ...'`) into dense vectors before clustering
- Behavioral features are concatenated with sequence embeddings to form a combined feature vector

### 3.3 Training Paradigm

```python
# Callbacks used:
callbacks = [
    EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-6),
    ModelCheckpoint(...)  # for saving best model
]

# Stratified train/test split:
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Standardization is ALWAYS applied after splitting:
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
```

---

## 4. Data Structures

### 4.1 Event / Sensor Dictionary Format

From `realtime_prediction_engine.py` and `simulate_live_streaming_and_predict.py`:

```python
event = {
    'user_id': int,              # e.g., 50001
    'timestamp': str,            # ISO format: "2026-03-10T14:23:00"
    'action': str,               # 'login', 'view_dashboard', 'run_analysis', 'create_visualization',
                                 # 'export_data', 'share_result', 'logout'
    'tier': str,                 # 'Free', 'Pro', 'Enterprise'
    'session_duration': int,     # seconds
    'success': bool,             # True if action succeeded
    'feature_used': str          # e.g., 'feature_A', 'feature_B'
}
```

The original system tracks **user behavioral events**, not raw sensor data. Intent is inferred from sequential action patterns.

### 4.2 Feature Matrix Structure

From `engineer_behavioral_features.py`:

The feature matrix `feature_matrix` is a pandas DataFrame with:

```python
Columns:
- user_id                    (identifier)
- long_term_success          (target: 0 or 1)

# Frequency features (18 total):
total_interactions
days_active
interactions_per_day
freq_login, pct_login
freq_view_dashboard, pct_view_dashboard
freq_run_analysis, pct_run_analysis
freq_create_visualization, pct_create_visualization
freq_export_data, pct_export_data
freq_share_result, pct_share_result
freq_logout, pct_logout
freq_basic, freq_advanced, freq_premium
pct_advanced_premium

# Sequence pattern features (9 total):
unique_actions
action_diversity_ratio
most_common_sequence_count
unique_sequences
has_login_analysis_pattern
has_analysis_viz_pattern
has_viz_export_pattern
has_export_share_pattern
complete_sessions

# Time pattern features (12 total):
avg_hour_of_day
hour_std
pct_business_hours
pct_weekend
avg_time_between_interactions_hrs
median_time_between_interactions_hrs
std_time_between_interactions_hrs
max_gap_days
days_since_last_interaction
days_since_first_interaction

# Workflow complexity features (15 total):
avg_session_duration
total_session_time_hrs
median_session_duration
max_session_duration
overall_success_rate
successful_actions
failed_actions
success_rate_run_analysis
success_rate_create_visualization
success_rate_export_data
tier_progression
advanced_user
early_success_rate
early_avg_session
```

**Total:** ~54 features + 2 meta columns (`user_id`, `long_term_success`).

### 4.3 Prediction Output Structure

From `RealtimePredictionEngine.process_event()`:

```python
prediction = {
    'timestamp': datetime,
    'user_id': int,
    'action': str,
    'tier': str,
    'success': bool,
    'intention_label': str,          # e.g., 'Builder', 'Explorer', 'Learner', 'Abandoner'
    'success_probability': float,    # 0-100 percentage
    'feature_extraction_time_ms': float,
    'total_latency_ms': float,
    'event_sequence_length': int,
    'confidence_score': float        # 0-100
}
```

---

## 5. Historical Mock / Fallback Data Patterns

The original code extensively uses **synthetic data generation** for testing:

```python
if user_behavior_df is None or len(user_behavior_df) == 0:
    print("⚠️  Creating sample sequence data for LSTM training")
    np.random.seed(42)
    n_samples = 1000
    n_timesteps = sequence_length
    n_features = n_features
    X = np.random.randn(n_samples, n_timesteps, n_features).astype(np.float32)
    y = np.random.randint(0, n_classes, n_samples)
```

**Key characteristics:**
- `np.random.seed(42)` for determinism
- `np.random.randn()` for Gaussian samples
- `np.random.randint()` for class labels
- `random.choice()` for categorical draws

The simulation engine (`LiveInputSimulator`) uses realistic distributions:

- `np.random.exponential(scale=15)` for session durations
- `random.choices(population, weights=...)` for tier distribution
- Pattern templates (`exploratory`, `goal_oriented`, `high_frequency`) with predefined action sequences

---

## 6. Mapping Historical Patterns to Phase 2 Implementation

| Historical Pattern | Phase 2 Adaptation |
|--------------------|--------------------|
| **Event dictionaries** with `user_id`, `action`, `tier`, `session_duration`, `success`, `feature_used` | **Sensor data objects** will follow similar structure, but with sensor-specific keys: `{ face: {...}, voice: {...}, keyboard: {...}, timestamp }` |
| **Feature engineering with pandas DataFrames** | Client-side `sensorAggregator.js` will maintain a sliding buffer as array of objects, convert to numeric vector matching the 28-feature specification |
| **Try/except import fallback** | Python training scripts will include `try/except ImportError` blocks with sample data generation, ensuring standalone execution even if optional deps missing |
| **ASCII-bordered logging** | Adopt similar `print("=" * 70)` style in Python training scripts for clear console output during model generation |
| **Random seed 42** | Use `np.random.seed(42)` consistently in `generate_dataset.py` for reproducible synthetic data |
| **Stratified train/test split** | Use `train_test_split(..., stratify=y)` in training script |
| **StandardScaler** | Save scaler parameters to JSON to replicate preprocessing in browser (though we'll standardize in JS later) |
| **TensorFlow/Keras** | Switch to **PyTorch** for ONNX export friendliness (more reliable opset support), but keep similar architecture (LSTM → Dense layers) |
| **Model checkpointing** | Save `.pth` file and export to `.onnx` with dynamic quantization (as per Phase 2 spec) |
| **Simulation engine** | The original `LiveInputSimulator` generates user events. Our browser workers will generate **sensor readings** instead – but we can reuse the event timing patterns to simulate realistic sensor data during training data generation |

### Key Adaptation: From Behavioral Events to Multimodal Sensors

The original system derived intent from **what actions a user took** (clicks, navigation). Our Phase 2 browser app will derive intent from **how the user behaves** (face, voice, typing). The mapping:

| Original Event Field | Sensor Equivalent (Phase 2) |
|----------------------|-----------------------------|
| `action` (categorical) | **AU activations** + gaze coordinates → encoded as discrete patterns |
| `success` (binary) | **Voice stress level** + **intent confidence** (continuous) |
| `session_duration` | **Typing dwell time** + **inter-key interval** |
| `tier` (Free/Pro/Enterprise) | Not applicable (no user tiers) |
| `feature_used` | **Which sensor modality** triggered event |

**Feature vector alignment:** The 28 features specified in Phase 2 (6 AU + 2 gaze + 13 MFCC + pitch + loudness + jitter + shimmer + 4 keyboard) do not directly map to the original 54 behavioral features. However, the **feature naming convention** (lowercase with underscores) and **normalization approach** (StandardScaler) should be retained.

---

## 7. Additional Observations

1. **Modular structure:** Original code organizes files by function (`engineer_behavioral_features.py`, `train_lstm_intention_classifier.py`, `prepare_modeling_dataset.py`) – we will mirror this in `training/`.

2. **No class inheritance:** Classes are standalone utility containers (e.g., `LSTMIntentionClassifier`), not part of deep inheritance hierarchies.

3. **Print-based progress:** Even large training runs use `print` statements, not `logging` module. This is acceptable for the training pipeline.

4. **Deterministic seeds:** Always `np.random.seed(42)` and `tf.random.set_seed(42)` for reproducibility.

5. **Performance targets:** The realtime engine aims for **<100ms latency** per event. Our client-side workers should respect this budget.

---

## Conclusion

The original IntentScope backend is a **behavioral analytics platform** that predicts user success and intention from logged actions. Phase 2 pivots to **multimodal intention reading** from live sensors. The coding patterns (snake_case, try/except fallbacks, verbose progress prints, pandas-centric data) will be preserved in the new client-side and training code.

**Next step:** Create `training/generate_dataset.py`, `training/train_fusion_model.py`, `requirements.txt`, and `README.md` following these conventions.
