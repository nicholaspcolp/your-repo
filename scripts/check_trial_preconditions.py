"""Check trial preconditions before allowing an autonomy trial to start.
Checks:
- PROPOSED/JARVIS/TRIAL_AUTONOMY_MANIFEST.json exists and is valid JSON
- `defection_capture` is true
- operations_root exists (either passed via --ops-root or present in manifest)
- required artifact paths (chats, defections) exist and are writable

Exits nonzero if checks fail.
"""
import argparse
import json
from pathlib import Path
import sys

p = argparse.ArgumentParser()
p.add_argument('--manifest', default='PROPOSED/JARVIS/TRIAL_AUTONOMY_MANIFEST.json')
p.add_argument('--ops-root', default=r'C:\Users\Tensh\JARVISBRAINSURGERY(OPERATIONS GOVERNANCE TRIALS)')
args = p.parse_args()

manifest_path = Path(args.manifest)
if not manifest_path.exists():
    print(f'ERROR: Manifest not found at {manifest_path}')
    sys.exit(2)

try:
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
except Exception as e:
    print(f'ERROR: Failed to parse manifest: {e}')
    sys.exit(2)

errors = []
if not manifest.get('defection_capture', False):
    errors.append('defection_capture is not true in manifest')

ops_root = Path(args.ops_root)
if not ops_root.exists():
    errors.append(f'operations root not found: {ops_root}')

# check artifact paths
ap = manifest.get('artifact_paths', {})
for key, pth in ap.items():
    pthp = Path(pth)
    if not pthp.exists():
        # try to create directories for writeable artifacts
        try:
            pthp.parent.mkdir(parents=True, exist_ok=True)
            if key in ('chats','defections'):
                # ensure file exists or can be created
                if not pthp.exists():
                    pthp.write_text('', encoding='utf-8')
        except Exception as e:
            errors.append(f'artifact path not writable or creatable: {pth} ({e})')

if errors:
    print('PRECONDITION FAILURES:')
    for e in errors:
        print(' -', e)
    sys.exit(3)

print('Preconditions OK')
sys.exit(0)
