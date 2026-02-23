# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 DTRabbit

import bpy
from bpy.types import PropertyGroup
from bpy.props import FloatProperty, FloatVectorProperty, IntProperty

class SupportProperties(PropertyGroup):

    position: FloatProperty(name="Position",
                            description="Distance from left end of instrument",
                            min=0.025,
                            default=0.025,
                            unit='LENGTH',
                            )
    thickness: FloatProperty(name="Pad Thickness",
                             description="Thickness of padding",
                             min=0.005,
                             default=0.005,
                             unit='LENGTH')
    support_dim_X: FloatProperty(name="Span",
                                 description="Length along the instrument",
                                 min=0.005,
                                 default=0.025,
                                 unit='LENGTH')
    extension: FloatProperty(name="Extension",
                             description="Distance support extends from instrument and pad",
                             min=0.005,
                             default=0.005,
                             unit='LENGTH')
    separation: FloatProperty(name="Separation",
                             description="Distance between base and lid section of support",
                             min=0.002,
                             default=0.002,
                             unit='LENGTH')
    flange_extension: FloatProperty(name="Flange extension",
                                    description="Minimum distance flange extends from side of support",
                                    min=0.01,
                                    default=0.01,
                                    unit='LENGTH')
    flange_dim_Z: FloatProperty(name="Flange thickness",
                                    description="Min thickness of flange",
                                    min=0.003,
                                    default=0.003,
                                    unit='LENGTH')
    screw_diam: FloatProperty(name="Screw diameter",
                             description="Diameter of the screw shaft",
                             min=0.003,
                             default=0.0048,
                             unit='LENGTH')
    screw_length: FloatProperty(name="Screw length",
                             description="Length of the screw shaft",
                             min=0.016,
                             default=0.016,
                             unit='LENGTH')
    nut_diam: FloatProperty(name="Nut diameter",
                             description="Diameter of the nut across corners",
                             min=0.006,
                             default=0.00882,
                             unit='LENGTH')
    washer_diam: FloatProperty(name="Washer diameter",
                             description="Diameter of washer",
                             min=0.006,
                             default=0.00982,
                             unit='LENGTH')
    washer_depth: FloatProperty(name="Washer depth",
                             description="Thickness of washer",
                             min=0.0005,
                             default=0.00095,
                             unit='LENGTH')
    slot_length: FloatProperty(name="Slot length",
                             description="Length of the screw slot",
                             min=0.010,
                             default=0.010,
                             unit='LENGTH')

registration_list = (SupportProperties,)
support_props_list = ("thickness", "support_dim_X", "extension", "separation",
                      "flange_extension", "flange_dim_Z",
                      "screw_diam", "screw_length", "nut_diam",
                      "washer_diam", "washer_depth", "slot_length")
