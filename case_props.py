# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 DTRabbit

import bpy
from bpy.types import PropertyGroup
from bpy.props import (CollectionProperty,
                       IntProperty,
                       FloatProperty,
                       BoolProperty,
                       FloatVectorProperty)

from .utils import calc_case
from .instrument_list import InstrumentListItem
from .support_list import SupportListItem

class CaseProperties(PropertyGroup):

    # instrument list
    instrument_list: CollectionProperty(name="Instrument List",
                        type=InstrumentListItem)
    instrument_list_index: IntProperty(name="Instrument List index", default=-1)

    # support list
    support_list: CollectionProperty(name="Support List",
                        type=SupportListItem)
    support_list_index: IntProperty(name="Support List index", default=-1)

    # case
    clearance: FloatProperty(name="Clearance",
                             description="Internal clearance",
                             default=0.01,
                             min=0.01,
                             max=0.05,
                             unit='LENGTH',
                             update = calc_case)

    # calculated properties
    size: FloatVectorProperty(name="",
                              size=3,
                              unit='LENGTH')
    location: FloatVectorProperty(name="",
                                  size=3,
                                  unit='LENGTH')
    base_Z: FloatProperty(name="",
                          default = 0,
                          unit='LENGTH')
    lid_Z: FloatProperty(name="",
                         default = 0,
                         unit='LENGTH')

registration_list = (CaseProperties,)
