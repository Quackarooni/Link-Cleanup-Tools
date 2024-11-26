import bpy

from bpy.types import Operator
from bpy.props import EnumProperty, FloatProperty

from . import utils
from .utils import fetch_user_preferences

# EnumProperties that are generated dynamically tend to misbehave as Python tends to clean up memory
# Caching the results forces Python to keep track of the data while the operator is in use
enum_callback_cache = []


def cache_enum_results(function):
    def wrapped_func(self, context):
        enum_callback_cache.clear()
        output = function(self, context)
        enum_callback_cache.extend(output)
        return output

    return wrapped_func


class NODE_OT_straighten_reroutes(Operator):
    bl_idname = "node.straighten_reroutes"
    bl_label = "Straighten Reroutes"
    bl_description = "Reposition reroutes such that the links they have to other nodes are straight"
    bl_options = {"REGISTER", "UNDO"}

    target_reroutes: EnumProperty(
        name="Target Reroutes",
        items=(
            ("INPUT", "Input Reroutes", "Straighten reroutes connected to an input socket"),
            ("OUTPUT", "Output Reroutes", "Straighten reroutes connected to output socket"),
            ("BOTH", "Both", "Straighten reroutes connected to either an input/output socket")
        ),
        default='BOTH',
        description="Specifies which reroutes will be repositioned and straightened")

    @classmethod
    def poll(cls, context):
        try:
            space = context.space_data

            is_existing = space.node_tree is not None
            is_node_editor = space.type == "NODE_EDITOR"

            return all((is_existing, is_node_editor))
        
        except AttributeError:
            return False

    @staticmethod
    def get_connected_socket(reroute, in_out):
        try:
            if in_out == 'INPUT':
                return reroute.inputs[0].links[0].from_socket
            elif in_out == 'OUTPUT':
                return reroute.outputs[0].links[0].to_socket
        
        except IndexError:
            return None

    @staticmethod
    def is_connected_to_non_reroute(reroute, in_out):
        try:
            if in_out == 'INPUT':
                node = reroute.inputs[0].links[0].from_node
            elif in_out == 'OUTPUT':
                node = reroute.outputs[0].links[0].to_node

            return node.bl_idname != 'NodeReroute'
        
        except IndexError:
            return False

    def straighten_reroutes(self, reroutes, *, in_out):
        prefs = fetch_user_preferences()
        padding = prefs.reroute_padding

        if in_out == 'INPUT':
            clamp_function = max
            offset = padding
        elif in_out == 'OUTPUT':
            clamp_function = min
            offset = -padding
        else:
            raise ValueError(f"'{in_out}' invalid value for parameter 'in_out'.")

        #reroutes_to_straighten = tuple(r for r in reroutes if self.is_connected_to_non_reroute(r, in_out=in_out))
        reroutes_to_straighten = tuple(r for r in reroutes)
        for reroute in reroutes_to_straighten:
            target_socket = self.get_connected_socket(reroute, in_out=in_out)
            target = utils.get_socket_location(target_socket)
            
            if prefs.reposition_exceeding_reroutes:
                reroute.location.x = clamp_function(reroute.location.x , target.x + offset)
            reroute.location.y = target.y

        return

    def execute(self, context):
        target_reroutes = self.target_reroutes
        prefs = fetch_user_preferences()

        nodes = utils.fetch_nodes(context, target=prefs.apply_to)
        reroutes = tuple(n for n in nodes if n.bl_idname == "NodeReroute")

        old_positions = tuple(map(tuple, (r.location for r in reroutes)))

        with utils.TemporaryUnframe(nodes=nodes):
            if target_reroutes == 'INPUT':
                self.straighten_reroutes(reroutes, in_out='INPUT')

            elif target_reroutes == 'OUTPUT':
                self.straighten_reroutes(reroutes, in_out='OUTPUT')

            elif target_reroutes == 'BOTH':
                if prefs.resolve_ambiguous_reroutes == 'INPUT':
                    self.straighten_reroutes(reroutes, in_out='OUTPUT')
                    self.straighten_reroutes(reroutes, in_out='INPUT')
                elif prefs.resolve_ambiguous_reroutes == 'OUTPUT':
                    self.straighten_reroutes(reroutes, in_out='INPUT')
                    self.straighten_reroutes(reroutes, in_out='OUTPUT')

        new_positions = tuple(map(tuple, (r.location for r in reroutes)))

        if old_positions == new_positions:
            self.report({'WARNING'}, 'Reroute links are already straightened.')
            return {"CANCELLED"}
        else:
            self.report({'INFO'}, 'Successfully straightened reroute links.')
            return {"FINISHED"}


class NODE_OT_straighten_node_link(Operator):
    bl_idname = "node.straighten_node_link"
    bl_label = "Straighten Node Link"
    bl_description = "Reposition active node such that the chosen link is straight"
    bl_options = {"REGISTER", "UNDO"}

    offset: FloatProperty()

    @classmethod
    def poll(cls, context):
        return context.active_node is not None

    def execute(self, context):
        prefs = fetch_user_preferences()
        node = context.active_node
        node.location.y += self.offset

        return {"FINISHED"}


class NODE_OT_toggle_straighten_reroute_nodes(Operator):
    bl_idname = "node.toggle_straighten_reroute_nodes"
    bl_label = "Apply To"
    bl_description = "Reposition reroutes such that the links they have to other nodes are straight"
    bl_options = {"INTERNAL"}

    @classmethod
    def poll(cls, context):
        try:
            space = context.space_data

            is_existing = space.node_tree is not None
            is_node_editor = space.type == "NODE_EDITOR"

            return all((is_existing, is_node_editor))
        
        except AttributeError:
            return False

    def execute(self, context):
        prefs = fetch_user_preferences()
        target = prefs.apply_to

        if target == 'SELECTED':
            prefs.apply_to = "ALL"
        elif target == 'ALL':
            prefs.apply_to = "SELECTED" 

        utils.refresh_ui(context)        

        self.report({'INFO'}, f"{NODE_OT_straighten_reroutes.bl_label} : Target nodes set to '{prefs.apply_to}.'")
        return {"FINISHED"}


classes = (
    NODE_OT_straighten_reroutes,
    NODE_OT_toggle_straighten_reroute_nodes,
    NODE_OT_straighten_node_link,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
