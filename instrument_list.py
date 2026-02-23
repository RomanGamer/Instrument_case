# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 DTRabbit

import bpy
from bpy.types import PropertyGroup, UIList, Object, Operator
from bpy.props import PointerProperty, CollectionProperty, IntProperty

from .utils import calc_case, current_instr_list_item
from .support_list import SupportListItem

class InstrumentListItem(PropertyGroup):

    instr: PointerProperty(type = Object)
    support_list: CollectionProperty(name="Support List", type=SupportListItem)
    support_list_index: IntProperty(name="Support List Index", default=-1)
    support_count: IntProperty(default=0)

class Instrument_UL_List(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = 'OBJECT_DATAMODE'

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.instr.name, icon=custom_icon)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon=custom_icon)

class Instrument_LIST_OT_NewItem(Operator):

    bl_idname = "instrument_list.new_item"
    bl_label = "Add a new instrument"

    @classmethod
    def poll(cls, context):
        result = len(context.selected_objects) > 0
        for item in context.scene.case_props.instrument_list:
            if item.instr in context.selected_objects:
                result = False
                break
        return result

    def execute(self, context):
        c_props = context.scene.case_props
        for obj in context.selected_objects:
            c_props.instrument_list.add()
            c_props.instrument_list[-1].instr = obj
            c_props.instrument_list_index = len(c_props.instrument_list) - 1
        calc_case(self, context)
        return {'FINISHED'}

class Instrument_LIST_OT_DeleteItem(Operator):

    bl_idname = "instrument_list.delete_item"
    bl_label = "Remove an instrument"

    @classmethod
    def poll(cls, context):
        return context.scene.case_props.instrument_list and (context.scene.case_props.instrument_list_index >= 0)

    def execute(self,context):
        c_props = context.scene.case_props
        instrument_list = c_props.instrument_list
        for support in current_instr_list_item(context).support_list:
            bpy.ops.support_list.delete_item()
        index = c_props.instrument_list_index
        instrument_list.remove(index)
        c_props.instrument_list_index = min(max(0, index-1), len(instrument_list)-1)
        calc_case(self, context)
        return {'FINISHED'}

registration_list = (InstrumentListItem,
                     Instrument_UL_List,
                     Instrument_LIST_OT_NewItem,
                     Instrument_LIST_OT_DeleteItem)
