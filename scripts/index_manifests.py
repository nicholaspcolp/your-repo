"""Index manifest source files and produce WORK/JARVIS_BRAIN_OPERATIONS/manifest_sources/index.json
Scans common manifest locations (GOV/*.csv) and records path, size, mtime, and sha256 for provenance.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
from datetime import datetime

p = argparse.ArgumentParser()
p.add_argument('--root', default='GOV')
p.add_argument('--out', default='WORK/JARVIS_BRAIN_OPERATIONS/manifest_sources/index.json')
args = p.parse_args()

root = Path(args.root)
out = Path(args.out)
out.parent.mkdir(parents=True, exist_ok=True)

manifests = list(root.glob('**/*MANIFEST*.csv')) + list(root.glob('**/*manifest*.csv'))
entries = []
for m in sorted(set(manifests)):
    try:
        st = m.stat()
        size = st.st_size
        mtime = datetime.utcfromtimestamp(st.st_mtime).isoformat()+'Z'
        # compute small sha for provenance
        h = hashlib.sha256()
        with open(m, 'rb') as f:
            while True:
                b = f.read(8*1024*1024)
                if not b:
                    break
                h.update(b)
        sha = h.hexdigest()
        entries.append({'path': str(m), 'size_bytes': size, 'modified': mtime, 'sha256': sha})
    except Exception:
        continue

index = {'generated_at': datetime.utcnow().isoformat()+'Z', 'manifests': entries}
out.write_text(json.dumps(index, indent=2), encoding='utf-8')
print('Wrote manifest index to', out)
