# Vistaar Flask Backend

## Project Overview

This project is a Flask backend for managing versioned configuration data stored in Postgres (via Supabase).  
Each write operation creates a new version in `config_versions`, and runtime reads use in-memory cached latest snapshots.

Config domains covered:
- glossary
- ambiguity
- aliases (en-gu)
- aliases (english)
- forbidden
- preferred
- schemes
- config management (reload, rollback, versions)

---

## Setup Instructions

### Prerequisites
- Python 3.10+ (recommended)
- Required Python packages installed (Flask, Supabase client, etc.)

### Run locally
From project root:

```bash
python -m Utils.APIs
```

Default Flask debug server starts on:
- `http://127.0.0.1:5000`

### Environment variables
The app reads:
- `SUPABASE_URL`
- `SUPABASE_KEY`
- Optional write metadata fallback:
  - `USER`
  - `USERNAME`

You may also send header:
- `X-Triggered-By`

---

## API Endpoints

## Glossary

### `GET /glossary`
- **Description:** Search glossary entries.
- **Query params:**
  - `term` (optional): search string
  - `limit` (optional): max results
- **Request body:** none
- **Example request:**

```bash
curl "http://127.0.0.1:5000/glossary?term=milk&limit=10"
```

- **Example response (shape):**

```json
[
  {
    "en": "milk",
    "gu": ["દૂધ"],
    "transliteration": ["dudh"]
  }
]
```

### `POST /glossary`
- **Description:** Publish a new glossary version from provided snapshot payload.
- **Exact request body format:**

```json
{
  "snapshot": {},
  "note": "optional",
  "triggered_by": "optional"
}
```

- **Example request:**

```bash
curl -X POST "http://127.0.0.1:5000/glossary" \
  -H "Content-Type: application/json" \
  -d "{\"snapshot\":{\"test_term\":{\"gu\":[\"ટેસ્ટ\"],\"transliteration\":[\"test\"]}},\"note\":\"add test term\"}"
```

- **Example response (shape):**

```json
{
  "ok": true,
  "config_type": "glossary_terms",
  "version_number": 12,
  "row": {},
  "skipped": false,
  "versions": {}
}
```

### `PATCH /glossary`
- **Description:** Edit value for an existing glossary key and publish a new version.
- **Exact request body format (as parsed in code):**

```json
{
  "entry": {
    "key": "existing_key",
    "value": {}
  },
  "note": "optional"
}
```

Accepted key aliases in `entry`:
- `key` or `input_key` or `term`

Accepted value aliases in `entry`:
- `value` or `new_value` or `output` or `replacement`

- **Example request:**

```bash
curl -X PATCH "http://127.0.0.1:5000/glossary" \
  -H "Content-Type: application/json" \
  -d "{\"entry\":{\"key\":\"milk\",\"value\":{\"gu\":[\"દૂધ\"],\"transliteration\":[\"dudh\"]}},\"note\":\"edit milk\"}"
```

- **Example response:**

```json
{
  "ok": true,
  "message": "milk has been edited",
  "version_number": 13,
  "versions": {}
}
```

### `DELETE /glossary`
- **Description:** Delete an existing glossary key and publish a new version.
- **Exact request body format:**

```json
{
  "entry": {
    "key": "existing_key"
  },
  "note": "optional"
}
```

Accepted key aliases in `entry`:
- `key` or `input_key` or `term`

- **Example request:**

```bash
curl -X DELETE "http://127.0.0.1:5000/glossary" \
  -H "Content-Type: application/json" \
  -d "{\"entry\":{\"key\":\"milk\"},\"note\":\"remove milk\"}"
```

- **Example response:**

```json
{
  "ok": true,
  "message": "milk has been deleted",
  "version_number": 14,
  "versions": {}
}
```

---

## Ambiguity

Existing endpoint comments (kept verbatim):

```text
#right now to update a row in ambiguity, we can just get and add a new term, or we can add a full snapshot
#which is a list of objects
#
#patch being used to add a new value
```

### `GET /ambiguity`
- **Description:** Search ambiguity entries.
- **Query params:**
  - `term` (optional)
  - `limit` (optional)
- **Request body:** none
- **Example request:**

```bash
curl "http://127.0.0.1:5000/ambiguity?term=દૂધ&limit=10"
```

- **Example response (shape):**

```json
[
  {
    "gu_terms": ["દૂધ"],
    "type": "ask",
    "rule": "..."
  }
]
```

