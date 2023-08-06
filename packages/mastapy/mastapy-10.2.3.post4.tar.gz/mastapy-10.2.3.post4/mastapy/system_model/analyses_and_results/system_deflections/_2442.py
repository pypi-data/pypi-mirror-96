﻿'''_2442.py

SpiralBevelGearSystemDeflection
'''


from mastapy.system_model.part_model.gears import _2189
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6550
from mastapy.system_model.analyses_and_results.power_flows import _3766
from mastapy.gears.rating.spiral_bevel import _363
from mastapy.system_model.analyses_and_results.system_deflections import _2343
from mastapy._internal.python_net import python_net_import

_SPIRAL_BEVEL_GEAR_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections', 'SpiralBevelGearSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('SpiralBevelGearSystemDeflection',)


class SpiralBevelGearSystemDeflection(_2343.BevelGearSystemDeflection):
    '''SpiralBevelGearSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _SPIRAL_BEVEL_GEAR_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SpiralBevelGearSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2189.SpiralBevelGear':
        '''SpiralBevelGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2189.SpiralBevelGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign else None

    @property
    def component_load_case(self) -> '_6550.SpiralBevelGearLoadCase':
        '''SpiralBevelGearLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6550.SpiralBevelGearLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase else None

    @property
    def power_flow_results(self) -> '_3766.SpiralBevelGearPowerFlow':
        '''SpiralBevelGearPowerFlow: 'PowerFlowResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_3766.SpiralBevelGearPowerFlow)(self.wrapped.PowerFlowResults) if self.wrapped.PowerFlowResults else None

    @property
    def component_detailed_analysis(self) -> '_363.SpiralBevelGearRating':
        '''SpiralBevelGearRating: 'ComponentDetailedAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_363.SpiralBevelGearRating)(self.wrapped.ComponentDetailedAnalysis) if self.wrapped.ComponentDetailedAnalysis else None
