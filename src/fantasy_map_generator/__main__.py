"""Allow running the package as a script: python -m fantasy_map_generator"""

import sys

from fantasy_map_generator.cli import main

if __name__ == "__main__":
    sys.exit(main())
