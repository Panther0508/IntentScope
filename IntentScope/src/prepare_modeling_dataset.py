import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

print("=" * 70)
print("PREPARING DATA FOR MODELING")
print("=" * 70)

# Separate features and target
X = feature_matrix.drop(['user_id', 'long_term_success'], axis=1)
y = feature_matrix['long_term_success']

print(f"\n✓ Dataset Prepared:")
print(f"  • Feature matrix shape: {X.shape}")
print(f"  • Target variable shape: {y.shape}")
print(f"  • Total features: {X.shape[1]}")
print(f"  • Positive class ratio: {y.mean():.1%} (successful users)")
print(f"  • Negative class ratio: {(1-y.mean()):.1%} (non-successful users)")

# Check for any missing values
missing_counts = X.isnull().sum()
if missing_counts.sum() > 0:
    print(f"\n⚠ Warning: Found {missing_counts.sum()} missing values")
    print(missing_counts[missing_counts > 0])
else:
    print("\n✓ No missing values in feature matrix")

# Split into train/test sets (80/20 split)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\n✓ Train/Test Split (80/20):")
print(f"  • Training set: {X_train.shape[0]} samples ({y_train.mean():.1%} positive)")
print(f"  • Test set: {X_test.shape[0]} samples ({y_test.mean():.1%} positive)")

# Standardize features (important for many ML models)
scaler_model = StandardScaler()
X_train_scaled = scaler_model.fit_transform(X_train)
X_test_scaled = scaler_model.transform(X_test)

# Convert back to DataFrames to preserve feature names
X_train_scaled = pd.DataFrame(X_train_scaled, columns=X_train.columns, index=X_train.index)
X_test_scaled = pd.DataFrame(X_test_scaled, columns=X_test.columns, index=X_test.index)

print("\n✓ Features Standardized (StandardScaler):")
print(f"  • Mean of scaled training features: {X_train_scaled.mean().mean():.2e}")
print(f"  • Std of scaled training features: {X_train_scaled.std().mean():.2f}")

# Feature importance preview - calculate correlation with target
feature_correlations_prep = pd.DataFrame({
    'feature': X.columns,
    'correlation': [X[col].corr(y) for col in X.columns]
})
feature_correlations_prep['abs_correlation'] = feature_correlations_prep['correlation'].abs()
feature_correlations_prep = feature_correlations_prep.sort_values('abs_correlation', ascending=False)

print("\n" + "=" * 70)
print("TOP 20 FEATURES BY CORRELATION WITH TARGET")
print("=" * 70)
for _idx_prep, _row_prep in feature_correlations_prep.head(20).iterrows():
    _feat_name = _row_prep['feature']
    _corr_val = _row_prep['correlation']
    print(f"  {_feat_name:40s}: {_corr_val:7.3f}")

print("\n" + "=" * 70)
print("MODELING DATASET SUMMARY")
print("=" * 70)
print("\n✓ Available Variables for Modeling:")
print("  • X_train: Training features (unscaled)")
print("  • X_test: Test features (unscaled)")
print("  • X_train_scaled: Training features (standardized)")
print("  • X_test_scaled: Test features (standardized)")
print("  • y_train: Training labels")
print("  • y_test: Test labels")
print("  • scaler_model: Fitted StandardScaler object")
print("  • feature_matrix: Complete dataset with user_id and target")

print("\n✓ Feature Categories Summary:")
_freq_count = len([c for c in X.columns if c.startswith('freq_') or c.startswith('pct_')])
_seq_count = len([c for c in X.columns if 'pattern' in c or 'sequence' in c])
_time_count = len([c for c in X.columns if 'hour' in c or 'time_between' in c or 'since' in c])
_workflow_count = len([c for c in X.columns if 'success' in c or 'session' in c])
print(f"  • Frequency features: {_freq_count}")
print(f"  • Sequence pattern features: {_seq_count}")
print(f"  • Time pattern features: {_time_count}")
print(f"  • Workflow/success features: {_workflow_count}")

print("\n" + "=" * 70)
print("NEXT STEPS FOR MODELING")
print("=" * 70)
print("✓ Data is ready for machine learning models:")
print("  1. Classification models (Logistic Regression, Random Forest, XGBoost, etc.)")
print("  2. Feature selection and importance analysis")
print("  3. Hyperparameter tuning and cross-validation")
print("  4. Model evaluation and interpretation")
print("\n✓ Consider class imbalance (27.1% positive class)")
print("  → Use stratified sampling, SMOTE, or class_weight balancing")
