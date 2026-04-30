# Frontend Workbench

The Vite + React workbench is the first visual interface for Personality Core.

It is intentionally an operator surface, not a landing page. The first screen lets users run the same prompt through multiple personality presets and inspect what changed.

## Run It

Start the API:

```bash
personality-core serve --host 127.0.0.1 --port 8787
```

Start Vite:

```bash
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

The Vite dev server proxies `/v1` and `/health` to `http://127.0.0.1:8787`.

## Build It

```bash
npm run build
```

## Current UX

The workbench has three areas:

- left: model, demo prompt, preset selection, token cap
- center: prompt editor, run button, result tabs, generated output
- right: diagnostics, resolved traits, per-core scores, core trace, installed rules

The core interaction is:

```text
same model + same prompt + different core stack = visible behavior differences
```

## Backend Routes

The frontend uses native Personality Core routes:

- `GET /v1/cores`
- `GET /v1/personalities`
- `POST /v1/compare`

The OpenAI-compatible `/v1/chat/completions` route remains available for external clients.

## Next UI Improvements

- editable custom core stack with sliders
- single-run mode next to compare mode
- stabilizer before/after view
- compiled prompt drawer
- saved comparison history
- model/backend health indicator
