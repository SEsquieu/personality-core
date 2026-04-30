# Core Creator

Core Creator turns a plain-language behavior intent into a schema-valid Personality Core JSON file.

The first implementation uses deterministic drafting so it works without spending model tokens. It is designed so an AI-assisted drafting pass can be added later while keeping the same validation and install path.

## Workflow

```text
describe intent -> draft JSON -> edit JSON -> validate -> install -> add to stack
```

## Frontend

Open the workbench:

```bash
npm run dev
```

Use the `Core Creator` mode:

- enter a core name
- describe the desired behavior
- click `Draft`
- review or edit the JSON
- click `Validate`
- click `Install`

Installed cores are written to `cores/{core_id}.json`, the registry reloads, and the new core is added to the active stack.

## API

Draft:

```http
POST /v1/cores/draft
```

Validate:

```http
POST /v1/cores/validate
```

Install:

```http
POST /v1/cores/install
```

Install rejects duplicate core IDs unless `overwrite` is true.

## Safety

The registry validates:

- ID format
- trait delta range
- default strength range
- required schema fields

Generated drafts include conservative boundaries:

- `preserve_task_accuracy`
- `no_personal_attacks`
- `no_slurs`

Future AI-assisted drafting should still pass through the same validation and install endpoint.
