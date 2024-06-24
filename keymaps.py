from .keymap_ui import KeymapItemDef, KeymapStructure, KeymapLayout
from .operators import (
    NODE_OT_straighten_reroutes,
)

keymap_info = {
    "keymap_name": "Node Editor",
    "space_type": "NODE_EDITOR",
}


keymap_structure = KeymapStructure(
    { 
        NODE_OT_straighten_reroutes.bl_label: (       
            KeymapItemDef(NODE_OT_straighten_reroutes.bl_idname, props={"target_reroutes": "INPUT"}, **keymap_info),
            KeymapItemDef(NODE_OT_straighten_reroutes.bl_idname, props={"target_reroutes": "OUTPUT"}, **keymap_info),
            KeymapItemDef(NODE_OT_straighten_reroutes.bl_idname, props={"target_reroutes": "BOTH"}, **keymap_info),
        )
    }
)


mapping_dict = {
    NODE_OT_straighten_reroutes.bl_idname: (
        "target_reroutes", {
            "INPUT": "Input Reroutes", 
            "OUTPUT": "Output Reroutes", 
            "BOTH": "All Reroutes"
            },
    ),
}

keymap_layout = KeymapLayout(layout_structure=keymap_structure, custom_label_mappings=mapping_dict)


def register():
    keymap_structure.register()


def unregister():
    keymap_structure.unregister()
