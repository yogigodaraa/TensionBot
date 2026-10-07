"""Command line interface for mooring data generator."""

import argparse
import json
import signal
import sys
import time
from pathlib import Path
from typing import Optional, TextIO

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .generator import MooringDataGenerator
from .openapi import generate_openapi_spec


class MooringDataSender:
    """Handle sending mooring data via HTTP."""

    def __init__(self, url: str, timeout: int = 30):
        self.url = url
        self.session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        self.timeout = timeout
        self.success_count = 0
        self.error_count = 0

    def send_data(self, data: dict) -> bool:
        """Send data via HTTP POST."""
        try:
            response = self.session.post(
                self.url,
                json=data,
                timeout=self.timeout,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'mooring-data-generator/1.0'
                }
            )
            response.raise_for_status()
            self.success_count += 1
            print(f"✓ Data sent successfully (#{self.success_count})")
            return True
        except requests.exceptions.RequestException as e:
            self.error_count += 1
            print(f"✗ Error sending data (#{self.error_count}): {e}")
            return False

    def get_stats(self) -> dict:
        """Get sending statistics."""
        total = self.success_count + self.error_count
        success_rate = (self.success_count / total * 100) if total > 0 else 0
        return {
            "total_attempts": total,
            "successful": self.success_count,
            "failed": self.error_count,
            "success_rate": round(success_rate, 2)
        }


class MooringDataFileWriter:
    """Handle writing mooring data to file."""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.file_handle: Optional[TextIO] = None
        self.record_count = 0
        self.is_first_record = True

    def __enter__(self):
        self.file_handle = open(self.file_path, 'w')
        self.file_handle.write('[\n')  # Start JSON array
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file_handle:
            self.file_handle.write('\n]')  # End JSON array
            self.file_handle.close()

    def write_data(self, data: dict) -> bool:
        """Write data to file."""
        try:
            if not self.is_first_record:
                self.file_handle.write(',\n')
            else:
                self.is_first_record = False

            json.dump(data, self.file_handle, indent=2)
            self.file_handle.flush()
            self.record_count += 1
            print(f"✓ Data written to file (record #{self.record_count})")
            return True
        except Exception as e:
            print(f"✗ Error writing to file: {e}")
            return False


class GracefulKiller:
    """Handle graceful shutdown on Ctrl+C."""

    def __init__(self):
        self.kill_now = False
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

    def _handle_signal(self, signum, frame):
        print("\n🛑 Received interrupt signal. Shutting down gracefully...")
        self.kill_now = True


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        description="Generate and send fake mooring data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Send data to HTTP endpoint
  mooring-data-generator http://127.0.0.1:8000/api/mooring-data

  # Save data to file
  mooring-data-generator --file output.json

  # Generate OpenAPI specification
  mooring-data-generator --openapi

  # Custom interval and mooring ID
  mooring-data-generator http://localhost:3000/data --interval 10 --mooring-id MOOR_002
        """
    )

    # Main argument - URL or options
    parser.add_argument(
        'url',
        nargs='?',
        help='HTTP endpoint URL to send data to'
    )

    # Output options
    parser.add_argument(
        '--file',
        help='Save data to JSON file instead of sending via HTTP'
    )

    parser.add_argument(
        '--openapi',
        action='store_true',
        help='Generate OpenAPI 3.0 specification and exit'
    )

    # Configuration options
    parser.add_argument(
        '--interval',
        type=float,
        default=5.0,
        help='Interval between data generation in seconds (default: 5.0)'
    )

    parser.add_argument(
        '--mooring-id',
        default='MOOR_001',
        help='Mooring station identifier (default: MOOR_001)'
    )

    parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='HTTP request timeout in seconds (default: 30)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    return parser


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Handle OpenAPI specification generation
    if args.openapi:
        spec = generate_openapi_spec()
        print(json.dumps(spec, indent=2))
        return

    # Validate arguments
    if not args.url and not args.file:
        parser.error("Either URL or --file option must be provided")

    if args.url and args.file:
        parser.error("Cannot use both URL and --file options simultaneously")

    if args.interval <= 0:
        parser.error("Interval must be greater than 0")

    # Initialize components
    generator = MooringDataGenerator(mooring_id=args.mooring_id)
    killer = GracefulKiller()

    print("🚀 Starting Mooring Data Generator")
    print(f"📍 Mooring ID: {args.mooring_id}")
    print(f"⏱️  Interval: {args.interval}s")

    if args.url:
        print(f"🌐 Sending to: {args.url}")
        sender = MooringDataSender(args.url, timeout=args.timeout)
        output_handler = sender
    else:
        print(f"📁 Writing to: {args.file}")
        output_handler = MooringDataFileWriter(args.file)

    print("\n🔄 Generating data... (Press Ctrl+C to stop)\n")

    try:
        # Context manager for file writing
        if args.file:
            with output_handler as writer:
                _run_generation_loop(generator, writer, killer, args)
        else:
            _run_generation_loop(generator, output_handler, killer, args)

    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

    finally:
        # Print final statistics
        if args.url:
            stats = output_handler.get_stats()
            print("\n📊 Final Statistics:")
            print(f"   Total attempts: {stats['total_attempts']}")
            print(f"   Successful: {stats['successful']}")
            print(f"   Failed: {stats['failed']}")
            print(f"   Success rate: {stats['success_rate']}%")
        elif hasattr(output_handler, 'record_count'):
            print(f"\n📊 Total records written: {output_handler.record_count}")

        print("👋 Goodbye!")


def _run_generation_loop(generator, output_handler, killer, args):
    """Run the main data generation loop."""
    while not killer.kill_now:
        try:
            # Generate data
            data = generator.generate_dict()

            if args.verbose:
                print(f"Generated data for {data['mooring_id']} at {data['timestamp']}")

            # Send/write data
            if args.file:
                success = output_handler.write_data(data)
            else:
                success = output_handler.send_data(data)

            if not success and args.url:
                print("⚠️  Continuing despite send failure...")

            # Wait for next iteration
            if not killer.kill_now:
                time.sleep(args.interval)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            if not killer.kill_now:
                time.sleep(1)  # Brief pause before retrying


if __name__ == '__main__':
    main()
