# Copilot instructions for TensionBot

- **Generator** (`backend/`): Python ≥ 3.8 package `mooring_data_generator` (Click CLI, FastAPI receiver, Pydantic). `pip install -e ".[dev]"`, `pytest`, `ruff check .` (config in `pyproject.toml`, line length 88).
- **Dashboard** (`dashboard/`): Node, Express, Socket.io, `standard` ESLint style (no semicolons, single quotes). `npm ci`, `npm test` (Jest + supertest), `npm run lint`.
- `app.js` only calls `server.listen()` when run directly (`require.main === module`), so tests can `require('../app')`. Keep it that way, and keep timers `.unref()`'d.
- **Data is synthetic.** Never add real vessel or port sensor data.
- **When reviewing PRs:** keep the generator's JSON shape in sync with the dashboard's `POST /api/mooring-data` validation.
