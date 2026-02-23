# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 DTRabbit

import bpy
from bpy.types import PropertyGroup
from bpy.props import FloatProperty

class MaterialsProperties(PropertyGroup):

    ext_ply_thickness: FloatProperty(name="External ply thickness",
                             description="Thickness of the outer ply layer",
                             min=0.005,
                             default=0.005,
                             unit='LENGTH')
    int_ply_thickness: FloatProperty(name="Internal ply thickness",
                             description="Thickness of the inner ply layer",
                             min=0.005,
                             default=0.005,
                             unit='LENGTH')
    l_sec_width: FloatProperty(name="L-section Width",
                             description="Width of the L-section",
                             min=0.020,
                             default=0.020,
                             unit='LENGTH')
    l_sec_thickness: FloatProperty(name="L-section thickness",
                             description="Thickness of the L-section",
                             min=0.005,
                             default=0.005,
                             unit='LENGTH')

registration_list = (MaterialsProperties,)
materials_props_list = ("ext_ply_thickness", "int_ply_thickness",
                        "l_sec_width", "l_sec_thickness")
