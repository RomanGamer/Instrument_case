# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 DTRabbit

import bpy
from bpy.types import PropertyGroup
from bpy.props import FloatProperty

def screw_diam_update(self, context):
    context.scene.support_props.screw_diam = context.scene.fittings_props.screw_diam

def screw_length_update(self, context):
    context.scene.support_props.screw_length = context.scene.fittings_props.screw_length

def nut_diam_update(self, context):
    context.scene.support_props.nut_diam = context.scene.fittings_props.nut_diam

def washer_diam_update(self, context):
    context.scene.support_props.washer_diam = context.scene.fittings_props.washer_diam

def washer_depth_update(self, context):
    context.scene.support_props.washer_depth = context.scene.fittings_props.washer_depth

class FittingsProperties(PropertyGroup):

    screw_diam: FloatProperty(name="Screw diameter",
                             description="Diameter of the screw shaft",
                             min=0.003,
                             default=0.0048,
                             unit='LENGTH',
                             update=screw_diam_update)
    screw_length: FloatProperty(name="Screw length",
                             description="Length of the screw shaft",
                             min=0.016,
                             default=0.016,
                             unit='LENGTH',
                             update=screw_length_update)
    nut_diam: FloatProperty(name="Nut diameter",
                             description="Diameter of the nut across corners",
                             min=0.006,
                             default=0.00882,
                             unit='LENGTH',
                             update=nut_diam_update)
    washer_diam: FloatProperty(name="Washer diameter",
                             description="Diameter of washer",
                             min=0.006,
                             default=0.00982,
                             unit='LENGTH',
                             update=washer_diam_update)
    washer_depth: FloatProperty(name="Washer depth",
                             description="Thickness of washer",
                             min=0.0005,
                             default=0.00095,
                             unit='LENGTH',
                             update=washer_depth_update)

registration_list = (FittingsProperties,)
fittings_props_list = ("screw_diam", "screw_length", "nut_diam", "washer_diam", "washer_depth")
