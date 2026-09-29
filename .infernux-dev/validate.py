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
runtime_sources = tuple(PACKAGE.joinpath("runtime").rglob("*.py"))
editor_sources = tuple(PACKAGE.joinpath("editor").rglob("*.py"))
if not any("InxComponent" in path.read_text(encoding="utf-8") for path in runtime_sources):
    raise SystemExit("Template runtime has no InxComponent example")
if not any("InxPreload" in path.read_text(encoding="utf-8") for path in runtime_sources):
    raise SystemExit("Template runtime has no Player-safe InxPreload example")
if not any("InxPreload" in path.read_text(encoding="utf-8") for path in editor_sources):
    raise SystemExit("Template editor has no editor-owned InxPreload example")
for path in runtime_sources:
    source = path.read_text(encoding="utf-8")
    if "example_plugin_editor" in source or "Infernux.engine.ui" in source:
        raise SystemExit(f"Runtime source imports Editor code: {path.relative_to(PACKAGE)}")
for english in PACKAGE.joinpath("plugin_pages").glob("*.md"):
    if english.name.endswith(".zh-CN.md"):
        continue
    localized = english.with_name(f"{english.stem}.zh-CN.md")
    if not localized.is_file():
        raise SystemExit(f"Missing zh-CN page: {localized.name}")
    source = english.read_text(encoding="utf-8")
    for required_topic in ("runtime/", "editor/", "plugin_pages/", "add_cleanup", "Export InxPackage"):
        if required_topic not in source:
            raise SystemExit(f"Plugin tutorial is missing {required_topic!r}: {english.name}")
print("Template layout and Python sources are valid.")
