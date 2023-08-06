﻿'''_2437.py

ShaftSystemDeflection
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.scripting import _7157
from mastapy.system_model.part_model.shaft_model import _2129
from mastapy.system_model.analyses_and_results.static_loads import _6546
from mastapy.system_model.analyses_and_results.power_flows import _3762
from mastapy.system_model.analyses_and_results.system_deflections import _2435, _2436, _2327
from mastapy.shafts import _19
from mastapy.math_utility.measured_vectors import _1560
from mastapy._internal.python_net import python_net_import

_SHAFT_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections', 'ShaftSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftSystemDeflection',)


class ShaftSystemDeflection(_2327.AbstractShaftSystemDeflection):
    '''ShaftSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _SHAFT_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def number_of_cycles_for_fatigue(self) -> 'float':
        '''float: 'NumberOfCyclesForFatigue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfCyclesForFatigue

    @property
    def pin_tangential_oscillation_amplitude(self) -> 'float':
        '''float: 'PinTangentialOscillationAmplitude' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinTangentialOscillationAmplitude

    @property
    def two_d_drawing_showing_axial_forces_with_mounted_components(self) -> '_7157.SMTBitmap':
        '''SMTBitmap: 'TwoDDrawingShowingAxialForcesWithMountedComponents' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_7157.SMTBitmap)(self.wrapped.TwoDDrawingShowingAxialForcesWithMountedComponents) if self.wrapped.TwoDDrawingShowingAxialForcesWithMountedComponents else None

    @property
    def component_design(self) -> '_2129.Shaft':
        '''Shaft: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2129.Shaft)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign else None

    @property
    def component_load_case(self) -> '_6546.ShaftLoadCase':
        '''ShaftLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6546.ShaftLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase else None

    @property
    def power_flow_results(self) -> '_3762.ShaftPowerFlow':
        '''ShaftPowerFlow: 'PowerFlowResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_3762.ShaftPowerFlow)(self.wrapped.PowerFlowResults) if self.wrapped.PowerFlowResults else None

    @property
    def shaft_section_end_with_worst_static_safety_factor(self) -> '_2435.ShaftSectionEndResultsSystemDeflection':
        '''ShaftSectionEndResultsSystemDeflection: 'ShaftSectionEndWithWorstStaticSafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2435.ShaftSectionEndResultsSystemDeflection)(self.wrapped.ShaftSectionEndWithWorstStaticSafetyFactor) if self.wrapped.ShaftSectionEndWithWorstStaticSafetyFactor else None

    @property
    def shaft_section_end_with_worst_fatigue_safety_factor(self) -> '_2435.ShaftSectionEndResultsSystemDeflection':
        '''ShaftSectionEndResultsSystemDeflection: 'ShaftSectionEndWithWorstFatigueSafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2435.ShaftSectionEndResultsSystemDeflection)(self.wrapped.ShaftSectionEndWithWorstFatigueSafetyFactor) if self.wrapped.ShaftSectionEndWithWorstFatigueSafetyFactor else None

    @property
    def shaft_section_end_with_worst_fatigue_safety_factor_for_infinite_life(self) -> '_2435.ShaftSectionEndResultsSystemDeflection':
        '''ShaftSectionEndResultsSystemDeflection: 'ShaftSectionEndWithWorstFatigueSafetyFactorForInfiniteLife' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2435.ShaftSectionEndResultsSystemDeflection)(self.wrapped.ShaftSectionEndWithWorstFatigueSafetyFactorForInfiniteLife) if self.wrapped.ShaftSectionEndWithWorstFatigueSafetyFactorForInfiniteLife else None

    @property
    def component_detailed_analysis(self) -> '_19.ShaftDamageResults':
        '''ShaftDamageResults: 'ComponentDetailedAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_19.ShaftDamageResults)(self.wrapped.ComponentDetailedAnalysis) if self.wrapped.ComponentDetailedAnalysis else None

    @property
    def planetaries(self) -> 'List[ShaftSystemDeflection]':
        '''List[ShaftSystemDeflection]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(ShaftSystemDeflection))
        return value

    @property
    def shaft_section_results(self) -> 'List[_2436.ShaftSectionSystemDeflection]':
        '''List[ShaftSectionSystemDeflection]: 'ShaftSectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ShaftSectionResults, constructor.new(_2436.ShaftSectionSystemDeflection))
        return value

    @property
    def shaft_section_end_results_by_offset_with_worst_safety_factor(self) -> 'List[_2435.ShaftSectionEndResultsSystemDeflection]':
        '''List[ShaftSectionEndResultsSystemDeflection]: 'ShaftSectionEndResultsByOffsetWithWorstSafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ShaftSectionEndResultsByOffsetWithWorstSafetyFactor, constructor.new(_2435.ShaftSectionEndResultsSystemDeflection))
        return value

    @property
    def mounted_components_applying_torque(self) -> 'List[_1560.ForceResults]':
        '''List[ForceResults]: 'MountedComponentsApplyingTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.MountedComponentsApplyingTorque, constructor.new(_1560.ForceResults))
        return value

    def calculate_outer_diameter_to_achieve_fatigue_safety_factor_requirement(self):
        ''' 'CalculateOuterDiameterToAchieveFatigueSafetyFactorRequirement' is the original name of this method.'''

        self.wrapped.CalculateOuterDiameterToAchieveFatigueSafetyFactorRequirement()
