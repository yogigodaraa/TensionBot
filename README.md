# TensionBot

[![CI](https://github.com/yogigodaraa/TensionBot/actions/workflows/ci.yml/badge.svg)](https://github.com/yogigodaraa/TensionBot/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Fake-mooring-data generator + real-time visualization dashboard. Built as a hackathon companion project for the BHP/UWA work.

## What it does

Two-part system for demoing mooring sensor analytics when real data isn't available:

- **Generator** — Python CLI that produces synthetic oceanographic readings (temperature, salinity, pressure, wave height, current speed) with configurable drift and ranges, sends them over HTTP with retry + exponential backoff.
- **Dashboard** — Node.js / Express server that receives generated data, stores the last 1000 records in memory, and streams updates to the browser over Socket.io WebSockets.

## Tech stack

**Backend** (`backend/`) — Python 3.8+
- FastAPI, Uvicorn, Click, Requests
- Ruff (lint), Tox (test matrix)

**Dashboard** (`dashboard/`) — Node.js
- Express, Socket.io, Axios, Helmet, compression

## Getting started

**Generator**

```bash
cd backend
pip install -e .
mooring-data-generator --help      # send synthetic data
mooring-data-receiver --help       # test HTTP receiver
```

**Dashboard**

```bash
cd dashboard
npm install
npm start                           # http://localhost:3000
```

Demo the whole thing:

```bash
./demo.sh
```

## Project structure

```
backend/          Python data generator + pyproject.toml
dashboard/        Express + Socket.io dashboard
  views/          dashboard.html
  test/           Jest + supertest API tests
  app.js          Server entry
demo.sh           End-to-end demo script
```

## Tests

```bash
cd backend && pip install -e ".[dev]" && pytest && ruff check .
cd dashboard && npm ci && npm test && npm run lint
```

## Credits

The generator package in `backend/` (`mooring-data-generator`) declares *BHP UWA* as its author
and `github.com/bhp-uwa/mooring-data-generator` as its homepage in `pyproject.toml`. It appears to
be the hackathon-provided generator, adapted here.
<!-- TODO(yogi): confirm the origin and licence of backend/ and adjust this credit if needed -->

## Related projects

- [bhp](https://github.com/yogigodaraa/bhp): Mooring Portal (Next.js) with a four-pillar data-quality pipeline
- [MIB](https://github.com/yogigodaraa/MIB): FastAPI tension-forecasting backend with a crew dashboard

## Status

Hackathon project (prototype). MIT licensed; see [LICENSE](LICENSE).
