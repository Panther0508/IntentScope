module.exports = {
  root: true,
  env: {
    browser: true,
    es2020: true,
  },
  extends: [
    'eslint:recommended',
    'plugin:react/recommended',
    'plugin:react-hooks/recommended',
  ],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
  },
  plugins: ['react', 'react-hooks', 'react-refresh'],
  rules: {
    'react/react-in-jsx-scope': 'off',
    'react/prop-types': 'off',
    'react/jsx-no-target-blank': 'off',
    'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],
    'no-console': ['warn', { allow: ['warn', 'error', 'log'] }],
    'no-unused-vars': ['warn', { 'args': 'none', 'varsIgnorePattern': '^_', 'argsIgnorePattern': '^_' }],
  },
  settings: {
    react: {
      version: '18.3',
    },
  },
  ignorePatterns: [
    'dist',
    'node_modules',
    'e2e',
    'public/scenarios',
    'training/output',
    'dev',
    'vite-plugin-local-api.js',
    'vite.config.js',
    'playwright.config.js',
    'scripts',
  ],
  overrides: [
    {
      files: ['**/__tests__/**'],
      env: { node: true },
      globals: {
        vi: 'readonly',
        describe: 'readonly',
        it: 'readonly',
        test: 'readonly',
        expect: 'readonly',
        beforeEach: 'readonly',
        afterEach: 'readonly',
        beforeAll: 'readonly',
        afterAll: 'readonly',
      },
    },
  ],
}
