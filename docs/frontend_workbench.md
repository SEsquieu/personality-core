# Frontend Workbench

The Vite + React workbench is the first visual interface for Personality Core.

It is intentionally an operator surface, not a landing page. The first screen is a Core Stack Editor for tuning installed cores in situ, with Compare mode kept as the quick demo lane.

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

- left: mode switch, model, demo prompt, token cap, stack/preset controls
- center: prompt editor, resolve/compile/run actions, generated output
- right: diagnostics, resolved traits, per-core scores, conflicts, core trace

The core interaction is:

```text
install cores -> tune strengths -> resolve/compile -> run stack -> validate output
```

Compare mode still supports:

```text
same model + same prompt + different saved core stack = visible behavior differences
```

## Backend Routes

The frontend uses native Personality Core routes:

- `GET /v1/cores`
- `GET /v1/personalities`
- `POST /v1/stack/resolve`
- `POST /v1/stack/compile`
- `POST /v1/stack/run`
- `POST /v1/compare`

The OpenAI-compatible `/v1/chat/completions` route remains available for external clients.

## Next UI Improvements

- stabilizer before/after view
- saved comparison history
- model/backend health indicator
- save/load custom stack JSON
- edit core params beyond strength
