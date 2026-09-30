# Infernux Plugin Template

The official starter repository for creating plugins for [Infernux](https://github.com/ChenlizheMe/Infernux), an open-source C++17/Vulkan game engine with a Python authoring layer. Use this template for Python extensions, native libraries, Java tools, WebAssembly modules, shaders, materials, web content, or any other files an Infernux project needs.

[简体中文](README.zh-CN.md) · [Infernux Engine](https://github.com/ChenlizheMe/Infernux) · [Plugin Documentation](https://github.com/ChenlizheMe/Infernux/tree/master/docs) · [Official Plugins](https://github.com/ChenlizheMe/Infernux#plugins)

```mermaid
flowchart LR
    A[Your source and build tools] --> B[package/]
    B --> C[package.py]
    C --> D[Installable .inxpkg]
    D --> E[Infernux Editor and Player]
```

## Create a plugin

1. Select **Use this template** on GitHub and clone your new repository.
2. Edit `package/inx_package.json`: choose a globally unique lowercase `reference`, a human-readable name, a version, and the supported Infernux range.
3. Put runtime files in `package/runtime/`, Editor-only code in `package/editor/`, and plugin documentation in `package/plugin_pages/`. Other assets may use directories that fit your plugin.
4. Build and verify the installable package:

   ```powershell
   python package.py build dist/example-plugin.inxpkg
   python package.py verify dist/example-plugin.inxpkg
   ```

`package.py` uses only the Python standard library, so packaging does not require an Infernux installation. Your repository may use CMake, Gradle, Cargo, npm, or another build system; copy only the files users need at runtime into `package/`.

Inside an Infernux project, the selected folder is already the package root: select it in Project/File Manager, right click, and choose **Export InxPackage...**. The installed Plugins page contains the full tutorial, including lifecycle ownership, hot reload, Player component registration, large imports, and an Editor-only Flask tool window.

## Package layout

```text
your-plugin/
├─ package.py                  standalone InxPackage builder
├─ README.md                   GitHub project documentation
├─ package/
│  ├─ inx_package.json         identity, version, engine compatibility
│  ├─ runtime/                 available to Editor and exported Players
│  ├─ editor/                  Editor-only code, tools, and translations.json
│  ├─ plugin_pages/            documentation shown in the Plugins window
│  ├─ requirements.txt         optional Python requirements
│  └─ shaders/, web/, samples/ optional plugin assets
└─ .github/workflows/          validation and release automation
```

Only `package/` enters the `.inxpkg`. Source trees, build files, repository documentation, tests, and temporary output stay outside. The packer preserves arbitrary file types; directory placement determines how Infernux installs and exports them.

## Automated releases

Every pull request and push to `main` validates the manifest and verifies deterministic package output. Set the manifest version, then push the matching `v<version>` tag. GitHub Actions publishes the `.inxpkg` and `infernux-plugin-release.json` to a GitHub Release, ready for the Infernux Plugins window.

For a complete production example, see the [Windows](https://github.com/ChenlizheMe/infernux_windows), [Linux](https://github.com/ChenlizheMe/infernux_linux), [Web](https://github.com/ChenlizheMe/infernux_web), [Android](https://github.com/ChenlizheMe/infernux_android), and [MCP](https://github.com/ChenlizheMe/infernux_mcp) plugins.

`plugin_pages/` is the only conventional source for Plugins-panel documentation. Runtime and Editor preloads are deliberately separate: runtime components and preloads are cooked into Players, while Editor panels and tools are excluded. Register threads, servers, watches, and callbacks with `PreloadContext.add_cleanup()` as soon as they are created. Infernux removes lifecycle-owned contributions during hot reload, disable, uninstall, and project shutdown.

The template includes `editor/translations.json`. Infernux loads this package-owned catalog before Editor preloads, applies it to panel titles and every declared menu level, and removes it on disable, uninstall, or hot reload.

## License

[MIT](LICENSE).
