# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 DTRabbit

import bpy
import bmesh
from bpy.types import Operator

# from math import round
from mathutils import Vector

from .utils import (X, Y, Z,
                    current_instr,
                    set_mode,
                    apply_transformations,
                    add_block,
                    add_and_apply_bool,
                    remove_doubles,
                    separate_parts,
                    select_object,
                    delete_object,
                    add_cylinder,
                    average,
                    current_support_list_item
                    )

def bevel_support(support, s_props, support_dim_Y, axis_to_base_Z, flange_dim_Z):
    select_object(support)
    bpy.ops.object.mode_set(mode='EDIT')
    select_mode = bpy.context.tool_settings.mesh_select_mode[:]
    bpy.context.tool_settings.mesh_select_mode = (False, True, False)
    bm = bmesh.from_edit_mesh(support.data)

    ref_corner_loc = [round(s_props.support_dim_X /2, 4),
                      round(support_dim_Y / 2, 4),
                      round((axis_to_base_Z / 2) - (s_props.separation / 2), 4)]
    flange_top_edges = []
    for e in bm.edges:
        e.select = False
        # is e on top of support
        for v in e.verts:
            abs_loc = [abs(round(c, 4)) for c in v.co]
            if ref_corner_loc == abs_loc: e.select = True
        # is e on top of flange
        if (round(e.verts[0].co[Z], 4) == round(e.verts[1].co[Z], 4)) and \
           (round(e.verts[1].co[Z], 4) == -round((axis_to_base_Z / 2) - flange_dim_Z, 4)):
            flange_top_edges.append(e)
    shortest_edge_len = 100
    for e in flange_top_edges:
        shortest_edge_len = round(e.calc_length(), 4) if e.calc_length() < shortest_edge_len \
                                                      else shortest_edge_len
    for e in flange_top_edges:
        edge_len = round(e.calc_length(), 4)
        if (edge_len == shortest_edge_len) or \
           (edge_len == round(s_props.support_dim_X, 4)) or \
           (edge_len == round(support_dim_Y, 4)):
            e.select = True
    bpy.ops.mesh.bevel(offset=0.002, offset_pct=0, segments=4, affect='EDGES')
    bpy.context.tool_settings.mesh_select_mode = select_mode
    bpy.ops.object.mode_set(mode='OBJECT')

def bevel_pad(pad, s_props):
    select_object(pad)
    bpy.ops.object.mode_set(mode='EDIT')
    select_mode = bpy.context.tool_settings.mesh_select_mode[:]
    bpy.context.tool_settings.mesh_select_mode = (False, True, False)
    bm = bmesh.from_edit_mesh(pad.data)

    ref_Z = round((s_props.separation / 2), 4)
    candidate_edges = []
    other_edges = []
    high_X = 0
    low_X = 0
    for e in bm.edges:
        e.select = False
        for v in e.verts:
            abs_Z = abs(round(v.co[Z], 4))
            high_X = round(v.co[X], 4) if round(v.co[X], 4) > high_X else high_X
            low_X = round(v.co[X], 4) if round(v.co[X], 4) < low_X else low_X
            if ref_Z == abs_Z:
                if (round(e.other_vert(v).co[Z], 4) == round(v.co[Z], 4)):
                    if (round(e.other_vert(v).co[X], 4) == round(v.co[X], 4)) and \
                       (e not in candidate_edges):
                        candidate_edges.append(e)
                    elif (round(e.other_vert(v).co[X], 4) != round(v.co[X], 4)) and \
                         (e not in other_edges):
                        other_edges.append(e)
    loop_edges = [[e for e in candidate_edges if round(e.verts[0].co[X], 4) == high_X],
                  [e for e in candidate_edges if round(e.verts[0].co[X], 4) == low_X]]
    low_Y = 100
    for e in other_edges:
        for v in e.verts:
            low_Y = abs(round(v.co[Y], 4)) \
                    if abs(round(v.co[Y], 4)) < low_Y \
                    else low_Y
    inner_edges = [e for e in other_edges \
                     if (abs(round(e.verts[0].co[Y], 4)) == low_Y) or \
                        (abs(round(e.verts[1].co[Y], 4)) == low_Y)]
    for l in loop_edges:
        for e in l:
            e.select = True
        bpy.ops.mesh.shortest_path_select()
    for e in inner_edges:
        e.select = True
    bpy.ops.mesh.bevel(offset=0.002, offset_pct=0, segments=4, affect='EDGES')
    bpy.context.tool_settings.mesh_select_mode = select_mode
    bpy.ops.object.mode_set(mode='OBJECT')

