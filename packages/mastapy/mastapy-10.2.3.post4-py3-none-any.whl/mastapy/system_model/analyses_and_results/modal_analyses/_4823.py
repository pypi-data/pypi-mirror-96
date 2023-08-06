﻿'''_4823.py

HypoidGearModalAnalysis
'''


from mastapy.system_model.part_model.gears import _2132
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6203
from mastapy.system_model.analyses_and_results.system_deflections import _2335
from mastapy.system_model.analyses_and_results.modal_analyses import _4768
from mastapy._internal.python_net import python_net_import

_HYPOID_GEAR_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses', 'HypoidGearModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('HypoidGearModalAnalysis',)


class HypoidGearModalAnalysis(_4768.AGMAGleasonConicalGearModalAnalysis):
    '''HypoidGearModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _HYPOID_GEAR_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HypoidGearModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2132.HypoidGear':
        '''HypoidGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2132.HypoidGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign else None

    @property
    def component_load_case(self) -> '_6203.HypoidGearLoadCase':
        '''HypoidGearLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6203.HypoidGearLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase else None

    @property
    def system_deflection_results(self) -> '_2335.HypoidGearSystemDeflection':
        '''HypoidGearSystemDeflection: 'SystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2335.HypoidGearSystemDeflection)(self.wrapped.SystemDeflectionResults) if self.wrapped.SystemDeflectionResults else None
