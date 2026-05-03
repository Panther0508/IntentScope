"""
Train Fusion Model for IntentScope
Temporal fusion model that takes multimodal time-series and outputs:
  - 8-class intent softmax
  - 32-dimensional embedding for downstream use

Exports to ONNX with dynamic quantization.

Historical pattern: Try/except fallbacks, verbose print statements with borders,
progress tracking, and a final inference test using onnxruntime.
"""

import os
import sys
import json
import numpy as np

print("=" * 70)
print("FUSION MODEL TRAINING")
print("=" * 70)

# ── Try importing required libraries ──────────────────────────────────────
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torch.utils.data import DataLoader, TensorDataset
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("[WARN] PyTorch not available – will create ONNX placeholder only.")

try:
    import onnx
    from onnxruntime.quantization import quantize_dynamic, QuantType
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False
    print("[WARN] ONNX/onnxruntime not available – export will be skipped.")

try:
    from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
    from sklearn.model_selection import train_test_split
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("[WARN] scikit-learn not available – metrics will be limited.")

# ── Configuration ──────────────────────────────────────────────────────────
SEQUENCE_LENGTH = 50
N_FEATURES = 28
N_CLASSES = 8
EMBEDDING_DIM = 32
HIDDEN_DIM = 64
NUM_LAYERS = 2
DROPOUT = 0.3
BATCH_SIZE = 64
LEARNING_RATE = 0.001
NUM_EPOCHS = 30
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu') if TORCH_AVAILABLE else None

DATA_DIR = 'training/data'
MODEL_DIR = 'training'
PUBLIC_DIR = 'public'

print(f"\nConfiguration:")
print(f"  • Device: {DEVICE if TORCH_AVAILABLE else 'N/A'}")
print(f"  • Sequence length: {SEQUENCE_LENGTH}")
print(f"  • Features: {N_FEATURES}")
print(f"  • Classes: {N_CLASSES}")
print(f"  • Epochs: {NUM_EPOCHS}")
print(f"  • Batch size: {BATCH_SIZE}")


# ── Model Definition ───────────────────────────────────────────────────────
class FusionModel(nn.Module):
    """
    Temporal fusion model: LSTM backbone with two heads.
    Head 1: intent classification (8-way softmax)
    Head 2: embedding generation (32-dim)
    """

    def __init__(self, input_dim, hidden_dim, n_layers, n_classes, embedding_dim, dropout=0.3):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.n_layers = n_layers

        # Bidirectional LSTM
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=n_layers,
            batch_first=True,
            dropout=dropout if n_layers > 1 else 0,
            bidirectional=True
        )

        # Attention mechanism (simple self-attention)
        self.attention = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, 1)
        )

        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, n_classes)
        )

        # Embedding head
        self.embedding_head = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, embedding_dim)
        )

    def forward(self, x):
        # x: (batch, seq_len, features)
        lstm_out, (hidden, cell) = self.lstm(x)
        # lstm_out: (batch, seq_len, hidden_dim*2)

        # Attention pooling over time dimension
        attention_weights = F.softmax(self.attention(lstm_out), dim=1)
        context = torch.sum(attention_weights * lstm_out, dim=1)  # (batch, hidden*2)

        # Heads
        intent_logits = self.classifier(context)
        embedding = self.embedding_head(context)

        return intent_logits, embedding

    def predict(self, x):
        """Convenience method: returns class index and probabilities."""
        self.eval()
        with torch.no_grad():
            logits, _ = self.forward(x)
            probs = F.softmax(logits, dim=1)
            preds = torch.argmax(probs, dim=1)
        return preds.cpu().numpy(), probs.cpu().numpy()


# ── Training Functions ─────────────────────────────────────────────────────
def load_data():
    """Load training and validation datasets.
    Prefers combined (synthetic + real) data if available; falls back to synthetic-only.
    """
    combined_X_path = os.path.join(DATA_DIR, 'X_combined.npy')
    combined_y_path = os.path.join(DATA_DIR, 'y_combined.npy')

    if os.path.exists(combined_X_path) and os.path.exists(combined_y_path):
        # Use combined dataset
        print(f"\n[INFO] Loading combined dataset (synthetic + real)...")
        X = np.load(combined_X_path)
        y = np.load(combined_y_path)

        # Split 80/20
        from sklearn.model_selection import train_test_split
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        print(f"  • Combined data: {X.shape} → {len(np.unique(y))} classes")
    else:
        # Fall back to synthetic splits
        print(f"\n[INFO] Combined data not found – using synthetic train/val splits...")
        X_train = np.load(os.path.join(DATA_DIR, 'X_train.npy'))
        y_train = np.load(os.path.join(DATA_DIR, 'y_train.npy'))
        X_val = np.load(os.path.join(DATA_DIR, 'X_val.npy'))
        y_val = np.load(os.path.join(DATA_DIR, 'y_val.npy'))

    print(f"\n✓ Data loaded:")
    print(f"  • X_train: {X_train.shape}, dtype={X_train.dtype}")
    print(f"  • y_train: {y_train.shape}, classes={len(np.unique(y_train))}")
    print(f"  • X_val:   {X_val.shape}")
    print(f"  • y_val:   {y_val.shape}")

    return X_train, y_train, X_val, y_val


