# TensionBot

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
  public/         Static assets
  views/          Templates
  app.js          Server entry
demo.sh           End-to-end demo script
```

## Status

Hackathon project. Repo was renamed from `bhp-uwa`. MIT license declared in `pyproject.toml` and README; no top-level LICENSE file.
