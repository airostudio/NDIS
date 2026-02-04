#!/usr/bin/env python3
"""
Run Velma API Server
Starts the FastAPI application
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from velma.api.app import run_api
from velma.utils import Config

if __name__ == "__main__":
    config = Config()

    host = config.get("api.host", "0.0.0.0")
    port = config.get("api.port", 8000)

    print(f"\n🚀 Starting Velma API Server on {host}:{port}\n")

    run_api(host=host, port=port)
