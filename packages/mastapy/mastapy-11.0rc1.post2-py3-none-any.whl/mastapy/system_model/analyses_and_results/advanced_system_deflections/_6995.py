﻿'''_6995.py

RingPinsAdvancedSystemDeflection
'''


from typing import List

from mastapy.system_model.part_model.cycloidal import _2241
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6572
from mastapy.system_model.analyses_and_results.system_deflections import _2456
from mastapy.system_model.analyses_and_results.advanced_system_deflections import _6983
from mastapy._internal.python_net import python_net_import

_RING_PINS_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections', 'RingPinsAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('RingPinsAdvancedSystemDeflection',)


class RingPinsAdvancedSystemDeflection(_6983.MountableComponentAdvancedSystemDeflection):
    '''RingPinsAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _RING_PINS_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RingPinsAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2241.RingPins':
        '''RingPins: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2241.RingPins)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign else None

    @property
    def component_load_case(self) -> '_6572.RingPinsLoadCase':
        '''RingPinsLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6572.RingPinsLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase else None

    @property
    def component_system_deflection_results(self) -> 'List[_2456.RingPinsSystemDeflection]':
        '''List[RingPinsSystemDeflection]: 'ComponentSystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentSystemDeflectionResults, constructor.new(_2456.RingPinsSystemDeflection))
        return value
