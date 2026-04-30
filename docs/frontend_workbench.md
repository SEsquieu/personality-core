# Frontend Workbench

The Vite + React workbench is the first visual interface for Personality Core.

It is intentionally an operator surface, not a landing page. The first screen is a Core Stack Editor for tuning installed cores in situ, with Compare mode kept as the quick demo lane.

## Run It

Start the workbench:

```bash
npm run dev
```

`npm run dev` checks for the API at `http://127.0.0.1:8787`, starts it when needed, and then launches Vite.

To run the API and UI separately:

```bash
personality-core serve --host 127.0.0.1 --port 8787
npm run dev:ui
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

The left panel is organized as collapsible workflow sections:

- Runtime
- Input
- Installed Stack
- Load Preset
- Core Library

Installed Stack stays open by default. Runtime, Input, Load Preset, and Core Library are collapsed so the stack remains the primary object on screen.

Each installed core is a compact row with its strength visible. Expanding a row reveals description, the strength slider, and trait deltas.

Core Creator mode lets users load a valid JSON template, draft through the selected model endpoint, edit, validate, and install new core JSON files. Installed cores are immediately available in the Stack Editor.

The Runtime panel exposes provider model examples and a `Test Provider` check so users can verify Ollama, OpenAI, OpenRouter, or LM Studio before spending a longer generation on stack output or core drafting.

The Runtime panel also exposes contract fail policy. For contract cores such as `structured_json_output_core`, users can choose whether drift should warn, repair, block, or return raw output.

Diagnostics include active contracts and runtime mutations so users can see which behavior is being prompted, evaluated, or applied by the backend.

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
- `GET /v1/cores/template`
- `GET /v1/personalities`
- `GET /v1/providers`
- `POST /v1/providers/health`
- `POST /v1/cores/draft`
- `POST /v1/cores/validate`
- `POST /v1/cores/install`
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
