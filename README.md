# Infernux Plugin Template

[简体中文](README.zh-CN.md)

This repository separates authoring from distribution. You may use CMake, Cargo, Gradle, npm, or any other tooling at the repository root. Only files placed under `package/` enter the `.inxpkg`; the root README, build configuration, CI, source trees, and temporary output never do.

## Quick start

1. Edit `package/inx_package.json` and choose a globally unique lowercase reference.
2. Put Player-safe files under `package/runtime/`, Editor-only files under `package/editor/`, and ordinary assets under any other lowercase directory in `package/`.
3. Let your outer build place its final `.dll`, `.so`, `.pyd`, `.wasm`, Java resources, shaders, materials, web pages, or other required files into `package/`.
4. Build without installing Infernux:

   ```powershell
   python package.py build dist/example-plugin.inxpkg
   python package.py verify dist/example-plugin.inxpkg
   ```

## Layout

```text
infernux-plugin/
├─ package.py                     standalone standard-library packer
├─ CMakeLists.txt / build.gradle  optional author tooling; never packaged
├─ README.md                      repository documentation; never packaged
├─ package/
│  ├─ inx_package.json            package identity and compatibility
│  ├─ runtime/                    Player and Editor runtime files
│  ├─ editor/                     Editor-only files
│  ├─ plugin_pages/               pages shown by the Plugins panel
│  ├─ requirements.txt            optional fixed-name Python requirements
│  └─ samples/, shaders/, web/    ordinary assets installed under Assets/Plugins
└─ .github/workflows/             repository automation; never packaged
```

The manifest intentionally contains no `requirements` or `dependencies` keys. `requirements.txt`, when present, is found by its fixed filename. The package format treats `.pyd`, `.wasm`, materials, shaders, HTML, and unknown files as bytes; placement determines ownership and Player export policy.

```json
{
  "$schema": "infernux.inxpackage.source",
  "reference": "your-studio/example-plugin",
  "name": "Example Plugin",
  "version": "0.1.0",
  "engine": ">=0.4,<0.5",
  "intro": "A minimal Infernux runtime and editor extension."
}
```

`plugin_pages/` is the only conventional source for Plugins-panel documentation. Root README and license files remain repository content. Push a `v<version>` tag to run the included workflow, which builds the package twice, checks deterministic bytes, and publishes the package plus `infernux-plugin-release.json`.
