# Contributing to IntentScope

Thank you for your interest in contributing! IntentScope is an ambitious project aiming to be the most advanced purely client-side intention-reading platform.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Adding a New Sensor Modality](#adding-a-new-sensor-modality)
- [Improving the Fusion Model](#improving-the-fusion-model)
- [Testing](#testing)
- [Style Guidelines](#style-guidelines)
- [Submitting Changes](#submitting-changes)
- [Community](#community)

## Code of Conduct

This project adheres to the [Contributor Covenant](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.10+ (optional, for training models)
- Modern browser with WebGPU support (Chrome 113+, Edge 113+)

### Fork & Clone

```bash
git clone https://github.com/YOUR_USERNAME/IntentScope.git
cd IntentScope
```

### Install Dependencies

```bash
# Frontend
npm install

# Optional: Training environment
cd training
python -m venv venv
# Activate (Windows PowerShell):
venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate
pip install -r requirements.txt
cd ..
```

### Run Development Server

```bash
npm run dev
# → http://localhost:3000
```

The app will prompt for camera/microphone permissions. Click "Allow" to start sensor capture.

## Development Workflow

1. **Create a branch** for your feature/fix:
   ```bash
   git checkout -b feat/my-new-sensor
   ```

2. **Make changes** following our style guidelines (below).

3. **Run tests**:
   ```bash
   npm test              # Unit tests
   npm run test:e2e      # Playwright e2e tests
   npm run lint          # ESLint
   ```

4. **Test manually** in browser:
   - Open http://localhost:3000
   - Navigate through pages
   - Check console for errors
   - Verify sensors work (if applicable)

5. **Commit** with conventional commit messages:
   ```bash
   git add .
   git commit -m "feat: add galvanic skin response sensor"
   ```

6. **Push** and open a Pull Request:
   ```bash
   git push origin feat/my-new-sensor
   ```
   Then open PR on GitHub with a clear description.

## Adding a New Sensor Modality

IntentScope is designed to be extensible. Follow these steps to add a new sensor:

### 1. Create a Web Worker

File: `src/workers/<modality>Worker.js`

```javascript
// Worker structure
self.onmessage = async (event) => {
  const { type } = event.data

  if (type === 'init') {
    // Initialize your sensor (camera, mic, hardware API)
    await initSensor()
    self.postMessage({ type: 'ready' })
    return
  }

  if (type === 'tick') {
    // Extract features
    const features = extractFeatures()
    self.postMessage({
      type: 'result',
      features: { /* ... */ },
      timestamp: performance.now()
    })
  }
}
```

### 2. Register Worker in SensorContext

- Add state: `const [<modality>Data, set<Modality>Data] = useState(null)`
- Add ref: `const <modality>WorkerRef = useRef(null)`
- Initialize in `startSensors()`: create worker, set `onmessage` handler
- In handler: update state via `set<Modality>Data()`, push to `aggregatorRef.current.push()`
- Cleanup in `stopSensors()`: terminate worker

### 3. Extend SensorAggregator

File: `src/utils/sensorAggregator.js`

Add the new modality's features to the 28-D vector:
```javascript
// In getVector():
const featureVector = [
  // Face (13): gaze_x, gaze_y, AU1..AU6
  ...face.gaze_x, face.gaze_y, ...face.au,
  // Voice (13): 13 MFCCs
  ...voice.mfcc,
  // Keyboard (2): typing_speed_norm, hold_duration_avg
  this.keyboardStats.typing_speed_norm,
  this.keyboardStats.hold_duration_avg,
  // NEW: <modality> features here (update count)
  ...newModality.features
]
```

Also update `getFeatureNames()` to include new feature labels.

### 4. Update Training Pipeline

The fusion model expects a fixed input dimension. You must:

- Update `generate_dataset.py` to generate synthetic data with the new features
- Update `train_fusion_model.py`: `INPUT_FEATURES = 28 + N` where N is new count
- Retrain the model: `python training/train_fusion_model.py`
- Replace `public/fusion_model.onnx`

### 5. Update UI

Display new sensor data on Dashboard/Analysis pages as needed.

## Improving the Fusion Model

The current model is a Bi-LSTM with attention. To improve:

### Data Collection

- Record real user sessions (with consent) via the Playground's "Record" feature
- Export scenarios as JSON, convert to `.npy` using the provided script
- Augment training data: `python training/preprocess_real_data.py`

### Model Architecture

Edit `training/train_fusion_model.py`:

```python
class FusionBiLSTM(nn.Module):
    def __init__(self, input_size, hidden_size=128, num_layers=2, num_classes=8):
        super().__init__()
        # ... modify as needed
```

Try:
- Different hidden sizes (64, 256)
- More/less layers
- Add convolutional layers before LSTM
- Change dropout rate
- Use GRU instead of LSTM
- Add regularization (L1/L2)

### Training

```bash
cd training
python train_fusion_model.py --epochs 100 --batch-size 32 --lr 0.001
```

Monitor validation accuracy and loss. Avoid overfitting.

### Export

Model auto-exports to ONNX on completion. Copy to `public/fusion_model.onnx`.

## Testing

### Unit Tests (Vitest)

Located in `src/__tests__/`.

Run:
```bash
npm test
```

Key modules:
- `sensorAggregator.test.js` – buffer filling, vector construction
- `keyboardTracker.test.js` – inter-key timing, variance
- `fusionWorker.test.js` – mock ONNX session, inference logic
- `newsEngine.test.js` – IndexedDB storage, query functions

### End-to-End Tests (Playwright)

Located in `e2e/`.

```bash
npx playwright test
```

Critical paths:
- User can start sensors and see intent predictions update
- Deception challenge flow completes
- API Playground endpoints respond
- Simulator loads scenario and plays back

Write new tests for any new feature using the Page Object Model.

### Manual Testing

- Test with no camera/mic: graceful errors
- Rapid sensor toggle: no worker leaks
- Slow network: news cache fallback works
- Browser console: zero errors

Use Chrome DevTools → Application → Service Workers to debug workers.

## Style Guidelines

### JavaScript/JSX

- **Indentation:** 2 spaces
- **Semicolons:** Yes
- **Quotes:** Single quotes
- **Naming:** camelCase for variables/functions; PascalCase for components; UPPER_CASE for constants
- **Imports:** group by type (React, third-party, internal)
- **Components:** functional with hooks; no class components
- **File names:** kebab-case (`use-starfield.js`, `RobotLab.jsx`)

### Python

- Follow PEP 8
- Docstrings for all functions/classes
- Type hints where practical
- Try/except fallbacks for optional dependencies
- Verbose console prints (already project convention)

### CSS

- Use custom properties (variables) defined in `index.css`
- BEM-like naming: `.component-modifier`
- Black/gold theme colors only (`--color-gold`, `--color-dark`)

### Comments

- Write concise comments explaining WHY, not WHAT
- For complex algorithms: pseudo-code explanation
- For fallbacks: note the reason and error condition

## Submitting Changes

### Before Submitting

1. All tests pass (`npm test && npm run test:e2e`)
2. Lint clean (`npm run lint`)
3. No console errors in browser
4. Build succeeds (`npm run build`)
5. Updated documentation if needed

### Pull Request Process

1. Push your branch to GitHub
2. Open PR against `main` branch
3. Fill PR template:
   - **What** does this change do?
   - **Why** is it needed?
   - **How** did you test it?
   - **Screenshots** (if UI changes)
4. Wait for review (maintainer will run CI)
5. Address feedback, then merge

### PR Title Convention

Use [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` for new features
- `fix:` for bug fixes
- `refactor:` code restructuring
- `test:` adding tests
- `docs:` documentation updates
- `chore:` maintenance tasks

Example: `feat: add galvanic skin response sensor to fusion pipeline`

## Community

- **Issues:** Report bugs or request features on GitHub Issues
- **Discussions:** Use GitHub Discussions for questions/ideas
- **Discord:** Coming soon

### Good First Issues

Look for labels `good first issue` or `help wanted` in Issues.

## 📚 Additional Resources

- [Architecture docs](docs/ARCHITECTURE.md) (soon)
- [Training guide](training/README.md)
- [API reference](docs/API.md) (soon)

---

**Happy contributing!** Together we'll build the future of intention reading.
