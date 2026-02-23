# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 DTRabbit

import bpy
import bmesh

from math import prod
from mathutils import Vector

# Globals - hopefully I can get rid of these at a later date
# 'constants' for vector indexing
X = 0
Y = 1
Z = 2
XYZ = (X,Y,Z)

def average(l=[]):
    return sum(l) / len(l) if len(l) > 0 else 0

def select_objects(objects, replace=True):
    if replace: bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        bpy.data.objects[obj.name].select_set(True)
    bpy.context.view_layer.objects.active = objects[0]

def select_object(object, replace=True):
    select_objects([object], replace)

def delete_objects(objects):
    select_objects(objects)
    bpy.ops.object.delete()

def delete_object(object):
    """
    Delete an object
    """
    delete_objects([object])

def duplicate_and_join(name="DUP_AND_JOIN", objects=[]):
    select_objects(objects)
    bpy.ops.object.duplicate()
    if len(objects) > 1:
        bpy.ops.object.join()
    bpy.context.active_object.name = name
    return bpy.context.active_object

def current_instr_list_item(context):
    return context.scene.case_props.instrument_list[context.scene.case_props.instrument_list_index] if context.scene.case_props.instrument_list_index > -1 else None

def current_instr(context):
    return current_instr_list_item(context).instr if current_instr_list_item(context) is not None else None

def current_support_list_item(context):
    props = current_instr_list_item(context)
    return None if props is None else props.support_list[props.support_list_index] if props.support_list_index > -1 else None

def set_mode(obj, new_mode):
    m = obj.mode
    bpy.ops.object.mode_set(mode=new_mode)
    return m

def apply_transformations(object, L = False, R = False, S = False):
    select_object(object)
    bpy.ops.object.transform_apply(location=L, rotation=R, scale=S)

def add_block(block_name, block_location, block_scale):
    """
    Add a block for further processes
    """
    obj = bpy.data.objects.new(name=block_name, object_data=bpy.data.meshes.new(name=block_name))
    obj.location = block_location
    bpy.context.collection.objects.link(obj)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm)
    bm.to_mesh(obj.data)
    obj.scale=block_scale
    apply_transformations(obj, S=True)
    return obj

def add_cylinder(name="C", location=[0,0,0], radius=1, depth=1, vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=location, vertices=vertices)
    bpy.context.active_object.name = name
    return bpy.context.active_object

def add_bool(owner, name, operation, object):
    """
    Add a boolean modifier
    owner: object boolean applies to
    name: identifier for modifier
    operation: boolean operation to apply
    object: object used in operation
    """
    boolean = owner.modifiers.new(name, 'BOOLEAN')
    boolean.operation = operation
    boolean.solver = 'MANIFOLD'
    boolean.object = object

def apply_mod(owner, mod_name):
    """
    Apply boolean bool_name to owner
    """
    select_object(owner)
    bpy.ops.object.modifier_apply(modifier=mod_name, use_selected_objects=True)

def add_and_apply_bool(owner, operation, object, del_object = False):
    add_bool(owner, "temp_bool", operation, object)
    apply_mod(owner, "temp_bool")
    if del_object: delete_object(object)

def remove_doubles(obj):
    select_object(obj)
    m = set_mode(obj, 'EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=0.001)
    set_mode(obj, m)

def separate_parts(obj, large_name="Support", small_name="Clamp"):
    global X,Y,Z
    select_object(obj)
    m = set_mode(obj, 'EDIT')
    bpy.ops.mesh.separate(type='LOOSE')
    volumes = [prod(o.dimensions) for o in bpy.context.selected_objects]
    large, small = (0, 1) if volumes[0] > volumes[1] else (1,0)
    bpy.context.selected_objects[large].name=large_name
    bpy.context.selected_objects[small].name=small_name
    set_mode(obj, m)
    return bpy.context.selected_objects[large], bpy.context.selected_objects[small]

def is_object_mode(context):
    for o in context.selected_objects:
        if o.mode == 'EDIT':
            return False
    return True

def instrument_radii(object, position):
    global X,Y,Z
    b1 = add_block("b1", position, (0.0001,1,1))
    add_and_apply_bool(b1, 'INTERSECT', object)
    radii = (b1.dimensions[Y]/2, b1.dimensions[Z]/2)
    delete_object(b1)
    return radii

def calc_case(self, context):
    c_props = context.scene.case_props
    if len(c_props.instrument_list) > 0:
        # store current selection
        selected_objects = context.selected_objects[:]
        active_object = context.active_object

        parts = [o.instr for o in c_props.instrument_list]
        obj = duplicate_and_join("TEMP_JOINED_INSTRUMENTS", parts)
        rel_bb = [Vector(p) for p in obj.bound_box]
        abs_bb = [obj.location + v for v in rel_bb]
        abs_bb_XYZ = [[], [], []]
        for p in abs_bb:
            for c in XYZ:
                abs_bb_XYZ[c].append(p[c])
        abs_bb_min_max_XYZ = [[min(v) for v in abs_bb_XYZ], [max(v) for v in abs_bb_XYZ]]
        c_props.size = [abs_bb_min_max_XYZ[1][c] - abs_bb_min_max_XYZ[0][c] + c_props.clearance * 2 for c in XYZ]
        c_props.location = [average([abs_bb_min_max_XYZ[1][c], abs_bb_min_max_XYZ[0][c]]) for c in XYZ]
        c_props.base_Z = c_props.location[Z] - (c_props.size[Z] / 2)
        c_props.lid_Z = c_props.location[Z] + (c_props.size[Z] / 2)
        delete_object(obj)
        # restore initial selection
        if len(selected_objects) > 0:
            select_objects(selected_objects)
            bpy.context.view_layer.objects.active = active_object
    else:
        c_props.size = Vector([0,0,0])
        c_props.location = Vector([0,0,0])
        c_props.base_Z = 0
        c_props.lid_Z = 0
