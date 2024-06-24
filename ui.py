import bpy
from bpy.types import Panel

from .import utils
from .utils import fetch_user_preferences

import itertools
from rna_keymap_ui import _indented_layout


class NODE_PT_straighten_reroute_links(Panel):
    bl_label = "Straighten Reroute Links"
    bl_category = "Cleanup"
    bl_region_type = "UI"
    bl_space_type = 'NODE_EDITOR'

    def draw(self, context):
        layout = self.layout
        prefs = fetch_user_preferences()

        layout.label(text="Apply To:")
        layout.prop(prefs, "operator_nodes", text="")
        layout.prop(prefs, "reroute_padding")
        layout.prop(prefs, "reposition_exceeding_reroutes")
        layout.prop(prefs, "resolve_ambiguous_reroutes")

        row = layout.row(align=True)
        row.operator("node.straighten_reroutes", text="Inputs").target_reroutes = 'INPUT'
        row.operator("node.straighten_reroutes", text="Outputs").target_reroutes = 'OUTPUT'
        layout.operator("node.straighten_reroutes", text="All Reroutes").target_reroutes = 'BOTH'


classes = (
    NODE_PT_straighten_reroute_links,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        

if __name__ == "__main__":
    register()