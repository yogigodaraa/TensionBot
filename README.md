# Mooring Data Visualization System

A comprehensive system for generating and visualizing fake mooring data for hackathon use. This project consists of two main components:

- **Backend (Python)**: Data generator and receiver for mooring sensor data
- **Dashboard (Node.js)**: Real-time visualization dashboard for monitoring mooring data

## Architecture

```
bhp-uwa/
├── backend/           # Python mooring data generator and receiver
│   ├── src/
│   └── pyproject.toml
├── dashboard/         # Node.js real-time dashboard
│   ├── public/
│   ├── views/
│   ├── app.js
│   └── package.json
└── README.md
```

## Quick Start

### Backend Setup (Python)

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Install with UV (recommended):
   ```bash
   uv tool install -U mooring-data-generator
   ```

   Or with pip:
   ```bash
   pip install -U mooring-data-generator
   ```

### Dashboard Setup (Node.js)

1. Navigate to dashboard directory:
   ```bash
   cd dashboard
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the dashboard:
   ```bash
   npm start
   ```

## Usage

### Generating Mooring Data

#### Send data via HTTP POST:
```bash
mooring-data-generator http://127.0.0.1:8000/api/mooring-data
```

#### Save data to file:
```bash
mooring-data-generator --file output.json
```

#### Get OpenAPI specification:
```bash
mooring-data-generator --openapi > openapi.json
```

### Testing Data Reception

Start the data receiver to test that data is being sent:
```bash
mooring-data-receiver
```

With custom host and port:
```bash
mooring-data-receiver --host 127.0.0.1 --port 5000
```

### Dashboard

Access the real-time dashboard at:
```
http://localhost:3000
```

The dashboard will display:
- Real-time mooring sensor data
- Historical data charts
- System status and alerts
- Data flow monitoring

## Development

### Backend Development

```bash
cd backend
uv sync --all-groups
uv run ruff format
uv run ruff check
uv run tox
```

### Dashboard Development

```bash
cd dashboard
npm run dev    # Start with nodemon for auto-reload
npm test       # Run tests
npm run lint   # Check code style
```

## API Endpoints

### Backend (Python)
- `POST /api/mooring-data` - Receive mooring data
- `GET /api/openapi` - Get OpenAPI specification

### Dashboard (Node.js)
- `GET /` - Dashboard home page
- `GET /api/status` - System status
- WebSocket connection for real-time data updates

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.