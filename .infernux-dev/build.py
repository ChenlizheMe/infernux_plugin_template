from pathlib import Path

from Infernux.plugins import InxPackage


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "dist" / "example-plugin.inxpkg"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
preview = InxPackage.export_source(str(ROOT), str(OUTPUT))
print(f"Built {OUTPUT} ({len(preview.file_records)} files)")
