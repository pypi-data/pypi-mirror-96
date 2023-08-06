﻿'''_3798.py

SpringDamperHalfPowerFlow
'''


from mastapy.system_model.part_model.couplings import _2272
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6587
from mastapy.system_model.analyses_and_results.power_flows import _3730
from mastapy._internal.python_net import python_net_import

_SPRING_DAMPER_HALF_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows', 'SpringDamperHalfPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('SpringDamperHalfPowerFlow',)


class SpringDamperHalfPowerFlow(_3730.CouplingHalfPowerFlow):
    '''SpringDamperHalfPowerFlow

    This is a mastapy class.
    '''

    TYPE = _SPRING_DAMPER_HALF_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SpringDamperHalfPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2272.SpringDamperHalf':
        '''SpringDamperHalf: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2272.SpringDamperHalf)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign else None

    @property
    def component_load_case(self) -> '_6587.SpringDamperHalfLoadCase':
        '''SpringDamperHalfLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6587.SpringDamperHalfLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase else None
