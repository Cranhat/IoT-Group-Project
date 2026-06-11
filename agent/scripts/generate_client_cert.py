#!/usr/bin/env python3
"""
Generate a client TLS certificate for a device.

Usage:
  python generate_client_cert.py <device_id>
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from certs import generate_client_cert


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python generate_client_cert.py <device_id>", file=sys.stderr)
        sys.exit(1)

    paths = generate_client_cert(sys.argv[1])
    print(json.dumps(paths, indent=2))


if __name__ == "__main__":
    main()
