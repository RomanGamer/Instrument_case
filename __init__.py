# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 DTRabbit

if "bpy" in locals():
    import importlib
    importlib.reload(fittings_props)
    importlib.reload(materials_props)
    importlib.reload(support_props)
    importlib.reload(support_list)
    importlib.reload(instrument_list)
    importlib.reload(case_props)
    importlib.reload(supports)
    importlib.reload(ui)

import bpy
from bpy.props import PointerProperty
from . import (fittings_props,
               materials_props,
               support_props,
               support_list,
               instrument_list,
               case_props,
               supports,
               ui)

modules = (fittings_props,
           materials_props,
           support_props,
           support_list,
           instrument_list,
           case_props,
           supports,
           ui)

def register():
    for m in modules:
        print(m, m.registration_list)
        for c in m.registration_list:
            bpy.utils.register_class(c)
    bpy.types.Scene.case_props = PointerProperty(type=case_props.CaseProperties)
    bpy.types.Scene.support_props = PointerProperty(type=support_props.SupportProperties)
    bpy.types.Scene.fittings_props = PointerProperty(type=fittings_props.FittingsProperties)
    bpy.types.Scene.materials_props = PointerProperty(type=materials_props.MaterialsProperties)

def unregister():
    for m in modules:
        for c in m.registration_list:
            bpy.utils.unregister_class(c)
    del bpy.types.Scene.case_props
    del bpy.types.Scene.support_props
    del bpy.types.Scene.fittings_props
    del bpy.types.Scene.materials_props
