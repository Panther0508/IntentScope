# Training Pipeline – IntentScope

This directory contains scripts to generate synthetic multimodal data and train the intention fusion model. The output is an ONNX model that runs in the browser via `onnxruntime-web`.

---

## Setup

1. Install Python 3.10+ (recommended: Python 3.12).
2. Install dependencies:

```bash
pip install -r requirements.txt
```

**Note:** If you don't have a GPU, PyTorch will fall back to CPU automatically.

---

## Usage

```bash
# Step 1: Generate synthetic dataset
python generate_dataset.py

# Step 2: Train the fusion model
python train_fusion_model.py
```

### What each script does

### `generate_dataset.py`

- Creates a synthetic time-series dataset with shape `(N, 50, 28)`.
- 8 intention classes: `Exploring`, `BuyIntent`, `Hesitation`, `Deception`, `ActionConfirm`, `RobotPick`, `RobotPlace`, `RobotIdle`.
- Features per timestep:
  - 6 facial Action Units (AU1, AU2, AU12, AU15, AU20, AU26)
  - 2 gaze coordinates (x, y)
  - 13 MFCC coefficients
  - pitch, loudness, jitter, shimmer
  - 4 keyboard statistics (inter-key interval, hold duration, variance, typing speed)
- Saves to `training/data/` as NumPy arrays and `label_map.json`.

### `train_fusion_model.py`

- Loads the training and validation sets.
- Builds a PyTorch LSTM-based fusion model:
  - Bidirectional LSTM (2 layers, 64 hidden units)
  - Self-attention pooling
  - Two output heads: 8-class softmax + 32-dim embedding
- Trains for 30 epochs with Adam optimizer and ReduceLROnPlateau scheduler.
- Saves best checkpoint to `training/fusion_model.pth`.
- Exports to ONNX (`public/fusion_model.onnx`) with opset 15.
- Applies dynamic INT8 quantization → `public/fusion_model_quantized.onnx`.
- Runs an inference test to verify the ONNX model.

---

## Output Files

| File | Description |
|------|-------------|
| `training/data/X_train.npy` | Training feature sequences (shape: `[N_train, 50, 28]`) |
| `training/data/y_train.npy` | Training labels (0–7) |
| `training/data/X_val.npy` | Validation sequences |
| `training/data/y_val.npy` | Validation labels |
| `training/data/label_map.json` | Intent label ↔ index mapping |
| `training/fusion_model.pth` | PyTorch checkpoint |
| `public/fusion_model.onnx` | FP32 ONNX model (for browser) |
| `public/fusion_model_quantized.onnx` | INT8 quantized ONNX (smaller, faster) |

---

## Running on Google Colab (Free GPU)

```python
# In a Colab notebook cell:
!pip install -r training/requirements.txt
!python training/generate_dataset.py
!python training/train_fusion_model.py
```

The Colab GPU will speed up training significantly.

---

## Reproducibility

- Random seeds are fixed (`np.random.seed(42)` and `torch.manual_seed(42)`) for deterministic data generation.
- Model checkpoints use `torch.save(model.state_dict())` and can be reloaded with identical architecture.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `CUDA out of memory` | Reduce `BATCH_SIZE` in `train_fusion_model.py` |
| `ModuleNotFoundError: No module named 'torch'` | Run `pip install torch` |
| `onnxruntime not available` | The ONNX export step will be skipped. Install with `pip install onnxruntime` for verification. |
| Slow training on CPU | Reduce `NUM_EPOCHS` or `HIDDEN_DIM` |

---

## Technical Notes

- The synthetic dataset is rule-based, not learned from real humans. It encodes *heuristic associations*:
  - `BuyIntent` → stable central gaze, high AU12 (smile), elevated pitch, fast typing.
  - `Hesitation` → erratic gaze, high brow furrow (AU1+AU2), voice tremor, slow irregular typing.
  - `Deception` → averted gaze, controlled AUs, stiff voice, deliberate keystrokes.
  - `RobotPick/Place` → gaze shifts to target, minimal keyboard activity.
- These patterns are amplified with Gaussian noise to simulate sensor noise.
- In Phase 3, the ONNX model will be loaded directly into the browser with `onnxruntime-web` and used to predict intentions from live sensor streams in real-time.
