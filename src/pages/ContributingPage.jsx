export default function ContributingPage() {
  const content = `# Embedded Contribute Page

## Code of Conduct

Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) – we follow the Contributor Covenant.

## Getting Started

### Prerequisites

- **Node.js** 18+ and npm
- Modern browser with WebGPU support (Chrome 113+)

### Setup

\`\`\`bash
git clone https://github.com/YOUR_USERNAME/IntentScope.git
cd IntentScope
npm install
npm run dev
\`\`\`

The app will be at http://localhost:3000. Allow camera/mic when prompted.

## Running Tests

\`\`\`bash
npm test              # Vitest unit tests
npm run test:e2e      # Playwright e2e tests
npm run lint          # ESLint with zero warnings
\`\`\`

## Project Structure

\`\`\`
IntentScope/
├── src/
│   ├── components/    # Reusable UI (Layout, NewsTicker, DiagnosticsOverlay)
│   ├── context/       # SensorContext – global sensor state
│   ├── pages/         # Route components (Dashboard, RobotLab, etc.)
│   ├── services/      # newsEngine – IndexedDB news cache
│   ├── utils/         # sensorAggregator, keyboardTracker, apiBridge, simulator
│   └── workers/       # face, voice, fusion Web Workers
├── training/          # Python ML training pipeline
├── public/            # Static assets, scenario JSON files
├── e2e/               # Playwright end-to-end tests
├── __tests__/         # Vitest unit tests
└── docs/              # Architecture deep-dive
\`\`\`

## Adding a Sensor

1. Create a new Web Worker in \`src/workers/\` (e.g., \`poseWorker.js\`)
2. Export an \`init\` message handler that posts \`{ type: 'result', ... }\` messages
3. Register in \`SensorContext.jsx\` – add worker init, message handler, cleanup
4. Update \`sensorAggregator.js\` to include the new features in the 28-D vector
5. Update \`training/generate_dataset.py\` and retrain the fusion model

## Improving the Fusion Model

- Collect more data (real or synthetic) in \`training/data/\`
- Edit \`training/train_fusion_model.py\` to adjust architecture/hyperparameters
- Run \`python train_fusion_model.py\` to export updated ONNX to \`public/fusion_model.onnx\`
- Restart the dev server to load new model

## Pull Request Process

1. Fork the repo, create a feature branch: \`git checkout -b feat/your-feature\`
2. Write clear, test-covered code. Follow the existing style (2 spaces, semicolons, single quotes).
3. Run \`npm run lint && npm test && npm run test:e2e\`. All must pass.
4. Commit using [Conventional Commits](https://www.conventionalcommits.org): \`feat:\` or \`fix:\` prefixes.
5. Push and open a PR against \`main\`.

## Need Help?

- Open an issue on GitHub: https://github.com/Panther0508/IntentScope/issues
- Use Discussions for questions/ideas: https://github.com/Panther0508/IntentScope/discussions

Happy contributing!`

  return (
    <div className="prose max-w-none p-4">
      <pre className="whitespace-pre-wrap font-schema text-sm">{content}</pre>
    </div>
  )
}