def train_epoch(model, dataloader, criterion, optimizer, device):
    """Train for one epoch."""
    model.train()
    total_loss = 0
    correct = 0
    total = 0

    for batch_x, batch_y in dataloader:
        batch_x = batch_x.to(device)
        batch_y = batch_y.to(device)

        optimizer.zero_grad()
        logits, _ = model(batch_x)
        loss = criterion(logits, batch_y)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        _, predicted = torch.max(logits.data, 1)
        total += batch_y.size(0)
        correct += (predicted == batch_y).sum().item()

    accuracy = 100 * correct / total
    avg_loss = total_loss / len(dataloader)
    return avg_loss, accuracy


def validate_epoch(model, dataloader, criterion, device):
    """Validate for one epoch."""
    model.eval()
    total_loss = 0
    correct = 0
    total = 0
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for batch_x, batch_y in dataloader:
            batch_x = batch_x.to(device)
            batch_y = batch_y.to(device)

            logits, _ = model(batch_x)
            loss = criterion(logits, batch_y)

            total_loss += loss.item()
            _, predicted = torch.max(logits.data, 1)
            total += batch_y.size(0)
            correct += (predicted == batch_y).sum().item()

            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(batch_y.cpu().numpy())

    accuracy = 100 * correct / total
    avg_loss = total_loss / len(dataloader)
    return avg_loss, accuracy, all_preds, all_labels


def train_model():
    """Main training loop."""
    if not TORCH_AVAILABLE:
        print("[ERROR] PyTorch not available – cannot train model.")
        return None

    # Load data
    try:
        X_train, y_train, X_val, y_val = load_data()
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        return None

    # Convert to PyTorch tensors
    train_dataset = TensorDataset(
        torch.tensor(X_train, dtype=torch.float32),
        torch.tensor(y_train, dtype=torch.long)
    )
    val_dataset = TensorDataset(
        torch.tensor(X_val, dtype=torch.float32),
        torch.tensor(y_val, dtype=torch.long)
    )

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)

    print(f"\n✓ DataLoaders ready – {len(train_loader)} training batches, {len(val_loader)} validation batches")

    # Initialize model
    model = FusionModel(
        input_dim=N_FEATURES,
        hidden_dim=HIDDEN_DIM,
        n_layers=NUM_LAYERS,
        n_classes=N_CLASSES,
        embedding_dim=EMBEDDING_DIM,
        dropout=DROPOUT
    ).to(DEVICE)

    print(f"\n✓ Model initialized on {DEVICE}")
    print(f"  • Parameters: {sum(p.numel() for p in model.parameters()):,}")

    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=5)

    # Training loop
    print("\n" + "=" * 70)
    print("TRAINING LOOP")
    print("=" * 70)

    best_val_acc = 0.0
    history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}

    for epoch in range(NUM_EPOCHS):
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, DEVICE)
        val_loss, val_acc, val_preds, val_labels = validate_epoch(model, val_loader, criterion, DEVICE)

        scheduler.step(val_loss)

        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), os.path.join(MODEL_DIR, 'fusion_model.pth'))

        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)

        print(f"Epoch {epoch+1:02d}/{NUM_EPOCHS} │ "
              f"Train: loss={train_loss:.4f} acc={train_acc:.2f}% │ "
              f"Val: loss={val_loss:.4f} acc={val_acc:.2f}%")

    print(f"\n✓ Training complete – best validation accuracy: {best_val_acc:.2f}%")
    print(f"✓ Model checkpoint saved to training/fusion_model.pth")

    # Final evaluation
    print("\n" + "=" * 70)
    print("FINAL EVALUATION")
    print("=" * 70)

    if SKLEARN_AVAILABLE:
        print("\nClassification Report:")
        print(classification_report(val_labels, val_preds, target_names=INTENT_LABELS, digits=4))
        print("Confusion Matrix:")
        print(confusion_matrix(val_labels, val_preds))
    else:
        print("  (sklearn not available – skipping detailed metrics)")

    return model, history


