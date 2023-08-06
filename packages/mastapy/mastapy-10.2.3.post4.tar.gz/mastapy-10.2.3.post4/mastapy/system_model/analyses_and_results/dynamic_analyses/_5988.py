﻿'''_5988.py

StraightBevelGearDynamicAnalysis
'''


from mastapy.system_model.part_model.gears import _2193
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6560
from mastapy.system_model.analyses_and_results.dynamic_analyses import _5895
from mastapy._internal.python_net import python_net_import

_STRAIGHT_BEVEL_GEAR_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses', 'StraightBevelGearDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('StraightBevelGearDynamicAnalysis',)


class StraightBevelGearDynamicAnalysis(_5895.BevelGearDynamicAnalysis):
    '''StraightBevelGearDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _STRAIGHT_BEVEL_GEAR_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StraightBevelGearDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2193.StraightBevelGear':
        '''StraightBevelGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2193.StraightBevelGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign else None

    @property
    def component_load_case(self) -> '_6560.StraightBevelGearLoadCase':
        '''StraightBevelGearLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6560.StraightBevelGearLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase else None
