# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 DTRabbit

from bpy.types import Panel
from .support_props import support_props_list
from .materials_props import materials_props_list
from .fittings_props import fittings_props_list

def show_support_props(box, props, props_active):
    for p in support_props_list:
        row = box.row()
        row.enabled = props_active
        row.prop(props, p)

class SideBar:

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Cases"


class CasesPanel(SideBar, Panel):
    bl_label = "Case"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):

        c_props = context.scene.case_props

        col = self.layout.box().row().column()
        col.row().prop(c_props, "clearance")
        col.row().label(text="Size")
        row = col.row()
        row.enabled = False
        row.prop(c_props, "size")
        col.row().label(text="Location")
        row = col.row()
        row.enabled = False
        row.prop(c_props, "location")
        row = col.row()
        row.label(text="Base Z")
        row.label(text="Lid Z")
        row = col.row()
        row.enabled = False
        row.prop(c_props, "base_Z")
        row.prop(c_props, "lid_Z")


class MaterialsPanel(SideBar, Panel):
    bl_label = "Materials"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        m_props = context.scene.materials_props
        box = self.layout.box()
        for p in materials_props_list:
            row = box.row()
            row.prop(m_props, p)


class FittingsPanel(SideBar, Panel):
    bl_label = "Fittings"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        f_props = context.scene.fittings_props
        box = self.layout.box()
        for p in fittings_props_list:
            row = box.row()
            row.prop(f_props, p)


class InstPanel(SideBar, Panel):
    bl_label = "Instruments"

    def draw(self, context):

        c_props = context.scene.case_props

        box = self.layout.box()
        box.row().template_list("Instrument_UL_List", "The_List", c_props, "instrument_list", c_props, "instrument_list_index")
        row = box.row()
        row.operator('instrument_list.new_item', text="ADD")
        row.operator('instrument_list.delete_item', text="REMOVE")


class SupportsDefaultsPanel(SideBar, Panel):
    bl_label = "Support defaults"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        show_support_props(self.layout.box(), context.scene.support_props, True)

class SupportsPanel(SideBar, Panel):
    bl_label = "Supports"

    def draw(self, context):

        s_props = context.scene.support_props
        c_props = context.scene.case_props
        this_support = s_props
        props_active = False
        if c_props.instrument_list_index >= 0:
            sl_props = c_props.instrument_list[c_props.instrument_list_index]
            support_list_active = True
            if sl_props.support_list_index >= 0:
                this_support = sl_props.support_list[sl_props.support_list_index].support_props
                props_active = True
        else:
            sl_props = context.scene.case_props
            support_list_active = False

        box = self.layout.box()
        box.enabled = support_list_active
        box.row().template_list("SupportList", "The_List", sl_props, "support_list", sl_props, "support_list_index")
        row = box.row()
        row.operator('support_list.new_item', text="ADD")
        row.operator('support_list.copy_item', text="COPY")
        row.operator('support_list.delete_item', text="REMOVE")
        row = box.row()
        row.enabled = props_active
        row.prop(this_support, "position")
        show_support_props(box, this_support, props_active)
        box.row().label(text="Generate")
        row = box.row()
        row.enabled = props_active
        row.operator('make.supports', text="Base")
        row.operator('make.holder', text="Lid")
        row.operator('support_list.delete_objects', text="Remove")

registration_list = (CasesPanel, MaterialsPanel, FittingsPanel, InstPanel, SupportsDefaultsPanel, SupportsPanel)
