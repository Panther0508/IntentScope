# Architecture

This document provides a deep dive into IntentScope's architecture, data flow, and model details.

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Browser (Client)                       │
├─────────────────────────────────────────────────────────────────┤
│  Web Workers                                                    │
│  ├── Face Worker    – MediaPipe → gaze + 6 Action Units       │
│  ├── Voice Worker   – Meyda → 13 MFCCs + pitch, loudness, ... │
│  └── Fusion Worker  – ONNX Runtime (Bi-LSTM) → intent probs   │
├─────────────────────────────────────────────────────────────────┤
│  Main Thread                                                     │
│  ├── React App (Routing: Home, Dashboard, Analysis, etc.)     │
│  ├── SensorContext – Global state, worker lifecycle            │
│  ├── SensorAggregator – 50-timestep sliding buffer (28-D)     │
│  ├── NewsEngine – Fetch + cache world knowledge               │
│  └── AINarrator – WebLLM Llama-3 local chat                   │
├─────────────────────────────────────────────────────────────────┤
│  IndexedDB (Dexie) – News cache, scenario storage             │
└─────────────────────────────────────────────────────────────────┘
```

## Sensor Pipeline

### Face Tracking (MediaPipe)

MediaPipe's FaceLandmarker (tasks-vision) runs in a dedicated Web Worker. Each video frame goes through:

1. **Landmark detection** – 468 3D face landmarks (GPU-accelerated)
2. **Feature extraction**:
   - **Gaze vector** (x, y) – computed from iris center vs eye corners
   - **Action Units** (AU1, AU2, AU4, AU6, AU10, AU12) – derived from facial region deformations

Output sent to main thread as `{ gaze_x, gaze_y, au: [6 values], timestamp }`.

### Voice Stress Analysis (Meyda)

Audio is captured via `AudioContext.createMediaStreamSource` → `ScriptProcessor`. Raw PCM chunks forwarded to voice worker.

Meyda analyzer extracts per ~1-second chunks:
- **13 MFCCs** (Mel-frequency cepstral coefficients)
- **Fundamental frequency (pitch)**
- **Loudness** (RMS)
- **Jitter** (pitch variability)
- **Shimmer** (amplitude variability)

Results posted as `{ mfcc: [...], pitch, loudness, jitter, shimmer, timestamp }`.

### Keyboard Dynamics

`keyboardTracker.js` attaches a global `keydown` listener and computes:
- `inter_key_interval` – average time between consecutive key presses
- `hold_duration_avg` – mean key hold time
- `variance` – standard deviation of intervals (measure of rhythm consistency)
- `typing_speed` – characters per minute

Sent whenever these stats update (~on each keypress).

### Aggregation & Normalization

The SensorAggregator maintains a ring buffer of 50 timesteps. Each incoming sensor packet is appended; if a timestamp for the same time already contains different modalities, they are merged.

Features are normalized to roughly [-1, 1] or [0,1] to match training data distribution:
- MFCCs clipped to [-3, 3] then scaled
- Pitch, loudness in [0, 1]
- Gaze coordinates from normalized image space (0–1)
- Keyboard stats from empirical ranges

When buffer fills (50 timesteps), `getFeatureVector()` returns a Float32Array of length 1400 (50 × 28).

## Fusion Model

### Architecture (PyTorch → ONNX)

Training pipeline (`training/train_fusion_model.py`) defines:

```python
class FusionBiLSTM(nn.Module):
    - Input:  (batch, 50, 28)
    - LSTM:  hidden_size=128, num_layers=2, bidirectional, batch_first=True
    - Attention:  softmax over timesteps to compute weighted sum of hidden states
    - Two heads:
        • intent_logits   → Linear(128*2, 8)   → CrossEntropyLoss
        • embedding      → Linear(128*2, 32)  → Cosine similarity loss