def build_nut_washer(loc, s_props, m_props):
    flange_top = loc[Z] + m_props.l_sec_thickness / 2
    washer_loc = [loc[X], loc[Y], flange_top - s_props.washer_depth / 2]
    nut = add_cylinder(name="NUT",
                       location=loc,
                       radius=(s_props.nut_diam * 1.1) / 2,
                       depth=m_props.l_sec_thickness * 1.1,
                       vertices=6)
    add_and_apply_bool(nut, 'UNION',
                       add_cylinder(name="WASHER",
                                    location=washer_loc,
                                    radius=(s_props.washer_diam * 1.1) / 2,
                                    depth=s_props.washer_depth + 0.0001, vertices=64),
                       True)
    return nut

def build_slot(location, s_props, flange_dim_Z):
    # slot width is 0.5mm wider than screw diameter
    slot_dim_Y = s_props.screw_diam * 1.1
    slot_dim_Z = flange_dim_Z + 0.01
    slot = add_block("SLOT", Vector([0, 0, 0]) + location, [s_props.slot_length, slot_dim_Y, slot_dim_Z])
    add_and_apply_bool(slot, 'UNION',
                       add_cylinder(name="SLOT_END_1",
                                    location=Vector([-s_props.slot_length / 2, 0, 0]) + location,
                                    radius=slot_dim_Y / 2, depth=slot_dim_Z),
                       del_object=True)
    add_and_apply_bool(slot, 'UNION',
                       add_cylinder(name="SLOT_END_2",
                                    location=Vector([s_props.slot_length / 2, 0, 0]) + location,
                                    radius=slot_dim_Y / 2, depth=slot_dim_Z),
                       del_object=True)
    return slot