### `PATCH /ambiguity`
- **Description:** Add a new ambiguity entry (append behavior with versioning).
- **Exact request body format:**

```json
{
  "entry": {
    "gu_terms": ["..."],
    "type": "hardcode",
    "rule": "...",
    "context": "optional"
  },
  "note": "optional"
}
```

`type` must be `"hardcode"` or `"ask"`.

- **Example request:**

```bash
curl -X PATCH "http://127.0.0.1:5000/ambiguity" \
  -H "Content-Type: application/json" \
  -d "{\"entry\":{\"gu_terms\":[\"ટેસ્ટ\"],\"type\":\"ask\",\"rule\":\"ask user\"},\"note\":\"add ambiguity\"}"
```

- **Example response:**

```json
{
  "ok": true,
  "message": "ambiguity entry added",
  "new_count": 42,
  "version": 9,
  "versions": {}
}
```

---

## Aliases (en-gu)

Existing endpoint comments (kept verbatim):

```text
# {
#   "entry": {
#     "canonical_en": "test",
#     "gu_aliases":["test"]
#   }
# }
#
# {
#   "entry": {
#     "key": "artificial insemination"
#   }
# } for delete method
#
#patch being used to add a new value
```

### `GET /aliases/en-gu`
- **Description:** Search en-gu alias mappings.
- **Query params:**
  - `term` (optional)
  - `limit` (optional)
- **Request body:** none
- **Example request:**

```bash
curl "http://127.0.0.1:5000/aliases/en-gu?term=test&limit=10"
```

- **Example response (shape):**

```json
[
  {
    "canonical_en": "test",
    "gu_aliases": ["ટેસ્ટ"]
  }
]
```

### `PATCH /aliases/en-gu`
- **Description:** Append new Gujarati aliases for a canonical English key.
- **Exact request body format (from comment):**

```json
{
  "entry": {
    "canonical_en": "test",
    "gu_aliases": ["test"]
  },
  "note": "optional"
}
```

- **Example request:**

```bash
curl -X PATCH "http://127.0.0.1:5000/aliases/en-gu" \
  -H "Content-Type: application/json" \
  -d "{\"entry\":{\"canonical_en\":\"test\",\"gu_aliases\":[\"ટેસ્ટ\"]},\"note\":\"append alias\"}"
```

- **Example response:**

```json
{
  "ok": true,
  "message": "en-gu aliases updated",
  "new_count": 120,
  "version": 15,
  "versions": {}
}
```

### `PUT /aliases/en-gu`
- **Description:** Replace the entire alias list for an existing canonical key.
- **Exact request body format:** same as PATCH.

```json
{
  "entry": {
    "canonical_en": "test",
    "gu_aliases": ["test"]
  },
  "note": "optional"
}
```

- **Example request:**

```bash
curl -X PUT "http://127.0.0.1:5000/aliases/en-gu" \
  -H "Content-Type: application/json" \
  -d "{\"entry\":{\"canonical_en\":\"test\",\"gu_aliases\":[\"ટેસ્ટ\",\"પરીક્ષણ\"]},\"note\":\"replace list\"}"
```

- **Example response:**

```json
{
  "ok": true,
  "entry": {
    "test": ["ટેસ્ટ", "પરીક્ષણ"]
  },
  "version_number": 16,
  "versions": {}
}
```

### `DELETE /aliases/en-gu`
- **Description:** Delete an existing canonical key from en-gu aliases.
- **Exact request body format (from comment):**

```json
{
  "entry": {
    "key": "artificial insemination"
  },
  "note": "optional"
}
```

Accepted key aliases in `entry`:
- `key` or `input_key` or `term`

- **Example request:**

```bash
curl -X DELETE "http://127.0.0.1:5000/aliases/en-gu" \
  -H "Content-Type: application/json" \
  -d "{\"entry\":{\"key\":\"test\"},\"note\":\"delete canonical\"}"
```

- **Example response:**

```json
{
  "ok": true,
  "message": "test deleted",
  "version_number": 17,
  "versions": {}
}
```

---

## Aliases (english)

Existing endpoint comments (kept verbatim):

```text
# {
#   "entry": {
#     "canonical": "udder",
#     "aliases":["xyaauu"]
#   }
# }
#patch being used to add a new value
```

### `GET /aliases/english`
- **Description:** Search english alias mappings.
- **Query params:**
  - `term` (optional)
  - `limit` (optional)