def export_onnx(model):
    """Export model to ONNX and apply dynamic quantization."""
    if not TORCH_AVAILABLE or not ONNX_AVAILABLE:
        print("[WARN] Skipping ONNX export – required libraries missing.")
        return

    print("\n" + "=" * 70)
    print("ONNX EXPORT")
    print("=" * 70)

    # Ensure model is in eval mode
    model.eval()

    # Dummy input for export
    dummy_input = torch.randn(1, SEQUENCE_LENGTH, N_FEATURES).to(DEVICE)

    # Export path
    os.makedirs(PUBLIC_DIR, exist_ok=True)
    onnx_path = os.path.join(PUBLIC_DIR, 'fusion_model.onnx')
    quantized_path = os.path.join(PUBLIC_DIR, 'fusion_model_quantized.onnx')

    # Export
    print(f"\nExporting to ONNX (opset 15)...")
    torch.onnx.export(
        model,
        dummy_input,
        onnx_path,
        input_names=['input'],
        output_names=['intent_logits', 'embedding'],
        dynamic_axes={
            'input': {0: 'batch_size'},
            'intent_logits': {0: 'batch_size'},
            'embedding': {0: 'batch_size'}
        },
        opset_version=15,
        do_constant_folding=True
    )
    print(f"✓ ONNX model saved: {onnx_path} ({os.path.getsize(onnx_path) / 1024:.1f} KB)")

    # Dynamic quantization
    print("\nApplying dynamic quantization...")
    quantize_dynamic(
        model_input=onnx_path,
        model_output=quantized_path,
        weight_type=QuantType.QUInt8,
        per_channel=False,
        reduce_range=True
    )
    print(f"✓ Quantized model saved: {quantized_path} ({os.path.getsize(quantized_path) / 1024:.1f} KB)")

    # Verify with onnxruntime
    print("\nVerifying ONNX model...")
    try:
        import onnxruntime as ort
        sess = ort.InferenceSession(quantized_path, providers=['CPUExecutionProvider'])
        input_name = sess.get_inputs()[0].name

        test_input = np.random.randn(2, SEQUENCE_LENGTH, N_FEATURES).astype(np.float32)
        outputs = sess.run(None, {input_name: test_input})

        intent_probs = F.softmax(torch.tensor(outputs[0]), dim=1).numpy()
        embeddings = outputs[1]

        print(f"✓ Inference successful!")
        print(f"  • Input shape: {test_input.shape}")
        print(f"  • Intent logits shape: {outputs[0].shape}")
        print(f"  • Embedding shape: {outputs[1].shape}")
        print(f"  • Sample intent probabilities: {intent_probs[0]}")
        print(f"  • Sample embedding norm: {np.linalg.norm(embeddings[0]):.4f}")

    except ImportError:
        print("[WARN] onnxruntime not available – skipping inference test.")
    except Exception as e:
        print(f"[WARN] ONNX verification failed: {e}")


# ── Main ────────────────────────────────────────────────────────────────────
def main():
    print("\n" + "=" * 70)
    print("INTENTSCOPE FUSION MODEL TRAINING")
    print("=" * 70)

    if not TORCH_AVAILABLE:
        print("\n[INFO] PyTorch not installed. Creating dummy ONNX placeholder.")
        os.makedirs(PUBLIC_DIR, exist_ok=True)
        placeholder_path = os.path.join(PUBLIC_DIR, 'fusion_model.onnx')
        with open(placeholder_path, 'wb') as f:
            f.write(b'ONNX_MODEL_PLACEHOLDER')
        print(f"✓ Created placeholder: {placeholder_path}")
        print("\nTo train the real model, install PyTorch: https://pytorch.org/get-started/locally/")
        sys.exit(0)

    # Step 1: Train
    model, history = train_model()
    if model is None:
        sys.exit(1)

    # Step 2: Export
    export_onnx(model)

    # Save training history
    with open(os.path.join(MODEL_DIR, 'training_history.json'), 'w') as f:
        json.dump(history, f, indent=2)
    print(f"\n✓ Training history saved to training/training_history.json")

    print("\n" + "=" * 70)
    print("✅ TRAINING PIPELINE COMPLETE")
    print("=" * 70)
    print("\nOutputs:")
    print(f"  • {MODEL_DIR}/fusion_model.pth          (PyTorch checkpoint)")
    print(f"  • {PUBLIC_DIR}/fusion_model.onnx       (FP32 ONNX)")
    print(f"  • {PUBLIC_DIR}/fusion_model_quantized.onnx (INT8 quantized)")
    print("\nNext: integrate the ONNX model into the browser using onnxruntime-web.")


if __name__ == "__main__":
    main()
