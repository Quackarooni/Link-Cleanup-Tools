import bpy
from bpy.types import Menu, Panel

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
        layout.prop(prefs, "apply_to", text="")

        row = layout.row(align=True)
        row.operator("node.straighten_reroutes", text="Inputs").target_reroutes = 'INPUT'
        row.operator("node.straighten_reroutes", text="Outputs").target_reroutes = 'OUTPUT'
        layout.operator("node.straighten_reroutes", text="All Reroutes").target_reroutes = 'BOTH'
        layout.menu("NODE_MT_straighten_node_link")


class NODE_MT_straighten_node_link(Menu):
    bl_label = "Straighten Node Link"
    bl_space_type = 'NODE_EDITOR'

    def define_items(self, context):
        node = context.active_node

        for socket in itertools.chain(node.inputs, node.outputs):
            for i, link in enumerate(socket.links):
                from_socket = link.from_socket
                to_socket = link.to_socket

                if socket.is_output:
                    icon = "TRACKING_FORWARDS_SINGLE"
                    offset = utils.get_socket_location(to_socket).y - utils.get_socket_location(from_socket).y
                    label = f"{to_socket.name} ({offset:.2f})"
                else:
                    icon = "TRACKING_BACKWARDS_SINGLE"
                    offset = utils.get_socket_location(from_socket).y - utils.get_socket_location(to_socket).y
                    label = f"{from_socket.name} ({offset:.2f})"

                yield ((offset, label, icon))


    def draw(self, context):
        layout = self.layout

        if context.active_node is not None:
            for offset, label, icon in self.define_items(context):
                layout.operator("node.straighten_node_link", text=label, icon=icon).offset = offset


classes = (
    NODE_PT_straighten_reroute_links,
    NODE_MT_straighten_node_link
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        

if __name__ == "__main__":
    register()