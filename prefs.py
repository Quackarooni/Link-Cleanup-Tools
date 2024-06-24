import bpy
from bpy.props import BoolProperty, EnumProperty, IntProperty

from .keymaps import keymap_layout, keymap_structure


class NodeLinkCleanupPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    reposition_exceeding_reroutes: BoolProperty(
        name="Reposition Exceeding Reroutes",
        default=True,
        description="Specifies whether reroutes exceeding the horizontal position of their connected nodes are repositioned horizontally",
    )

    reroute_padding: IntProperty(
        name="Minimum Padding",
        default=30,
        min=0,
        soft_max=100,
        max=9999,
        description="Specifies how far the horizontal padding is when straightening reroutes"
    )

    operator_nodes: EnumProperty(
        name="Operator Nodes",
        items=(
            ("ALL", "All Nodes", "Target all nodes of current nodetree"),
            ("SELECTED", "Selected Nodes", "Target only the selected nodes in current nodetree")
        ),
        default='ALL',
        description="Specifies which nodes the operators would target")


    resolve_ambiguous_reroutes: EnumProperty(
        name="Resolve Ambiguous Reroutes",
        items=(
            ("INPUT", "As Input", "Treat ambiguous reroutes as if connected to an input socket"),
            ("OUTPUT", "As Output", "Treat ambiguous reroutes as if connected to an output socket"),
        ),
        default='INPUT',
        description="Specifies how reroutes that are connected to both an input & output socket is treated")


    def draw(self, context):
        layout = self.layout
        keymap_layout.draw_keyboard_shorcuts(self, layout, context)


keymap_layout.register_properties(preferences=NodeLinkCleanupPreferences)


def register():
    bpy.utils.register_class(NodeLinkCleanupPreferences)


def unregister():
    bpy.utils.unregister_class(NodeLinkCleanupPreferences)
