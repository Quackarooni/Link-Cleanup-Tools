import bpy
import ctypes
import platform

from functools import wraps
from mathutils import Vector

weird_offset = 10
reroute_width = 10


class TemporaryUnframe:
    def __init__(self, nodes):
        self.parent_dict = {}
        for node in nodes:
            if node.parent is not None:
                self.parent_dict[node] = node.parent
            node.parent = None

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        for node, parent in self.parent_dict.items():
            node.parent = parent


def fetch_user_preferences(attr_id=None):
    prefs = bpy.context.preferences.addons[__package__].preferences

    if attr_id is None:
        return prefs
    else:
        return getattr(prefs, attr_id)


def fetch_nodes(context, *, target="ALL"):
    if target == 'ALL':
        return context.space_data.edit_tree.nodes
    elif target == 'SELECTED':
        return context.selected_nodes
    else:
        raise ValueError(f"'{target}' is not a valid target value.")


def get_width(node):
    if node.bl_idname == "NodeReroute":
        return reroute_width
    else:
        return node.width


def get_height(node):
    return node.width * node.dimensions.y / node.dimensions.x


def get_left(node):
    if node.bl_static_type == "REROUTE":
        return node.location.x
    else:
        return node.location.x


def get_center(node):
    if node.bl_static_type == "REROUTE":
        return node.location.x
    else:
        return node.location.x + (0.5 * node.width)


def get_right(node):
    if node.bl_static_type == "REROUTE":
        return node.location.x
    else:
        return node.location.x + node.width


def get_top(node):
    if node.bl_static_type == "REROUTE":
        return node.location.y
    elif node.hide:
        return node.location.y + (0.5 * get_height(node)) - weird_offset
    else:
        return node.location.y


def get_middle(node):
    if node.bl_static_type == "REROUTE":
        return node.location.y
    elif node.hide:
        return node.location.y - weird_offset
    else:
        return node.location.y - (0.5 * get_height(node))


def get_bottom(node):
    if node.bl_static_type == "REROUTE":
        return node.location.y
    elif node.hide:
        return node.location.y - (0.5 * get_height(node)) - weird_offset
    else:
        return node.location.y - get_height(node)


def get_bounds(nodes):
    if len(nodes) <= 0:
        return 0, 0, 0, 0

    min_x = min(get_left(node) for node in nodes)
    max_x = max(get_right(node) for node in nodes)
    min_y = min(get_bottom(node) for node in nodes)
    max_y = max(get_top(node) for node in nodes)

    return min_x, max_x, min_y, max_y


def get_bounds_midpoint(nodes):
    nodes = tuple(n for n in nodes if n.bl_idname != "NodeFrame")

    min_x, max_x, min_y, max_y = get_bounds(nodes)
    midpoint_x = 0.5 * (min_x + max_x)
    midpoint_y = 0.5 * (min_y + max_y)

    return midpoint_x, midpoint_y


class StructBase(ctypes.Structure):
    _subclasses = []
    __annotations__ = {}

    def __init_subclass__(cls):
        cls._subclasses.append(cls)

    @staticmethod
    def _init_structs():
        functype = type(lambda: None)
        for cls in StructBase._subclasses:
            fields = []
            for field, value in cls.__annotations__.items():
                if isinstance(value, functype):
                    value = value()
                fields.append((field, value))
            if fields:
                cls._fields_ = fields
            cls.__annotations__.clear()
        StructBase._subclasses.clear()

    @classmethod
    def get_fields(cls, tar):
        return cls.from_address(tar.as_pointer())


class BNodeSocketRuntimeHandle(StructBase):  # \source\blender\makesdna\DNA_node_types.h
    if platform.system() == "Windows":
        _padding_0: ctypes.c_char * 8

    declaration: ctypes.c_void_p
    changed_flag: ctypes.c_uint32
    total_inputs: ctypes.c_short
    _padding_1: ctypes.c_char * 2
    location: ctypes.c_float * 2


class BNodeStack(StructBase):
    vec: ctypes.c_float * 4
    min: ctypes.c_float
    max: ctypes.c_float
    data: ctypes.c_void_p
    hasinput: ctypes.c_short
    hasoutput: ctypes.c_short
    datatype: ctypes.c_short
    sockettype: ctypes.c_short
    is_copy: ctypes.c_short
    external: ctypes.c_short
    _padding_: ctypes.c_char * 4


class BNodeSocket(StructBase):
    next: ctypes.c_void_p  # lambda: ctypes.POINTER(BNodeSocket)
    prev: ctypes.c_void_p  # lambda: ctypes.POINTER(BNodeSocket)
    prop: ctypes.c_void_p
    identifier: ctypes.c_char * 64
    name: ctypes.c_char * 64
    storage: ctypes.c_void_p
    in_out: ctypes.c_short
    typeinfo: ctypes.c_void_p
    idname: ctypes.c_char * 64
    default_value: ctypes.c_void_p
    _padding_: ctypes.c_char * 4
    label: ctypes.c_char * 64
    description: ctypes.c_char * 64

    if (bpy.app.version >= (4, 0)) and (bpy.app.version_string != "4.0.0 Alpha"):
        short_label: ctypes.c_char * 64

    default_attribute_name: ctypes.POINTER(ctypes.c_char)
    to_index: ctypes.c_int
    link: ctypes.c_void_p
    ns: BNodeStack
    runtime: ctypes.POINTER(BNodeSocketRuntimeHandle)


def get_socket_location(sk):
    if (not sk.enabled) and (sk.hide):
        return Vector((0, 0))

    return Vector(BNodeSocket.get_fields(sk).runtime.contents.location[:])


StructBase._init_structs()