- **Request body:** none
- **Example request:**

```bash
curl "http://127.0.0.1:5000/aliases/english?term=udder&limit=10"
```

- **Example response (shape):**

```json
[
  {
    "canonical": "udder",
    "aliases": ["..."]
  }
]
```

### `PATCH /aliases/english`
- **Description:** Append aliases for canonical english key.
- **Exact request body format (from comment):**

```json
{
  "entry": {
    "canonical": "udder",
    "aliases": ["xyaauu"]
  },
  "note": "optional"
}
```

- **Example request:**

```bash
curl -X PATCH "http://127.0.0.1:5000/aliases/english" \
  -H "Content-Type: application/json" \
  -d "{\"entry\":{\"canonical\":\"udder\",\"aliases\":[\"udder-alt\"]},\"note\":\"append alias\"}"
```

- **Example response:**

```json
{
  "ok": true,
  "message": "english aliases updated",
  "new_count": 210,
  "version": 21,
  "versions": {}
}
```

### `PUT /aliases/english`
- **Description:** Replace the entire alias list for an existing canonical key.
- **Exact request body format:** same as PATCH.

```json
{
  "entry": {
    "canonical": "udder",
    "aliases": ["xyaauu"]
  },
  "note": "optional"
}
```

- **Example request:**

```bash
curl -X PUT "http://127.0.0.1:5000/aliases/english" \
  -H "Content-Type: application/json" \
  -d "{\"entry\":{\"canonical\":\"udder\",\"aliases\":[\"udder-alt1\",\"udder-alt2\"]},\"note\":\"replace list\"}"
```

- **Example response:**

```json
{
  "ok": true,
  "entry": {
    "udder": ["udder-alt1", "udder-alt2"]
  },
  "version_number": 22,
  "versions": {}
}
```

### `DELETE /aliases/english`
- **Description:** Delete an existing canonical key from english aliases.
- **Exact request body format:**

```json
{
  "entry": {
    "key": "udder"
  },
  "note": "optional"
}
```

Accepted key aliases in `entry`:
- `key` or `input_key` or `term`

- **Example request:**

```bash
curl -X DELETE "http://127.0.0.1:5000/aliases/english" \
  -H "Content-Type: application/json" \
  -d "{\"entry\":{\"key\":\"udder\"},\"note\":\"delete canonical\"}"
```

- **Example response:**

```json
{
  "ok": true,
  "message": "udder deleted",
  "version_number": 23,
  "versions": {}
}
```

---

## Forbidden

### `GET /forbidden`
- **Description:** Search forbidden mappings.
- **Query params:** `term`, `limit` (both optional)
- **Request body:** none
- **Example request:**

```bash
curl "http://127.0.0.1:5000/forbidden?term=foo&limit=10"
```

### `POST /forbidden`
- **Description:** Publish a new forbidden snapshot/version.
- **Exact request body format:**

```json
{
  "snapshot": {},
  "note": "optional",
  "triggered_by": "optional"
}
```

- **Example request:**

```bash
curl -X POST "http://127.0.0.1:5000/forbidden" \
  -H "Content-Type: application/json" \
  -d "{\"snapshot\":{\"bad_term\":\"replacement\"},\"note\":\"add mapping\"}"
```

### `PATCH /forbidden`
- **Description:** Edit value for an existing forbidden key.
- **Exact request body format:**

```json
{
  "entry": {
    "key": "existing_key",
    "value": "new_value"
  },
  "note": "optional"
}
```

Accepted aliases:
- key: `key` / `input_key` / `term`
- value: `value` / `new_value` / `output` / `replacement`

- **Example response:**

```json
{
  "ok": true,
  "message": "existing_key has been edited",
  "version_number": 31,
  "versions": {}
}
```

### `DELETE /forbidden`
- **Description:** Delete an existing forbidden key.
- **Exact request body format:**

```json
{
  "entry": {
    "key": "existing_key"
  },
  "note": "optional"
}
```

- **Example response:**

```json
{
  "ok": true,
  "message": "existing_key has been deleted",
  "version_number": 32,
  "versions": {}
}
```

---

## Preferred

### `GET /preferred`
- **Description:** Search preferred mappings.
- **Query params:** `term`, `limit` (optional)
- **Request body:** none

### `POST /preferred`
- **Description:** Publish a new preferred snapshot/version.
- **Exact request body format:**

