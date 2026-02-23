# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 DTRabbit

from bpy.types import PropertyGroup, UIList, Object, Operator
from bpy.props import CollectionProperty, IntProperty, PointerProperty, StringProperty

from .support_props import SupportProperties
from .utils import (current_instr,
                   delete_objects,
                   current_instr_list_item,
                   current_support_list_item)

def init_item(item, s_props):
        item.thickness = s_props.thickness
        item.support_dim_X = s_props.support_dim_X
        item.extension = s_props.extension
        item.separation = s_props.separation
        item.flange_extension = s_props.flange_extension
        item.flange_dim_Z = s_props.flange_dim_Z
        item.screw_diam = s_props.screw_diam
        item.screw_length = s_props.screw_length
        item.nut_diam = s_props.nut_diam
        item.washer_diam = s_props.washer_diam
        item.washer_depth = s_props.washer_depth
        item.slot_length = s_props.slot_length
        item.support = None
        item.pad = None
        item.clamp = None
        item.nut_plate = None

class SupportListItem(PropertyGroup):

    name: StringProperty()
    support_props: PointerProperty(type=SupportProperties)
    support: PointerProperty(type=Object)
    pad: PointerProperty(type=Object)
    clamp: PointerProperty(type=Object)
    nut_plate: PointerProperty(type=Object)

class SupportList(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = 'OBJECT_DATAMODE'

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name, icon=custom_icon)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon=custom_icon)

class SupportListNewItem(Operator):

    bl_idname = "support_list.new_item"
    bl_label = "Add a new support"

    @classmethod
    def poll(cls, context):
        return context.scene.case_props.instrument_list and \
            (context.scene.case_props.instrument_list_index >= 0)

    def execute(self, context):
        props = current_instr_list_item(context) #if context.scene.case_props.instrument_list_index >= 0 else context.scene.case_props
        props.support_list.add()
        props.support_list_index = len(props.support_list) - 1
        props.support_list[-1].name = current_instr(context).name + "_S" + str(props.support_count)
        props.support_count += 1
        init_item(props.support_list[-1].support_props, context.scene.support_props)
        return {'FINISHED'}

class SupportListDeleteItem(Operator):

    bl_idname = "support_list.delete_item"
    bl_label = "Remove a support"

    @classmethod
    def poll(cls, context):
        instr = current_instr_list_item(context)
        if instr is None:
            return False
        else:
            return instr.support_list_index > -1

    def execute(self,context):
        props = current_instr_list_item(context) #if context.scene.case_props.instrument_list_index >= 0 else context.scene.case_props
        support_list = props.support_list
        index = props.support_list_index
        if support_list[index].support is not None:
            delete_objects([support_list[index].support, support_list[index].pad, support_list[index].clamp, support_list[index].nut_plate])
        support_list.remove(index)
        props.support_list_index = min(max(0, index-1), len(support_list)-1)
        return {'FINISHED'}

class SupportListCopyItem(Operator):

    bl_idname = "support_list.copy_item"
    bl_label = "Add a new copy of the selected support"

    @classmethod
    def poll(cls, context):
        instr = current_instr_list_item(context)
        if instr is None:
            return False
        else:
            return instr.support_list_index > -1

    def execute(self, context):
        props = current_instr_list_item(context) #if context.scene.case_props.instrument_list_index >= 0 else context.scene.case_props
        s_props = props.support_list[props.support_list_index].support_props
        props.support_list.add()
        props.support_list_index = len(props.support_list) - 1
        props.support_list[-1].name = current_instr(context).name + "_S" + str(props.support_count)
        props.support_count += 1
        init_item(props.support_list[-1].support_props, s_props)
        props.support_list[-1].support_props.position = s_props.position
        return {'FINISHED'}

class SupportListRemoveObjects(Operator):

    bl_idname = "support_list.delete_objects"
    bl_label = "Remove support objects, but leave list entry"

    @classmethod
    def poll(cls, context):
        item = current_support_list_item(context)
        if item is None:
            return False
        else:
            return item.support is not None

    def execute(self, context):
        props = current_support_list_item(context)
        delete_objects([props.support, props.pad, props.clamp, props.nut_plate])
        props.support = None
        props.pad = None
        props.clamp = None
        props.nut_plate = None
        return {'FINISHED'}


registration_list = (SupportListItem, SupportList, SupportListNewItem, SupportListDeleteItem, SupportListCopyItem, SupportListRemoveObjects)
