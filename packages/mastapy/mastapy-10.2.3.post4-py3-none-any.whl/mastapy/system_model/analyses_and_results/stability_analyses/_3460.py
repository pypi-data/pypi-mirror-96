﻿'''_3460.py

HypoidGearSetStabilityAnalysis
'''


from typing import List

from mastapy.system_model.part_model.gears import _2181
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6504
from mastapy.system_model.analyses_and_results.stability_analyses import _3461, _3459, _3401
from mastapy._internal.python_net import python_net_import

_HYPOID_GEAR_SET_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses', 'HypoidGearSetStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('HypoidGearSetStabilityAnalysis',)


class HypoidGearSetStabilityAnalysis(_3401.AGMAGleasonConicalGearSetStabilityAnalysis):
    '''HypoidGearSetStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _HYPOID_GEAR_SET_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HypoidGearSetStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2181.HypoidGearSet':
        '''HypoidGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2181.HypoidGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign else None

    @property
    def assembly_load_case(self) -> '_6504.HypoidGearSetLoadCase':
        '''HypoidGearSetLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6504.HypoidGearSetLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase else None

    @property
    def hypoid_gears_stability_analysis(self) -> 'List[_3461.HypoidGearStabilityAnalysis]':
        '''List[HypoidGearStabilityAnalysis]: 'HypoidGearsStabilityAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidGearsStabilityAnalysis, constructor.new(_3461.HypoidGearStabilityAnalysis))
        return value

    @property
    def hypoid_meshes_stability_analysis(self) -> 'List[_3459.HypoidGearMeshStabilityAnalysis]':
        '''List[HypoidGearMeshStabilityAnalysis]: 'HypoidMeshesStabilityAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.HypoidMeshesStabilityAnalysis, constructor.new(_3459.HypoidGearMeshStabilityAnalysis))
        return value
