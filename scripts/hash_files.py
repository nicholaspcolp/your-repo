"""Hash files listed in a CSV. Append results to output (resume-safe).
Input CSV must have a header with FILEPATH and optional SIZE_BYTES.
Writes rows: FILEPATH,SIZE_BYTES,SHA256,elapsed_seconds

Usage:
  python scripts/hash_files.py --input pilot_files.csv --out GOV/reports/efmc_v5.3_sha256_pilot.csv --workers 1
"""
import argparse
import csv
import hashlib
import time
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--input', required=True)
p.add_argument('--out', required=True)
p.add_argument('--workers', type=int, default=1)
args = p.parse_args()

input_csv = Path(args.input)
out_csv = Path(args.out)

# Read already-hashed set to support resume
existing = set()
if out_csv.exists():
    with open(out_csv, newline='', encoding='utf-8') as outf:
        r = csv.DictReader(outf)
        for row in r:
            existing.add(row.get('FILEPATH'))


def sha256_file(path, chunk_size=8*1024*1024):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            b = f.read(chunk_size)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

with open(input_csv, newline='', encoding='utf-8') as inf, open(out_csv, 'a', newline='', encoding='utf-8') as outf:
    reader = csv.DictReader(inf)
    fieldnames = ['FILEPATH','SIZE_BYTES','SHA256','elapsed_seconds']
    writer = csv.DictWriter(outf, fieldnames=fieldnames)
    if outf.tell() == 0:
        writer.writeheader()

    for r in reader:
        fp = r.get('FILEPATH')
        if not fp or fp in existing:
            continue
        pth = Path(fp)
        if not pth.exists():
            print(f"MISSING: {fp}")
            continue
        start = time.time()
        try:
            sh = sha256_file(pth)
            elapsed = time.time()-start
            size = r.get('SIZE_BYTES') or pth.stat().st_size
            writer.writerow({'FILEPATH':fp,'SIZE_BYTES':size,'SHA256':sh,'elapsed_seconds':f"{elapsed:.2f}"})
            outf.flush()
            print(f"OK: {fp} -> {sh} ({elapsed:.2f}s)")
        except Exception as e:
            print(f"ERROR hashing {fp}: {e}")
