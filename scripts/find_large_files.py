from pathlib import Path
import sys

root = Path(sys.argv[1]) if len(sys.argv)>1 else Path(r"C:\Users\Tensh\Downloads\AI Studio")
minb = int(sys.argv[2]) if len(sys.argv)>2 else 5_000_000_000

print(f"Scanning {root} for files >= {minb} bytes...")
found=0
for p in root.rglob('*'):
    try:
        if p.is_file():
            s=p.stat().st_size
            if s>=minb:
                print(s, p)
                found+=1
    except Exception:
        continue
print('Found',found,'candidates')