```

Training uses:
- Synthetic data generator (`generate_dataset.py`) with class priors
- Optional real dataset concatenation (MPIIGaze, DOLOS, AffectNet, Bag-of-Lies)
- Adam optimizer, ReduceLROnPlateau scheduler
- Early stopping on validation loss

Export: `torch.onnx.export` with opset 15, dynamic axes for batch. Post-training dynamic INT8 quantization (optional, reduces size ~4×).

### Inference

ONNX Runtime Web loads `public/fusion_model.onnx`. Workers run in a separate thread to avoid blocking the UI.

If model fails to load (missing file, unsupported provider), the fusion worker falls back to a heuristic predictor (`simulateIntent`) that approximates intent probabilities from recent feature statistics.

## State Management

React Context (`SensorContext.jsx`) is the single source of truth for sensor data, fusion results, and simulation state. Child components subscribe via `useSensor()` hook.

The context also:
- Spawns/terminates workers on sensor start/stop
- Drives the 20Hz fusion loop with `requestAnimationFrame`
- Dispatches updates to the dev API bridge (WebSocket → local HTTP server)

## World Knowledge Engine

`newsEngine.js`:
- Fetches concurrently from HN Algolia, Dev.to, Reddit
- Stores articles in Dexie `news` table (IDB)
 `buildNewsQuery()` maps the top intent to search keywords and boosts security terms if deception > 0.3
- `getRelevantHeadlines(query)` scores articles by keyword overlap and returns top matches

Background refresh every 5 minutes.

## AI Narrator

`AINarrator.jsx` uses `@mlc-ai/web-llm` to run Llama-3-8B-Instruct-q4f16_1 via WebGPU.

System prompt template:

```
You are an AI observer monitoring the user's cognitive state in real-time.
Current Sensor Data:
- Intent probabilities: {Exploring: 0.12, Deception: 0.07, ...}
- Deception probability: 23%
- Face: gaze=(0.4,0.2), AUs=[0.1,0.2,...]
Latest News Headlines: [...]
Provide a concise observation (max 2 sentences) in a sci-fi observer tone.
```

Responses stream token-by-token in the chat bubble.

## Deception Detection

Deception probability is extracted directly from the "Deception" class probability from the fusion model. It is displayed as a percentage gauge that fills clockwise; color changes from gold (<50%) to red (>50%).

The DeceptionChallenge page presents a series of personal questions; each answer updates the gauge.

## Intent-Driven Robotics (RobotLab)

RobotLab visualizes a 3D arm (Three.js – pending implementation). The actual logic is a simple state machine in React:

```javascript
if (intentProbabilities.RobotPick > 0.7)  -> executePick()
else if (intentProbabilities.RobotPlace > 0.7) -> executePlace()
else if (intentProbabilities.Deception > 0.6) -> suspend()
else -> idle()
```

The mode toggle switches between "Intent" mode (autonomous) and "Expression" mode (user controls avatar manually – not yet implemented).

## Dev Tools

### Local API Gateway (dev-only)

When running `npm run dev`:
- `vite-plugin-local-api.js` spawns `dev/local-api-server.js`
- Server creates a WebSocket endpoint at `ws://localhost:9001`
- Browser-side `apiBridge.js` sends the latest state every 100ms
- HTTP `/api/*` routes are proxied from Vite to the local server

Endpoints: `/api/sensors`, `/api/intent`, `/api/narration`, `/api/robot`, `/api/status`

### Diagnostics Overlay

Press `Ctrl+Shift+D` to display a semi-transparent overlay with:
- Live FPS per worker
- Inference latency histogram
- Memory usage
- Recent event log
- Canvas-based FPS graph

### Sensor Simulator & Replay

Visit `/playground` to load pre-recorded scenarios from `public/scenarios/`. The simulator feeds recorded frames directly into the SensorAggregator, bypassing workers, and the full pipeline (fusion, narrator, robot) reacts identically to live data. Users can also record their own sessions (downloads as JSON).

## Deployment

### Vite Build

Production build generates static assets in `dist/`. Dynamic base path configured:

```js
base: process.env.NODE_ENV === 'production' ? '/IntentScope/' : '/'
```

This ensures correct asset resolution when served from GitHub Pages at `https://panther0508.github.io/IntentScope/`.

### GitHub Pages

`.github/workflows/deploy.yml` uses `peaceiris/actions-gh-pages@v4` to push the `dist/` folder to the `gh-pages` branch. Workflow runs on every push to `main`.

### Permissions & Security

- **Camera/Mic**: requested via `getUserMedia`; requires user gesture and HTTPS (GitHub Pages is HTTPS)
- **Web Workers**: COOP/COEP headers set in Vite dev server to enable `SharedArrayBuffer` (needed for high-resolution time in audio processing)
- **No external data exfiltration**: All inference local; news fetch uses public APIs; no personal data stored beyond IndexedDB (local only)

## Performance Targets

- Face worker: ≥20 FPS on mid-tier device
- Voice worker: ~10–20 feature vectors per second
- Fusion inference: ≤10ms per tensor (WASM), ≤5ms (WebGL)
- Overall pipeline end-to-end latency: <100ms
- Page load (first visit): ~3–4s plus LLM model download (~4GB) if used

## Future Extensibility

The design encourages adding new sensors, fusion models, or UI themes. The worker interface is stable; just implement the `{ type: 'init' / 'result' / 'error' }` protocol and register in `SensorContext.jsx`.

---

*Last updated: Phase 4 (Q2 2026)*
