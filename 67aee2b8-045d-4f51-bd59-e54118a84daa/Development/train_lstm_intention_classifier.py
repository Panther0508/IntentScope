import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import cross_val_score

print("=" * 70)
print("GRADIENT BOOSTING CLASSIFIER FOR INTENTION INFERENCE")
print("=" * 70)

# Handle missing values by filling with 0
X_train_filled = X_train_scaled.fillna(0)
X_test_filled = X_test_scaled.fillna(0)

print(f"\n✓ Input Data:")
print(f"  • Training features: {X_train_filled.shape}")
print(f"  • Test features: {X_test_filled.shape}")
print(f"  • Training labels: {y_train.shape} ({y_train.mean():.2%} positive)")
print(f"  • Test labels: {y_test.shape} ({y_test.mean():.2%} positive)")

# Train Gradient Boosting Classifier
print("\n" + "=" * 70)
print("TRAINING GRADIENT BOOSTING MODEL")
print("=" * 70)

gb_classifier = GradientBoostingClassifier(
    n_estimators=200,
    learning_rate=0.1,
    max_depth=5,
    min_samples_split=10,
    min_samples_leaf=4,
    subsample=0.8,
    random_state=42
)

gb_classifier.fit(X_train_filled, y_train)

print("\n✓ Model trained successfully!")

# Cross-validation score
cv_scores_gb = cross_val_score(gb_classifier, X_train_filled, y_train, cv=5, scoring='roc_auc')
print(f"✓ Cross-validation AUC: {cv_scores_gb.mean():.4f} (+/- {cv_scores_gb.std():.4f})")

# Evaluate on test set
print("\n" + "=" * 70)
print("MODEL EVALUATION")
print("=" * 70)

y_pred_gb = gb_classifier.predict(X_test_filled)
y_pred_proba_gb = gb_classifier.predict_proba(X_test_filled)[:, 1]

gb_test_acc = accuracy_score(y_test, y_pred_gb)
gb_test_auc = roc_auc_score(y_test, y_pred_proba_gb)
gb_test_f1 = f1_score(y_test, y_pred_gb)

print(f"\n✓ Test Set Performance:")
print(f"  • Accuracy: {gb_test_acc:.4f}")
print(f"  • AUC: {gb_test_auc:.4f}")
print(f"  • F1 Score: {gb_test_f1:.4f}")

# Classification report
print("\n" + "=" * 70)
print("CLASSIFICATION REPORT")
print("=" * 70)
print(classification_report(y_test, y_pred_gb, target_names=['Non-Successful', 'Successful']))

# Confusion matrix
conf_matrix_gb = confusion_matrix(y_test, y_pred_gb)
print("\n✓ Confusion Matrix:")
print(conf_matrix_gb)
print(f"  • True Negatives: {conf_matrix_gb[0,0]}")
print(f"  • False Positives: {conf_matrix_gb[0,1]}")
print(f"  • False Negatives: {conf_matrix_gb[1,0]}")
print(f"  • True Positives: {conf_matrix_gb[1,1]}")

# Feature importance
print("\n" + "=" * 70)
print("TOP 20 MOST IMPORTANT FEATURES")
print("=" * 70)

feature_importance_gb = pd.DataFrame({
    'feature': X_train_filled.columns,
    'importance': gb_classifier.feature_importances_
}).sort_values('importance', ascending=False)

for _idx_gb, _row_gb in feature_importance_gb.head(20).iterrows():
    print(f"  {_row_gb['feature']:40s}: {_row_gb['importance']:.4f}")

# Generate predictions for all users
print("\n" + "=" * 70)
print("ASSIGNING INTENTION LABELS USING GB PREDICTIONS")
print("=" * 70)

# Predict on full dataset
all_features_scaled_gb = pd.concat([X_train_filled, X_test_filled])
all_labels_true_gb = pd.concat([y_train, y_test])
all_user_ids_gb = feature_matrix.loc[all_features_scaled_gb.index, 'user_id'].values

gb_predictions_all_proba = gb_classifier.predict_proba(all_features_scaled_gb)[:, 1]
gb_predictions_all = (gb_predictions_all_proba > 0.5).astype(int)

# Create results dataframe
gb_results_df = pd.DataFrame({
    'user_id': all_user_ids_gb,
    'gb_success_prob': gb_predictions_all_proba,
    'gb_predicted_success': gb_predictions_all,
    'true_success': all_labels_true_gb.values
})

# Merge with behavioral features for intention labeling
gb_results_df = gb_results_df.merge(
    feature_matrix[['user_id', 'total_interactions', 'unique_actions', 
                    'advanced_user', 'action_diversity_ratio', 'pct_advanced_premium']], 
    on='user_id', 
    how='left'
)

# Assign intention labels based on predictions + behavior
def assign_gb_intention_label(row):
    # Abandoner: predicted failure + low engagement
    if row['gb_predicted_success'] == 0 and row['total_interactions'] <= 4:
        return 'Abandoner'
    # Builder: predicted success + high advanced usage
    elif row['gb_predicted_success'] == 1 and row['advanced_user'] == 1:
        return 'Builder'
    # Explorer: predicted success + diverse actions
    elif row['gb_predicted_success'] == 1 and row['unique_actions'] >= 5:
        return 'Explorer'
    # Learner: moderate engagement or mixed signals
    else:
        return 'Learner'

gb_results_df['gb_intention_label'] = gb_results_df.apply(assign_gb_intention_label, axis=1)

print("\n✓ Gradient Boosting-based Intention Distribution:")
gb_intention_dist = gb_results_df['gb_intention_label'].value_counts()
for _intention_gb, _count_gb in gb_intention_dist.items():
    _pct_gb = 100 * _count_gb / len(gb_results_df)
    print(f"  • {_intention_gb}: {_count_gb} users ({_pct_gb:.1f}%)")

# Compare with ground truth
print("\n" + "=" * 70)
print("INTENTION LABEL VALIDATION")
print("=" * 70)

# Analyze characteristics of each intention group
for _intention_profile in gb_intention_dist.index:
    intention_users_gb = gb_results_df[gb_results_df['gb_intention_label'] == _intention_profile]
    print(f"\n📊 {_intention_profile.upper()} PROFILE:")
    print(f"  • Count: {len(intention_users_gb)} users")
    print(f"  • Avg interactions: {intention_users_gb['total_interactions'].mean():.1f}")
    print(f"  • Avg unique actions: {intention_users_gb['unique_actions'].mean():.1f}")
    print(f"  • True success rate: {intention_users_gb['true_success'].mean():.2%}")
    print(f"  • Predicted success rate: {intention_users_gb['gb_predicted_success'].mean():.2%}")

print("\n" + "=" * 70)
print("FINAL MODEL SUMMARY")
print("=" * 70)
print(f"\n✓ Model Type: Gradient Boosting Classifier (Feature-based)")
print(f"✓ Total users classified: {len(gb_results_df)}")
print(f"✓ Test Accuracy: {gb_test_acc:.4f}")
print(f"✓ Test AUC: {gb_test_auc:.4f}")
print(f"✓ Test F1 Score: {gb_test_f1:.4f}")
print(f"✓ Intention categories: {gb_intention_dist.index.tolist()}")
print(f"✓ Feature importance analyzed: Top predictors identified")

print("\n✓ Available Variables:")
print("  • gb_classifier: Trained Gradient Boosting model")
print("  • gb_results_df: DataFrame with predictions and intention labels")
print("  • feature_importance_gb: Feature importance rankings")
print("  • conf_matrix_gb: Confusion matrix")
