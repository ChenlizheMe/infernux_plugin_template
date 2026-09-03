"""Early import lifecycle for runtime and editor services."""

from importlib import import_module

from Infernux.lifecycle import InxPreload, PreloadContext


class ExamplePluginPreload(InxPreload):
    def preload(self, context: PreloadContext) -> None:
        if not context.runtime:
            import_module("your_studio.example_plugin_editor.panel")

    def unload(self) -> None:
        pass
