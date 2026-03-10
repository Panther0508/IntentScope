"""
LSTM Intention Classifier for IntentScope
Deep Learning approach using TensorFlow/Keras for sequence-based intention prediction
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Bidirectional, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

# Set random seeds for reproducibility
np.random.seed(42)
tf.random.set_seed(42)


class LSTMIntentionClassifier:
    """
    LSTM-based classifier for predicting user intention from behavioral sequences.
    Uses Bidirectional LSTM for capturing both forward and backward sequence patterns.
    """
    
    def __init__(self, sequence_length=20, n_features=15, n_classes=4, learning_rate=0.001):
        self.sequence_length = sequence_length
        self.n_features = n_features
        self.n_classes = n_classes
        self.learning_rate = learning_rate
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.history = None
        
    def build_model(self):
        """Build Bidirectional LSTM model architecture"""
        model = Sequential([
            # Input layer
            tf.keras.layers.Input(shape=(self.sequence_length, self.n_features)),
            
            # First Bidirectional LSTM layer
            Bidirectional(LSTM(64, return_sequences=True)),
            BatchNormalization(),
            Dropout(0.3),
            
            # Second Bidirectional LSTM layer
            Bidirectional(LSTM(32, return_sequences=False)),
            BatchNormalization(),
            Dropout(0.3),
            
            # Dense layers
            Dense(32, activation='relu'),
            Dropout(0.2),
            Dense(16, activation='relu'),
            
            # Output layer
            Dense(self.n_classes, activation='softmax')
        ])
        
        # Compile with Adam optimizer
        optimizer = Adam(learning_rate=self.learning_rate)
        model.compile(
            optimizer=optimizer,
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy', tf.keras.metrics.AUC(name='auc')]
        )
        
        self.model = model
        return model
    
    def create_sequences(self, X, y, sequence_length=None):
        """Create sequences from behavioral data for LSTM input"""
        if sequence_length is None:
            sequence_length = self.sequence_length
            
        sequences = []
        labels = []
        
        for i in range(len(X) - sequence_length):
            sequences.append(X[i:i + sequence_length])
            labels.append(y[i + sequence_length])
            
        return np.array(sequences), np.array(labels)
    
    def prepare_data(self, user_behavior_df, feature_cols=None):
        """
        Prepare data for LSTM training from user behavior DataFrame.
        
        Args:
            user_behavior_df: DataFrame with user_id, timestamp, action, success, etc.
            feature_cols: List of feature columns to use (optional)
        """
        # Create sample data if not provided
        if user_behavior_df is None or len(user_behavior_df) == 0:
            print("⚠️  Creating sample sequence data for LSTM training")
            np.random.seed(42)
            n_samples = 1000
            n_timesteps = self.sequence_length
            n_features = self.n_features
            
            # Generate synthetic sequence data
            X = np.random.randn(n_samples, n_timesteps, n_features).astype(np.float32)
            
            # Generate labels (4 intention classes)
            y = np.random.randint(0, self.n_classes, n_samples)
            
            # Split into train/test
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            return X_train, X_test, y_train, y_test
        
        # Extract features from behavior data
        if feature_cols is None:
            # Default features to extract
            feature_cols = [
                'total_interactions', 'unique_actions', 'success_rate',
                'session_duration_mean', 'action_diversity_ratio', 'pct_advanced_premium',
                'freq_login', 'freq_view_dashboard', 'freq_run_analysis',
                'freq_create_visualization', 'freq_export_data', 'freq_share_result',
                'freq_logout', 'complete_sessions', 'advanced_user'
            ]
        
        # Sort by user and time
        df_sorted = user_behavior_df.sort_values(['user_id', 'timestamp']).reset_index(drop=True)
        
        # Aggregate features per user (simplified - would normally use full feature engineering)
        user_features = df_sorted.groupby('user_id').agg({
            'action': 'count',
            'success': 'mean',
            'session_duration_minutes': 'mean'
        }).reset_index()
        
        user_features.columns = ['user_id', 'total_interactions', 'success_rate', 'session_duration_mean']
        
        # Add derived features
        user_features['unique_actions'] = df_sorted.groupby('user_id')['action'].nunique().values
        user_features['action_diversity_ratio'] = user_features['unique_actions'] / 7
        
        # Fill missing features
        for col in feature_cols:
            if col not in user_features.columns:
                user_features[col] = np.random.rand(len(user_features))
        
        # Scale features
        X = user_features[feature_cols].values
        X_scaled = self.scaler.fit_transform(X)
        
        # Create sequences (using sliding window approach)
        # Repeat features to create sequence dimension
        X_seq = np.tile(X_scaled[:, np.newaxis, :], (1, self.sequence_length, 1))
        
        # Generate labels (based on success rate - can be replaced with actual labels)
        labels = (user_features['success_rate'] > 0.7).astype(int) + \
                 (user_features['total_interactions'] > 10).astype(int)
        labels = np.clip(labels, 0, self.n_classes - 1)
        
        y_encoded = self.label_encoder.fit_transform(labels)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_seq, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
        
        return X_train, X_test, y_train, y_test
    
    def train(self, X_train, y_train, X_val=None, y_val=None, epochs=50, batch_size=32, verbose=1):
        """Train the LSTM model"""
        if self.model is None:
            self.build_model()
        
        # Define callbacks
        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True,
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-6,
                verbose=1
            )
        ]
        
        # Validation data
        if X_val is None or y_val is None:
            # Use a portion of training data for validation
            val_split = 0.2
            validation_data = None
        else:
            validation_data = (X_val, y_val)
        
        # Train the model
        self.history = self.model.fit(
            X_train, y_train,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=verbose
        )
        
        return self.history
    
    def evaluate(self, X_test, y_test):
        """Evaluate the model on test data"""
        if self.model is None:
            raise ValueError("Model not trained yet!")
        
        # Predictions
        y_pred_proba = self.model.predict(X_test, verbose=0)
        y_pred = np.argmax(y_pred_proba, axis=1)
        
        # Metrics
        results = {
            'accuracy': accuracy_score(y_test, y_pred),
            'f1_macro': f1_score(y_test, y_pred, average='macro'),
            'f1_weighted': f1_score(y_test, y_pred, average='weighted'),
            'auc_macro': roc_auc_score(y_test, y_pred_proba, average='macro', multi_class='ovr'),
            'confusion_matrix': confusion_matrix(y_test, y_pred),
            'classification_report': classification_report(
                y_test, y_pred, 
                target_names=self.label_encoder.classes_.astype(str)
            )
        }
        
        return results, y_pred, y_pred_proba
    
    def predict(self, X):
        """Predict intention classes for new data"""
        if self.model is None:
            raise ValueError("Model not trained yet!")
        
        y_pred_proba = self.model.predict(X, verbose=0)
        y_pred = np.argmax(y_pred_proba, axis=1)
        
        return y_pred, y_pred_proba
    
    def get_feature_importance(self, X_sample, y_sample):
        """
        Get feature importance using permutation importance approximation.
        """
        baseline_pred = self.model.predict(X_sample, verbose=0)
        importance_scores = []
        
        for feature_idx in range(X_sample.shape[2]):
            # Permute this feature
            X_permuted = X_sample.copy()
            X_permuted[:, :, feature_idx] = np.random.permutation(X_permuted[:, :, feature_idx])
            
            # Measure performance drop
            permuted_pred = self.model.predict(X_permuted, verbose=0)
            importance = np.mean(np.abs(baseline_pred - permuted_pred))
            importance_scores.append(importance)
        
        return np.array(importance_scores)
    
    def summary(self):
        """Print model summary"""
        if self.model is None:
            print("Model not built yet!")
        else:
            self.model.summary()


def run_lstm_classification():
    """Main function to run LSTM classification"""
    print("=" * 70)
    print("LSTM INTENTION CLASSIFIER - DEEP LEARNING APPROACH")
    print("=" * 70)
    
    # Initialize classifier
    lstm_classifier = LSTMIntentionClassifier(
        sequence_length=20,
        n_features=15,
        n_classes=4,
        learning_rate=0.001
    )
    
    # Prepare data (using sample data)
    print("\n📊 Preparing sequence data...")
    X_train, X_test, y_train, y_test = lstm_classifier.prepare_data(
        user_behavior_df=None,
        feature_cols=None
    )
    
    print(f"✓ Training data shape: {X_train.shape}")
    print(f"✓ Test data shape: {X_test.shape}")
    print(f"✓ Number of classes: {lstm_classifier.n_classes}")
    
    # Build model
    print("\n🏗️  Building Bidirectional LSTM model...")
    lstm_classifier.build_model()
    lstm_classifier.summary()
    
    # Train model
    print("\n🎯 Training LSTM model...")
    history = lstm_classifier.train(
        X_train, y_train,
        epochs=30,
        batch_size=32,
        verbose=1
    )
    
    # Evaluate
    print("\n📈 Evaluating model...")
    results, y_pred, y_pred_proba = lstm_classifier.evaluate(X_test, y_test)
    
    print("\n" + "=" * 70)
    print("MODEL EVALUATION RESULTS")
    print("=" * 70)
    print(f"✓ Accuracy: {results['accuracy']:.4f}")
    print(f"✓ F1 Score (Macro): {results['f1_macro']:.4f}")
    print(f"✓ F1 Score (Weighted): {results['f1_weighted']:.4f}")
    print(f"✓ AUC (Macro): {results['auc_macro']:.4f}")
    
    print("\n✓ Classification Report:")
    print(results['classification_report'])
    
    print("\n✓ Confusion Matrix:")
    print(results['confusion_matrix'])
    
    # Training history
    print("\n" + "=" * 70)
    print("TRAINING HISTORY")
    print("=" * 70)
    if history.history:
        print(f"✓ Final Training Accuracy: {history.history['accuracy'][-1]:.4f}")
        print(f"✓ Final Validation Accuracy: {history.history.get('val_accuracy', [0])[-1]:.4f}")
        print(f"✓ Total Epochs: {len(history.history['loss'])}")
    
    print("\n" + "=" * 70)
    print("✅ LSTM CLASSIFICATION COMPLETE")
    print("=" * 70)
    
    return lstm_classifier, results


if __name__ == "__main__":
    lstm_classifier, results = run_lstm_classification()
