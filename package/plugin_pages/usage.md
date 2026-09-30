# Plugin authoring guide

This page ships inside the plugin and appears in Infernux's **Plugins** window. Keep it current with the package that users actually install.

## The package boundary

Only the contents of the repository's `package/` directory enter the `.inxpkg`. Repository tooling, CI files, intermediate output, and source material outside that directory stay outside the release.

```text
package/
├─ inx_package.json
├─ runtime/
│  └─ your_studio/example_plugin/
│     ├─ component.py
│     └─ preload.py
├─ editor/
│  ├─ translations.json
│  └─ your_studio/example_plugin_editor/
│     ├─ panel.py
│     └─ preload.py
├─ plugin_pages/
│  ├─ usage.md
│  ├─ usage.zh-CN.md
│  └─ media/
├─ requirements.txt
└─ samples/
```

The reserved directories have distinct jobs:

- `runtime/` contains code and raw resources needed by both the Editor and a built Player. Gameplay components belong here. Player builds compile these Python sources and publish their component, serializable type, and GUID records automatically.
- `editor/` contains panels, commands, import tools, and other authoring code. It loads only in the Editor and is excluded from Player builds.
- `plugin_pages/` contains markdown, text, and referenced images shown in the Plugins window. It is documentation and never executes.

Other package root directories are ordinary assets. Infernux imports them under `Assets/Plugins` and sends them through the normal asset and Player cook pipeline.

## Components and module identity

`ExampleRotator` is a normal `InxComponent`. Add it to a GameObject and adjust **Speed** in the Inspector. Keep runtime code under a real Python package and use explicit package imports. Do not edit `sys.path`, synthesize module names, or replace `sys.modules["infernux"]`.

Every source file receives a stable asset GUID when packaged. During Player build, Infernux freezes project and plugin runtime scripts into one component/type registry and one path-to-GUID catalog. A component serialized by the Editor therefore resolves to the same type in Windows, Linux, Web, and Android Players. Authors do not maintain a second Player registry.

Keep committed `.meta` files when an already released asset must retain its GUID. The standalone packer creates deterministic GUID metadata for files without one.

## Preload lifecycle

Subclass `InxPreload` when work must happen before scene scripts run. Put runtime preloads under `runtime/` and Editor preloads under `editor/`; do not make a runtime preload import Editor code.

`preload(context)` is the acquisition phase. `unload()` is the plugin-owned release phase. Register cleanup immediately after acquiring resources that are easy to forget:

```python
class ServicePreload(inx.InxPreload):
    def preload(self, context: inx.PreloadContext) -> None:
        server = start_server()
        context.add_cleanup(server.stop)

    def unload(self) -> None:
        pass
```

Cleanup callbacks run once in reverse order after `unload()`. They also run if a later statement in `preload()` fails. Use them for HTTP servers, worker threads, file watches, event subscriptions, and callbacks. Make each cleanup complete and bounded: stop accepting work, signal shutdown, join its thread, then release its socket or handle.

When a saved candidate has invalid Python syntax, Infernux keeps the last working lifecycle active. A valid save is loaded as one replacement transaction. Editor panels, commands, and shortcuts registered during an Editor preload are owned by that transaction and are removed automatically before replacement.

### Large Python packages

`requirements.txt` declares Python distributions required by the plugin. Importing a large module such as `torch` in a runtime preload is appropriate when gameplay needs it: the cost is paid once before scene scripts rather than during every Play transition or the first gameplay event.

Native extension modules may hold process-global state. Infernux detects newly loaded native Python modules and marks the lifecycle as requiring an Editor restart for replacement or uninstall. Call `context.require_restart(reason)` yourself only when the plugin creates other irreversible process state that cannot be fully released. Pure Python state and a correctly stopped Flask server do not require it.

## Independent Flask tool window

A Flask based authoring tool belongs under `editor/`. Start it from an Editor `InxPreload`, bind explicitly to loopback, let the operating system choose an available port, and register a complete shutdown with `context.add_cleanup`. Open the returned local URL through your panel or the platform browser command. Never start Flask at module import time and never enable the development reloader, because it creates an unowned child process.

```python
from threading import Thread
from werkzeug.serving import make_server

class ToolWindowPreload(inx.InxPreload):
    def preload(self, context: inx.PreloadContext) -> None:
        app = create_app()
        server = make_server("127.0.0.1", 0, app, threaded=True)
        thread = Thread(target=server.serve_forever, name="example-tool", daemon=True)
        thread.start()

        def stop() -> None:
            server.shutdown()
            thread.join(timeout=5.0)
            if thread.is_alive():
                raise RuntimeError("Example tool server did not stop")
            server.server_close()

        context.add_cleanup(stop)
        self.url = f"http://127.0.0.1:{server.server_port}/"
```

Add exact Flask and Werkzeug versions to `requirements.txt` when using this pattern. Keep the browser UI and server in `editor/` unless the Player intentionally exposes that service.

## Editor panel and translations

The example Editor preload imports `panel.py` inside its lifecycle transaction. Its five-level location is **Extensions → Example Plugin → Tools → Diagnostics → Live → Example Plugin**. `menu_path` supplies the literal label for each level. The parallel `menu_path_keys` tuple supplies an optional translation key for each level; use an empty string when one level must remain literal. One through five levels, and deeper paths, use the same contract.

Put the package catalog at the fixed path `editor/translations.json`. Infernux validates and publishes it before importing the package's Editor preload, then removes it with the package lifecycle. The file must use the `infernux.editor_translations` schema, contain every Editor locale, and declare the same namespaced key set in every locale. Plugin keys cannot replace engine keys or keys owned by another plugin. The first menu level uses the engine's `menu.extensions` key; every plugin-owned level uses the package namespace. The catalog remains Editor-only and never enters a Player.

## Build from File Manager

For a plugin authored inside a project:

1. Create one folder containing `runtime`, `editor`, `plugin_pages`, optional ordinary assets, and optionally `inx_package.json`.
2. Select that folder in the Project/File Manager.
3. Right click and choose **Export InxPackage...**.
4. Choose the destination `.inxpkg`.
5. Double click the produced package in Project view to inspect its file roles and GUIDs before import.

The selected folder is the package root. Do not add another `package/` wrapper inside it. Multi-selection preserves paths relative to the common parent.

For this Git repository, `package/` is already the package root. Build and verify it from any directory with:

```text
python package.py build dist/example-plugin.inxpkg
python package.py verify dist/example-plugin.inxpkg
```

Two builds from identical inputs must produce identical bytes. The included GitHub workflow validates Python sources, rebuilds twice, compares both archives, and publishes the `.inxpkg` plus its release manifest for a `v<version>` tag.

## Install, update, and remove

Open the `.inxpkg` from Project view or add its local path or GitHub repository in the Plugins window. Review the proposed files, then install. Runtime scripts refresh through the plugin lifecycle; an irreversible native lifecycle asks for restart instead of pretending to reload.

Updates are transactions. Keep GUIDs for existing assets, bump the manifest version, publish the matching `v<version>` tag, and let Infernux preserve enabled state, user-moved assets, and importer settings. Uninstall removes package-owned files and lifecycle contributions. Local user files and assets whose ownership moved elsewhere remain intact.

## Release checklist

- Runtime code contains no Editor imports.
- Editor services release threads, sockets, watchers, and callbacks.
- Components can be added in the Editor and load in a built Player.
- Plugin pages describe the shipped behavior in English and Chinese.
- `python package.py verify ...` succeeds.
- A clean install, hot reload, disable, update, Player build, and uninstall all succeed without restarting unless native state requires it.
