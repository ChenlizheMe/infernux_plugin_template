from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "package"
manifest = json.loads((PACKAGE / "inx_package.json").read_text(encoding="utf-8"))
required = {"reference", "name", "version", "engine"}
missing = sorted(required - manifest.keys())
if missing:
    raise SystemExit("Missing manifest fields: " + ", ".join(missing))
unsupported = sorted({"dependencies", "requirements"} & manifest.keys())
if unsupported:
    raise SystemExit("Unsupported manifest fields: " + ", ".join(unsupported))
for path in ("README.md", "README.zh-CN.md", "LICENSE", "package", "package.py"):
    if not (ROOT / path).exists():
        raise SystemExit(f"Missing template entry: {path}")
for path in sorted((*PACKAGE.joinpath("runtime").rglob("*.py"), *PACKAGE.joinpath("editor").rglob("*.py"))):
    compile(path.read_text(encoding="utf-8"), str(path), "exec")
for english in PACKAGE.joinpath("plugin_pages").glob("*.md"):
    if english.name.endswith(".zh-CN.md"):
        continue
    localized = english.with_name(f"{english.stem}.zh-CN.md")
    if not localized.is_file():
        raise SystemExit(f"Missing zh-CN page: {localized.name}")
print("Template layout and Python sources are valid.")