def build_support(self, context, orientation):

    # get the current instrument, make sure it's selected,
    # in the right mode and has no scale or rotation
    instrument = current_instr(context)
    select_object(instrument)
    set_mode(instrument, 'OBJECT')
    apply_transformations(instrument, S=True, R=True)

    # convenience variables for lists and property groups
    inst_list = context.scene.case_props.instrument_list
    inst_index = context.scene.case_props.instrument_list_index
    support_item = inst_list[inst_index].support_list[inst_list[inst_index].support_list_index]
    c_props = context.scene.case_props
    s_props = support_item.support_props
    m_props = context.scene.materials_props
    f_props = context.scene.fittings_props

    # distance from instrument axis to bottom or top of case
    base = c_props.base_Z if orientation == 'BASE' \
                          else instrument.location[Z] - abs(c_props.lid_Z - instrument.location[Z])
    axis_to_base_Z = abs(instrument.location[Z] - base)

    # centre of support (X)
    support_loc_X = instrument.location[X] + s_props.position
    # location vector of the support
    support_location = [support_loc_X,
                        instrument.location[Y],
                        instrument.location[Z] - (axis_to_base_Z / 2)]

    # construct a section of the instrument for building the pad, support and clamp spacer
    # a cube slightly wider than the support and scaled bigger than the max size
    # in Y and Z
    support_item.pad = add_block(support_item.name+"P",
                                    (support_loc_X, instrument.location[Y], instrument.location[Z]),
                                    (s_props.support_dim_X, 1, 1))

    # cut instrument from block
    add_and_apply_bool(support_item.pad, 'INTERSECT', instrument)
    # scale the section to allow pad thickness
    pad_scale = 1+(2*(s_props.thickness)/min(support_item.pad.dimensions[Y],
                                                support_item.pad.dimensions[Z]))
    support_item.pad.scale = (1, pad_scale, pad_scale)
    apply_transformations(support_item.pad, S = True)
    # cut instrument from centre of scaled pad
    add_and_apply_bool(support_item.pad, 'DIFFERENCE', instrument)

    # add support
    # calculate size of support across instrument (Y)
    support_dim_Y = support_item.pad.dimensions[Y] + 2 * (s_props.thickness + s_props.extension)
    # scale vector for support from support_dim_X to required depth (Y) and height (Z)
    support_scale = Vector((s_props.support_dim_X, support_dim_Y, abs(axis_to_base_Z)))
    # add a block
    support = add_block("Support_temp", support_location, support_scale)

    # cut the pad down
    add_and_apply_bool(support_item.pad, 'INTERSECT', support)
    # cut the pad out
    add_and_apply_bool(support, 'DIFFERENCE', support_item.pad)

    # make a temporary block for cutting the separation gap
    gap = add_block("Gap",
                    (support_loc_X, instrument.location[Y], instrument.location[Z]),
                    (1, 1, s_props.separation))
    add_and_apply_bool(support, 'DIFFERENCE', gap)
    add_and_apply_bool(support_item.pad, 'DIFFERENCE', gap)
    delete_object(gap)

    # clean up objects and identify parts
    remove_doubles(support)
    remove_doubles(support_item.pad)
    support_item.support, support_item.clamp = separate_parts(support,
                                                                large_name=support_item.name+"H",
                                                                small_name=support_item.name+"C")
    remove_doubles(support_item.support)
    remove_doubles(support_item.clamp)

    # make flange
    flange_ext_Y = max(s_props.flange_extension, s_props.washer_diam *2)
    flange_ext_X = s_props.slot_length + s_props.screw_diam + s_props.washer_diam + 0.002
    flange_dim_Y = support_dim_Y + 2 * flange_ext_Y
    flange_dim_X = s_props.support_dim_X + 2 * flange_ext_X

    t = s_props.screw_length - (m_props.l_sec_thickness - 0.001) - s_props.washer_depth - m_props.int_ply_thickness

    flange_dim_Z = s_props.flange_dim_Z if t < s_props.flange_dim_Z else t
    flange_radius = max(flange_dim_X, flange_dim_Y) / 2
    flange_loc_X = support_loc_X
    flange_loc_Y = instrument.location[Y]
    flange_loc_Z = base + (flange_dim_Z / 2)
    # put the flange and support together
    add_and_apply_bool(support_item.support,
                       'UNION',
                       add_cylinder(name="FLANGE",
                                    location=[flange_loc_X, flange_loc_Y, flange_loc_Z],
                                    radius=flange_radius, depth=flange_dim_Z,
                                    vertices=64),
                       del_object=True)
    remove_doubles(support_item.support)

    bevel_support(support_item.support, s_props, support_dim_Y, axis_to_base_Z, flange_dim_Z)
    bevel_pad(support_item.pad, s_props)

    # make the nut plate
    nut_plate_loc_Z = flange_loc_Z - flange_dim_Z - m_props.int_ply_thickness
    support_item.nut_plate = add_cylinder(name=support_item.name+"N",
                                          location=[flange_loc_X, flange_loc_Y, nut_plate_loc_Z],
                                          radius=flange_radius, depth=m_props.l_sec_thickness,
                                          vertices=64)
    # make screw slots in flange and nut holes in nut plate
    slot_dim_X = s_props.slot_length + s_props.washer_diam + 0.002

    for pos in [1, -1]:
        # make slots and nuts on X axis
        slot_loc_X = flange_loc_X - pos * flange_radius + pos * (slot_dim_X / 2 + 0.005)
        slot_loc = Vector([slot_loc_X, flange_loc_Y, flange_loc_Z])
        add_and_apply_bool(support_item.support,
                           'DIFFERENCE',
                           build_slot(slot_loc, s_props, flange_dim_Z),
                           del_object=True)
        nut_loc = Vector([slot_loc_X, flange_loc_Y, nut_plate_loc_Z])
        add_and_apply_bool(support_item.nut_plate,
                            'DIFFERENCE',
                            build_nut_washer(nut_loc, s_props, m_props),
                            del_object=True)
        # make slots and nuts on Y axis
        slot_loc_Y = flange_loc_Y + pos * ((support_dim_Y / 2) + s_props.washer_diam)
        slot_loc = Vector([flange_loc_X, slot_loc_Y, flange_loc_Z])
        add_and_apply_bool(support_item.support,
                           'DIFFERENCE',
                           build_slot(slot_loc, s_props, flange_dim_Z),
                           del_object=True)
        nut_loc = Vector([flange_loc_X, slot_loc_Y, nut_plate_loc_Z])
        add_and_apply_bool(support_item.nut_plate,
                            'DIFFERENCE',
                            build_nut_washer(nut_loc, s_props, m_props),
                            del_object=True)

    # rotate the support structures through X=180 degrees if it's a lid support
    if orientation == 'LID':
        context.scene.cursor.location = instrument.location
        pivot_point = context.scene.tool_settings.transform_pivot_point
        context.scene.tool_settings.transform_pivot_point = 'CURSOR'
        for o in (support_item.support, support_item.pad, support_item.clamp, support_item.nut_plate):
            select_object(o)
            bpy.ops.transform.rotate(value=3.14159, orient_axis='X')
        context.scene.tool_settings.transform_pivot_point = pivot_point

    # make sure the original object is selected at the end
    select_object(instrument)


class MakeSupports(Operator):
    bl_idname = "make.supports"
    bl_label = "Make Instrument Supports base"
    bl_description = "Creates supports and pads for musical instrument cases (base section)"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        instr = current_support_list_item(context)
        if instr is None:
            return False
        else:
            return instr.support is None

    def execute(self, context):
        build_support(self, context, 'BASE')
        return {'FINISHED'}


class MakeHolders(Operator):
    bl_idname = "make.holder"
    bl_label = "Make Instrument Supports lid"
    bl_description = "Creates supports and pads for musical instrument cases (lid section)"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        instr = current_support_list_item(context)
        if instr is None:
            return False
        else:
            return instr.support is None


    def execute(self, context):
        build_support(self, context, 'LID')
        return {'FINISHED'}

registration_list = (MakeSupports, MakeHolders)
