"""Mooring data receiver for testing data transmission."""

import argparse
import json
import signal
from datetime import datetime
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse


class DataReceiver:
    """HTTP server to receive and display mooring data."""

    def __init__(self, format_output: bool = False):
        self.app = FastAPI(
            title="Mooring Data Receiver",
            description="Test server to receive and display mooring data",
            version="1.0.0"
        )
        self.format_output = format_output
        self.received_count = 0
        self.setup_routes()
        self.setup_signal_handlers()

    def setup_signal_handlers(self):
        """Setup graceful shutdown handlers."""
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

    def _handle_shutdown(self, signum, frame):
        """Handle shutdown signals."""
        print(
            "\n🛑 Received shutdown signal. "
            f"Total requests received: {self.received_count}"
        )

    def setup_routes(self):
        """Setup API routes."""

        @self.app.get("/")
        async def root():
            """Root endpoint with server info."""
            return {
                "service": "Mooring Data Receiver",
                "status": "running",
                "received_count": self.received_count,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }

        @self.app.post("/api/mooring-data")
        async def receive_mooring_data(request: Request):
            """Receive mooring data via POST."""
            try:
                data = await request.json()
                self._log_request("POST", "/api/mooring-data", data)
                return JSONResponse(
                    status_code=200,
                    content={
                        "status": "success",
                        "message": "Mooring data received",
                        "timestamp": datetime.utcnow().isoformat() + "Z"
                    }
                )
            except json.JSONDecodeError as e:
                self._log_error("Invalid JSON in request body")
                raise HTTPException(
                    status_code=400, detail="Invalid JSON format"
                ) from e
            except Exception as e:
                self._log_error(f"Error processing request: {str(e)}")
                raise HTTPException(
                    status_code=500, detail="Internal server error"
                ) from e

        @self.app.post("/{path:path}")
        async def catch_all_post(path: str, request: Request):
            """Catch all other POST requests."""
            try:
                data = await request.json()
                self._log_request("POST", f"/{path}", data)
            except ValueError:  # body isn't JSON; log it as text
                body = await request.body()
                text = body.decode("utf-8", errors="ignore")
                self._log_request("POST", f"/{path}", text)

            return JSONResponse(
                status_code=200,
                content={
                    "status": "received",
                    "path": f"/{path}",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            )

        @self.app.get("/{path:path}")
        async def catch_all_get(path: str, request: Request):
            """Catch all GET requests."""
            query_params = dict(request.query_params)
            self._log_request("GET", f"/{path}", query_params if query_params else None)

            return JSONResponse(
                status_code=200,
                content={
                    "status": "received",
                    "method": "GET",
                    "path": f"/{path}",
                    "query_params": query_params,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            )

    def _log_request(self, method: str, path: str, data: Any = None):
        """Log incoming request."""
        self.received_count += 1
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        print(f"\n📨 Request #{self.received_count} - {timestamp}")
        print(f"   Method: {method}")
        print(f"   Path: {path}")

        if data is not None:
            print("   Body:")
            if self.format_output and isinstance(data, (dict, list)):
                formatted_data = json.dumps(data, indent=2)
                # Indent each line for better readability
                for line in formatted_data.split('\n'):
                    print(f"      {line}")
            else:
                print(f"      {data}")

        print("   " + "─" * 50)

    def _log_error(self, message: str):
        """Log error message."""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        print(f"\n❌ Error - {timestamp}")
        print(f"   {message}")
        print("   " + "─" * 50)


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Receive and display HTTP traffic for testing mooring data transmission"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run on default host and port
  mooring-data-receiver

  # Run on specific host and port
  mooring-data-receiver --host 127.0.0.1 --port 5000

  # Enable formatted output
  mooring-data-receiver --format

  # Quiet mode (less verbose)
  mooring-data-receiver --quiet
        """
    )

    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Host to bind to (default: 0.0.0.0)'
    )

    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Port to listen on (default: 8000)'
    )

    parser.add_argument(
        '--format',
        action='store_true',
        help='Format JSON request bodies for better readability'
    )

    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Reduce verbosity (don\'t show startup messages)'
    )

    parser.add_argument(
        '--reload',
        action='store_true',
        help='Enable auto-reload for development'
    )

    return parser


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Create data receiver
    receiver = DataReceiver(format_output=args.format)

    if not args.quiet:
        print("🚀 Starting Mooring Data Receiver")
        print(f"🌐 Listening on: http://{args.host}:{args.port}")
        print(f"📝 Formatted output: {'Enabled' if args.format else 'Disabled'}")
        print("\n📡 Waiting for HTTP requests... (Press Ctrl+C to stop)\n")
        print("Endpoints:")
        print("   GET  /                    - Server info")
        print("   GET  /health             - Health check")
        print("   POST /api/mooring-data   - Mooring data endpoint")
        print("   *    /*                  - Catch-all for any other requests")
        print("\n" + "=" * 60)

    try:
        uvicorn.run(
            receiver.app,
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level="warning" if args.quiet else "info",
            access_log=False  # We handle our own request logging
        )
    except KeyboardInterrupt:
        if not args.quiet:
            print(f"\n👋 Goodbye! Received {receiver.received_count} requests total.")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
