"""Example panel available only inside the editor."""

from Infernux.engine.interaction import PanelInteractionDescriptor
from Infernux.engine.ui.editor_panel import EditorPanel
from Infernux.engine.ui.panel_registry import editor_panel


@editor_panel(
    "Example Plugin",
    type_id="your_studio.example_plugin",
    title_key="your_studio.example_plugin.panel_title",
    menu_path="Extensions/Example Plugin/Tools/Diagnostics/Live",
    menu_path_keys=(
        "menu.extensions",
        "your_studio.example_plugin.menu_root",
        "your_studio.example_plugin.menu_tools",
        "your_studio.example_plugin.menu_diagnostics",
        "your_studio.example_plugin.menu_live",
    ),
    interaction=PanelInteractionDescriptor(),
)
class ExamplePluginPanel(EditorPanel):
    def __init__(self) -> None:
        super().__init__("Example Plugin", "your_studio.example_plugin")

    def on_render_content(self, ctx) -> None:
        ctx.label("Example Plugin")
        ctx.text_wrapped("This panel was registered by the plugin preload lifecycle.")
