from pathlib import Path
import sys

roots = sys.argv[1:2] or [r"C:\\JARVISBRAINSURGERY", r"C:\\"]
min_size = int(sys.argv[2]) if len(sys.argv) > 2 else 1_000_000_000  # default 1 GB

for root in roots:
    p = Path(root)
    if not p.exists():
        print(f"Root not found: {root}")
        continue
    print(f"Searching {root} for files with 'patch' in name >= {min_size} bytes...")
    found = 0
    try:
        for f in p.rglob("*patch*"):
            try:
                s = f.stat().st_size
            except Exception:
                continue
            if s >= min_size:
                print(f"{f} {s}")
                found += 1
    except Exception as e:
        print(f"Error while searching {root}: {e}")
    print(f"Found {found} matches in {root}")
