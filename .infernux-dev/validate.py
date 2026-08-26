from __future__ import annotations

import json
import py_compile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / "InxPackage.json").read_text(encoding="utf-8"))
required = {"reference", "name", "version", "engine", "dependencies", "requirements"}
missing = sorted(required - manifest.keys())
if missing:
    raise SystemExit("Missing manifest fields: " + ", ".join(missing))
if not isinstance(manifest["dependencies"], list):
    raise SystemExit("dependencies must be a list")
for path in ("README.md", "README.zh-CN.md", "LICENSE", "Runtime", "Editor"):
    if not (ROOT / path).exists():
        raise SystemExit(f"Missing template entry: {path}")
for path in sorted((*ROOT.joinpath("Runtime").rglob("*.py"), *ROOT.joinpath("Editor").rglob("*.py"))):
    py_compile.compile(str(path), doraise=True)
for english in ROOT.joinpath("InxPluginPages").glob("*.md"):
    if english.name.endswith(".zh-CN.md"):
        continue
    localized = english.with_name(f"{english.stem}.zh-CN.md")
    if not localized.is_file():
        raise SystemExit(f"Missing zh-CN page: {localized.name}")
print("Template layout and Python sources are valid.")
