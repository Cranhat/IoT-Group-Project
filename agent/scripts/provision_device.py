#!/usr/bin/env python3
"""
Standalone script to provision a peripheral IoT device container.

Usage:
  python provision_device.py [device_name]
  PROVISION_MOCK=true python provision_device.py sensor-01
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from provisioner import provision_device


def main() -> None:
    device_name = sys.argv[1] if len(sys.argv) > 1 else None
    result = provision_device(device_name)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