```json
{
  "snapshot": {},
  "note": "optional",
  "triggered_by": "optional"
}
```

### `PATCH /preferred`
- **Description:** Edit value for an existing preferred key.
- **Exact request body format:**

```json
{
  "entry": {
    "key": "existing_key",
    "value": "new_value"
  },
  "note": "optional"
}
```

Accepted aliases:
- key: `key` / `input_key` / `term`
- value: `value` / `new_value` / `output` / `replacement`

### `DELETE /preferred`
- **Description:** Delete an existing preferred key.
- **Exact request body format:**

```json
{
  "entry": {
    "key": "existing_key"
  },
  "note": "optional"
}
```

---

## Schemes

### `GET /schemes`
- **Description:** Search scheme mappings.
- **Query params:** `term`, `limit` (optional)
- **Request body:** none

### `POST /schemes`
- **Description:** Publish a new schemes snapshot/version.
- **Exact request body format:**

```json
{
  "snapshot": {},
  "note": "optional",
  "triggered_by": "optional"
}
```

### `PATCH /schemes`
- **Description:** Edit value for an existing schemes key.
- **Exact request body format:**

```json
{
  "entry": {
    "key": "existing_key",
    "value": "new_value"
  },
  "note": "optional"
}
```

Accepted aliases:
- key: `key` / `input_key` / `term`
- value: `value` / `new_value` / `output` / `replacement`

### `DELETE /schemes`
- **Description:** Delete an existing schemes key.
- **Exact request body format:**

```json
{
  "entry": {
    "key": "existing_key"
  },
  "note": "optional"
}
```

---

## Config Management (reload, rollback, versions)

### `GET /configs`
- **Description:** Return cached configs and version map.
- **Query params:**
  - `format=flat` (optional): returns only flat configs without wrapper
- **Request body:** none
- **Example request:**

```bash
curl "http://127.0.0.1:5000/configs"
```

### `POST /configs/reload`
- **Description:** Reload all config caches from latest DB versions.
- **Request body:** none
- **Example request:**

```bash
curl -X POST "http://127.0.0.1:5000/configs/reload"
```

### `POST /configs/rollback`
- **Description:** Roll back one config type by copying snapshot of requested version into a new latest version row.
- **Exact request body format:**

```json
{
  "config_type": "glossary",
  "version": 8,
  "note": "optional"
}
```

Allowed `config_type` values:
- `glossary`
- `ambiguity`
- `en-gujarati_aliases`
- `english_aliases`
- `forbidden`
- `preferred`
- `schemes`

- **Example request:**

```bash
curl -X POST "http://127.0.0.1:5000/configs/rollback" \
  -H "Content-Type: application/json" \
  -d "{\"config_type\":\"glossary\",\"version\":8}"
```

- **Example response:**

```json
{
  "ok": true,
  "rolled_back_to": 8,
  "new_version": 15,
  "config_type": "glossary_terms",
  "versions": {}
}
```

### `GET /configs/versions`
- **Description:** Return all versions metadata for one config type.
- **Query params:**
  - `config_type` (required)
- **Example request:**

```bash
curl "http://127.0.0.1:5000/configs/versions?config_type=glossary"
```

- **Example response:**

```json
{
  "config_type": "glossary_terms",
  "versions": [
    {
      "version_number": 15,
      "triggered_by": "api",
      "note": "rollback to version 8"
    }
  ]
}
```

---

## Versioning System

- Every successful write (`POST`, `PATCH`, `PUT`, `DELETE`, rollback) uses `publish_config_version(...)` to create a new immutable row in `config_versions`.
- `version_number` is per `config_type` and increases monotonically.
- Snapshot merge/write behavior:
  - Standard POST writes use snapshot parsing + publish validation.
  - Patch/update/delete flows publish full snapshots with `merge=False`.
- Retention policy:
  - Max 100 versions per config type are retained (older versions are pruned after successful insert).

### Rollback behavior

- Rollback does **not** overwrite existing versions.
- It fetches snapshot by `(config_type, version)` and inserts that snapshot as a **new** version (`force_insert=True`).
- After rollback insert, `load_configs_to_memory(...)` reloads latest snapshots across all config types.

---

## Additional Notes

```text

reload manually or over time?
for over time->it will reload even if no changes, unnecessary

ambiguous_terms can maybe have an id for each term to be able to delete or put, right now we will have
to create entire snapshot and then use patch to insert it.
```
